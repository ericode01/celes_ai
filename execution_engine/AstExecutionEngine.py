import asyncio
import json
import re
import traceback
from json import JSONDecodeError
from typing import Any

from semantic_kernel import Kernel, PromptTemplateConfig
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_function_from_prompt import KernelFunctionFromPrompt
from semantic_kernel.prompt_template import InputVariable

from jinja2_ast import nodes, Environment
from collections import deque

from jinja2_ast.nodes import Node


class AstExecutionEngine:
    def __init__(self, plan: nodes.Template, context: dict, semantic_kernel: Kernel, service_id: str,
                 chat_history: ChatHistory):
        self.template = plan
        self.context = context
        self.kernel = semantic_kernel
        self.service_id = service_id
        self.chat_history = chat_history
        self.full_chat_history = chat_history
        self.execution_error_mitigation_chat_function = None
        self.updated_node_map = {}
        self.jinja2_env = Environment()
        self.execution_stack = deque()

    def execute(self):
        # Add template first level nodes to execution stack
        self.execution_stack.extend(self.template.body)
        self.execution_stack.reverse()

        while len(self.execution_stack) != 0:
            cur_node = self.execution_stack.pop()

            if cur_node in self.updated_node_map:
                replacing_template = self.updated_node_map[cur_node]
                for idx in range(len(replacing_template.body) - 1, -1, -1):
                    self.execution_stack.append(replacing_template.body[idx])
                continue

            try:
                cur_node.eval(context=self.context, execution_stack=self.execution_stack, kernel=self.kernel)
            except Exception as ex:
                error_message = str(ex)

                # Accessing the inner (original) exception message
                # Check if there's a direct cause using `__cause__`
                if ex.__cause__:
                    error_message = error_message + ": " + str(ex.__cause__)

                if not self.mitigate_execution_error(cur_node=cur_node, error_message=error_message):
                    return

    def mitigate_execution_error(self, cur_node: Node, error_message: str, ):
        if not self.execution_error_mitigation_chat_function:
            self.initialize_execution_error_mitigation_chat_function()

        user_input = self.get_execution_error_mitigation_prompt(cur_node=cur_node, error_message=error_message)
        answer = asyncio.run(
            self.execution_error_mitigation_chat_function.invoke(self.kernel, user_input=user_input,
                                                                 chat_history=self.chat_history))

        print(answer)
        self.full_chat_history.add_user_message(user_input)
        self.full_chat_history.add_assistant_message(str(answer))

        try:
            answer_json = json.loads(str(answer))
        except JSONDecodeError as e:
            print(e)
            return False

        # new_code_snippet = self.search_msg_for_code_snippet(str(answer))

        if answer_json["issue_type"] == "syntax" or answer_json["issue_type"] == "logic":
            new_code_snippet = answer_json["replacing_code_snippet"]
            message_to_user = answer_json["message_to_user"]
            print(
                f"System:> {message_to_user}")
            print(
                f"System:> AI suggests replacing the problematic code with the following new code snippet: {new_code_snippet}")
            print("System:> Accept or not: Y/N")
            user_input = input("User:> ")
            if user_input == "Y":
                temp_ast = self.jinja2_env.parse(new_code_snippet)
                self.updated_node_map[cur_node] = temp_ast
                self.execution_stack.append(cur_node)
                print("System:> Modified plan.")
                return True
            else:
                return False

        if answer_json["issue_type"] == "data":
            message_to_user = answer_json["message_to_user"]
            print(
                f"System:> {message_to_user}")
            print(
                "System:> Please provide variable values.")
            user_input = input("User:> ")
            kw_pairs = user_input.split(",")
            for kw in kw_pairs:
                kw_list = kw.split(":")
                self.context[kw_list[0].strip()] = kw_list[1].strip()

            self.execution_stack.append(cur_node)
            print("System:> updated context. Retry.")
            return True

        # if new_code_snippet:
        #     print(
        #         f"System:> AI suggests replacing the problematic code with the following new code snippet: {new_code_snippet}")
        #     print("System:> Accept or not: Y/N")
        #     user_input = input("User:> ")
        #     if user_input == "Y":
        #         temp_ast = self.jinja2_env.parse(new_code_snippet)
        #         self.updated_node_map[cur_node] = temp_ast
        #         self.execution_stack.append(cur_node)
        #         print("System:> Modified plan.")
        #         return True
        #
        #     if user_input == "N":
        #         print(
        #             "System:> Please suggest a change to the plan for the current snippet or provide variable values.")
        #         user_input = input("User:> ")
        #         kw_pairs = user_input.split(",")
        #         for kw in kw_pairs:
        #             kw_list = kw.split(":")
        #             self.context[kw_list[0].strip()] = kw_list[1].strip()
        #
        #         self.execution_stack.append(cur_node)
        #         print("System:> updated context. Retry.")
        #         return True
        # else:
        #     print(
        #         f"System:> AI suggests this way to mitigate the error: {answer}")
        #     print("System:> Proceed without change? Y/N")
        #     user_input = input("User:> ")
        #     if user_input == "Y":
        #         return True
        #     if user_input == "N":
        #         return False

    def search_msg_for_code_snippet(self, msg: str):
        # Regex breakdown:
        # (```\s*Jinja2){1}\s*: Opening backticks, starting boundary for Jinja2 template
        # ((([^`]|`(?!``))+): Any non-backtick character or one backtick character not followed by 2 more consecutive backticks
        # (\s*```){1}: Closing backticks, closing boundary for Jinja2 template
        regex = "(```\s*Jinja2){1}\s*(([^`]|`(?!``))+)(\s*```){1}"

        m = re.search(regex, msg)
        if m:
            return m.group(2)
        return None

    def initialize_execution_error_mitigation_chat_function(self):
        prompt = '''{{$chat_history}}
{{$user_input}}
'''
        settings = self.kernel.get_prompt_execution_settings_from_service_id(self.service_id)
        settings.max_tokens = 2000
        settings.temperature = 0.1
        settings.top_p = 0.1

        prompt_template_config = PromptTemplateConfig(
            template=prompt,
            name="mitigate_execution_error",
            template_format="semantic-kernel",
            input_variables=[
                InputVariable(
                    name="user_input",
                    description="The user input",
                    is_required=True,
                    default="",
                ),
                InputVariable(
                    name="chat_history",
                    description="The history of the conversation",
                    is_required=True,
                )
            ],
            execution_settings=settings,
        )

        execution_error_mitigation_chat_function = KernelFunctionFromPrompt(
            function_name="execution_error_mitigation_chat_function",
            plugin_name="runtime_plugin",
            description="Try to resolve a runtime error with the help with AI.",
            template_format="semantic-kernel",
            prompt_template_config=prompt_template_config,
        )

        self.execution_error_mitigation_chat_function = execution_error_mitigation_chat_function

    def get_execution_error_mitigation_prompt(self, cur_node: Node, error_message: str):
        prompt = f'''Encountered execution error when executing
```
{cur_node.to_string()}
```
Error message: 
{error_message}

Following are three possible types of root cause to an execution error and the ways to fix them.
1. syntax issue including incorrect function name, incorrect function argument, incorrect variable assignment and so on.
Try to fix the issue by modifying the problematic code snippet shown above and generate a new code snippet in Jinja2 to replace the problematic snippet. Be aware if the code snippet is within a loop, the modification will affect future iterations. Add if-else condition if needed. Only generate the new code snippet for replacing. Don't generate other parts.
2. data issue including missing/incorrect data in the input, missing/incorrect data needed for a function call, unexpected data returned from a function call, and so on. If there's a undefined variable, it's a data issue and the issue_type to return is data.
Try to fix the issue by asking the user to provide the values of the missing or unexpected data.
3. code logic issue including missing steps in the code, missing validation checks, incorrect logic between steps and so on.
Try to fix the issue by modifying the problematic code snippet shown above and generate a new code snippet in Jinja2 to replace the problematic snippet. Be aware if the code snippet is within a loop, the modification will affect future iterations. Add if-else condition if needed. Only generate the new code snippet for replacing. Don't generate other parts.

First, categorize the error to be one of the three types listed above.
Second, follow the instruction of the certain type to fix the issue.
Their, generate a human-friendly message to explain the issue and your solution to the user.
Your output must be in JSON format as below and nothing else:
{{
"issue_type": "syntax" or "data" or "logic",
"message_to_user": "a human-friendly message to explain the issue and your solution to the user"
"replacing_code_snippet": "a Jinja2 code snippet" for syntax and logic issue or "" for data issue,
}}

Follow these rules:
- Try to fix this issue with the knowledge you have and the instructions you were given.
- Don't hallucinate anything that is not provided.
- If the error is not within the three types or you cannot fix the issue yourself, ask for help from the user. A user can help you by providing missing data, suggesting code changes, and so on.'''

        return prompt
