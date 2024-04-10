from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion

from execution_engine.AstExecutionEngine import AstExecutionEngine
from planner.jinja2_planner import Jinja2Planner
import semantic_kernel as sk

from plugins.EmailPlugin.native_functions import EmailPlugin
from plugins.ExcelPlugin.native_functions import ExcelPlugin
from plugins.JsonPlugin.native_functions import JsonPlugin

kernel = sk.Kernel()

# Prepare OpenAI service using credentials stored in the `.env` file
api_key, org_id = sk.openai_settings_from_dot_env()
service_id = "gpt-4-0125-preview"
kernel.add_service(
    OpenAIChatCompletion(
        service_id=service_id,
        ai_model_id="gpt-4-0125-preview",
        api_key=api_key,
        org_id=org_id
    )
)

kernel.import_plugin_from_object(EmailPlugin(), "EmailPlugin")
kernel.import_plugin_from_object(ExcelPlugin(), "ExcelPlugin")
kernel.import_plugin_from_object(JsonPlugin(), "JsonPlugin")

planner = Jinja2Planner(kernel=kernel, service_id=service_id)

goal = "The Excel file has a column email sent to mark we have sent an email to the person or not. Yes means we've sent an email to the person. Otherwise no or no value. Send an email to all the people we have sent the email yet. Names and email addresses are also in the Excel."
sop = '''1. Load the file from the user-specified location. The file has but not limited to these columns Name, email address, location, titok handle, email sent, other note.
2. Based on the criteria the user provides, select the ones, send an email to each of them and mark the email sent as Yes for that person.
3. Print the updated result to the console.'''
ast, chat_history = planner.create_plan(goal=goal, sop=sop)

engine = AstExecutionEngine(plan=ast, context={}, semantic_kernel=kernel, service_id=service_id,
                            chat_history=chat_history)
engine.execute()
