import asyncio
import re

from semantic_kernel import Kernel, PromptTemplateConfig
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.exceptions import PlannerInvalidGoalError
from semantic_kernel.functions.kernel_function_from_prompt import KernelFunctionFromPrompt
from semantic_kernel.prompt_template import InputVariable

from jinja2_ast import Environment
from planner.jinja2_planner_utils import Jinja2PlannerUtils


class Jinja2Planner:
    def __init__(
            self,
            kernel: Kernel,
            service_id: str
    ):
        self.kernel = kernel
        self.service_id = service_id
        self.jinja2_plan_creation_chat_function = None

    def create_plan(self, goal: str, sop: str):
        if not goal or len(goal) == 0:
            raise PlannerInvalidGoalError("[create_plan] The goal specified is empty")

        if not self.jinja2_plan_creation_chat_function:
            self.initialize_create_plan_chat_function()

        chat_history = self.create_chat_history()
        user_input = self.create_user_input(goal=goal, sop=sop)
        answer = asyncio.run(
            self.jinja2_plan_creation_chat_function.invoke(self.kernel, user_input=user_input,
                                                           chat_history=chat_history))

#         answer = '''```Jinja2
# # {# Step 0: Extract Key Values #}
# # {% set file_path = "user_specified_file_path.xlsx" %}
# #
# # {# Step 1: Load the Excel file to JSON list #}
# # {% set json_data = ExcelPlugin___ExcelFileToJsonList(file_path) %}
# #
# # {# Step 2: Filter the JSON data for people who haven't been sent an email yet #}
# # {% set recipients_to_email = JsonPlugin___QueryJsonData(json_data, "email sent != 'Yes'") %}
# #
# # {# Step 3: Loop through each recipient and send an email #}
# # {% for recipient in recipients_to_email %}
# #     {# Send an email to the recipient #}
# #     {% set email_result = EmailPlugin___SendAnEmail(recipient['Name'], recipient['email address']) %}
# #
# #     {# Mark the email as sent in the JSON data #}
# #     {% set update_result = JsonPlugin___UpsertObjectKeyValueWithConditionInList(json_data, ('email address', recipient['email address']), ('email sent', 'Yes')) %}
# # {% endfor %}
# #
# # {# Step 4: Print the updated JSON data to the console #}
# # {{ JsonPlugin___PrintJson(json_data) }}
# # ```'''

        print(answer)

        code_snippet = self.search_msg_for_code_snippet(str(answer))

        if not code_snippet:
            print("Cannot find code snippet from the plan./n" + answer)
            return

        chat_history.add_user_message(user_input)
        chat_history.add_assistant_message(f'''```Jinja2
{code_snippet}```''')
        env = Environment()
        ast = env.parse(code_snippet)

        return ast, chat_history

    def search_msg_for_code_snippet(self, msg: str):
        # Regex breakdown:
        # (```\s*([J|j]inja2)?){1}\s*: Opening backticks, starting boundary for Jinja2 template. "Jinja2" or "jinja2" is optional.
        # ((([^`]|`(?!``))+): Any non-backtick character or one backtick character not followed by 2 more consecutive backticks
        # (\s*```){1}: Closing backticks, closing boundary for Jinja2 template
        regex = "(```\s*([J|j]inja2)?){1}\s*(([^`]|`(?!``))+)(\s*```){1}"

        m = re.search(regex, msg)
        if m:
            return m.group(3)
        return None

    def create_user_input(self, goal: str, sop: str):
        prompt = f'''Goal
{goal}
        '''
        if sop:
            prompt = prompt + f'''
Standard Operating Procedure
{sop}
'''
        return prompt

    def create_chat_history(self):
        chat_history = ChatHistory()

        chat_history.add_system_message('''Instructions
Explain how to achieve the user's goal using the available functions with a Jinja2 Python template.
If a Standard Operating Procedure is provided, follow the Standard Operating Procedure.

Example
If the user posed the goal below, you could answer with the following template.''')
        chat_history.add_user_message('''Goal
I want you to generate 10 random numbers and send them to another function.''')
        chat_history.add_assistant_message('''Here's a Jinja2 template that achieves the goal:
```Jinja2
{# Step 0: Extract key values #}
{% set count = 10 %}

{# Step 1: Loop using the count #}
{% for seed in range(start = 0, stop = count, step = 1) %}

    {# Step 2: Create random number #}
    {% set random_number = Example___Random(seed = seed) %}

    {# Step 3: Call example ProcessNumber function with random number #}
    {% set result = Example___ProcessNumber(random_number = random_number) %}
    
    {# Step 4: Call output_json function to output result #}
    {{ JsonPlugin___PrintJson(json_data = result) }}
{% endfor %}
```''')
        chat_history.add_system_message('''Now let's try the real thing.''')

        # TODO: add complete type details
        user_msg_available_functions_prompt = '''The following functions are available to you:
## Supported variable assignment
- `{% set %}`

## Supported if-else control structures
- `{% if %}{% endif %}`
- `{% if %}{% else %}{% endif %}`
- `{% if %}{% elif %}{% else %}{% endif %}`

## Supported loop control structures
- `{% for item in iterable %}`

## Supported logic operators
- `and`
- `or`
- `not`

## Supported comparison operators
- `==`
- `!=`
- `<`
- `<=`
- `>`
- `>=`
- `in`
- `not in`

## Supported string operators
- `~` - Concatenates strings 

##Syntax to call a function
Always pass arguments with the key = value syntax.
- `{% set result = function_name(param1 = arg1, param2 = arg2, ....) %}` - for a function having one return value.
- `{% set (result1, result2, ...) = function_name(param1 = arg1, param2 = arg2, ....) %}` - for a function having multiple return values.
- `{{ function_name(param1 = arg1, param2 = arg2, ....) }}` - for a function having no return value or doesn't need to save the return value to a variable.

## helper functions
- `range(start, stop, step)` - Returns a sequence of numbers, starting from the start, and increments by the step, and stops right before the stop(exclusive).

## Custom functions
Lastly, you have the following custom functions to use.

{available_functions_manual}

IMPORTANT: You can only use the functions that are listed above. Do not use any other functions that are not explicitly listed here. For example, do not use `log()` or any `Example` functions, as they are not supported.'''
        available_functions_manual = Jinja2PlannerUtils.get_available_function_manual(self.kernel)
        user_msg_available_functions_prompt = user_msg_available_functions_prompt.replace(
            "{available_functions_manual}", available_functions_manual)
        chat_history.add_user_message(user_msg_available_functions_prompt)

        chat_history.add_system_message('''## Tips and reminders
- Add a comment above each step to describe what the step does.
- Each variable should have a well-defined name.
- All variables are global. Make sure to use unique variable names.
- Be extremely careful about types. For example, if you pass an array to a function that expects a number, the template will error out.
- Each step should contain only one function call.
- No HTML tag allowed.

## Start
Follow these steps to create one Jinja2 template to achieve the goal:
0. Extract Key Values:
  - Read the goal and any user-provided content carefully and identify any relevant strings, numbers, or conditions that you'll need. Do not modify any data.
  - Read and understand the Standard Operating Procedure if provided and follow the Standard Operating Procedure closely.
  - When generating variables or function inputs, only use content that the user has explicitly provided or confirmed. If the user did not explicitly provide specific information, you should not invent or assume this information.
  - Use the `{% set %}` statement to create a variable for each key value.
  - Omit this step if no values are needed from the initial context.
1. Choose the Right functions:
  - Use the provided functions to manipulate the variables you've created. Start with the basic functions and only use custom functions if necessary to accomplish the goal.
  - Be careful with syntax, i.e., Always reference a custom function by its full name.
2. Don't Create or Assume Unlisted functions:
  - Only use the functions provided. Any function not listed is considered hallucinated and must not be used.
  - Do not invent or assume the existence of any functions not explicitly defined above.
3. What if I Need More functions?
  - Stop here if the goal cannot be fully achieved with the provided functions or you need a function not defined, and just return a string with an appropriate error message.
4. Keep It Simple:
  - Avoid using loops or block expressions. They are allowed but not always necessary, so try to find a solution that does not use them.
  - Your template should be intelligent and efficient, avoiding unnecessary complexity or redundant steps.
5. No Nested functions:
  - Do not nest functions or conditionals inside other functions. This can cause errors in the template.
6. Output the Result:
  - Once you have completed the necessary steps to reach the goal, if it's necessary to print your result, use the `output_json(value)` function.
  - Ensure your template and all steps are enclosed in a ``` Jinja2 block.

Remember, the objective is not to use all the functions available, but to use the correct ones to achieve the desired outcome with a clear and concise template.''')

        return chat_history

    def initialize_create_plan_chat_function(self):
        prompt = '''{{$chat_history}}
{{$user_input}}
'''
        settings = self.kernel.get_prompt_execution_settings_from_service_id(self.service_id)
        settings.max_tokens = 4096
        settings.temperature = 0.1
        settings.top_p = 1

        prompt_template_config = PromptTemplateConfig(
            template=prompt,
            name="create_jinja2_plan",
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

        jinja2_plan_creation_chat_function = KernelFunctionFromPrompt(
            function_name="jinja2_plan_creation_chat_function",
            plugin_name="jinja2_planner_plugin",
            description="Create a Jinja2 plan.",
            template_format="semantic-kernel",
            prompt_template_config=prompt_template_config,
        )

        self.jinja2_plan_creation_chat_function = jinja2_plan_creation_chat_function
