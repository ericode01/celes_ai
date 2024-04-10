from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory

from execution_engine.AstExecutionEngine import AstExecutionEngine
from jinja2_ast import Template, Environment
import json
import semantic_kernel as sk


def output_json(obj):
    print(json.dumps(obj))


def CourseraPlugin_search(query):
    return {
        'hits': [
            {
                'name': 'course1',
                'entityType': 'type1'
            },
            {
                'name': 'course2',
                'entityType': 'type2'
            }
        ]
    }


# Initialize the Jinja2 environment
# env = Environment()

# Create the template (in a real application, you'd likely load this from a file)
template_string = """
{# Step 1: Call the CourseraPlugin_search function with the query for "Artificial Intelligence" courses #}
{% set courseraResults = CourseraPlugin_search("Artificial Intelligence") %}

{# Step 2: Extract and structure the relevant course information (name and type) from the search results #}
{% set coursesInfo = [] %}
{% for course in courseraResults.hits %}
    {% set courseDetails = {"name": course.name, "type": course.entityType} %}
    {% if courseDetails not in coursesInfo %}
        {% set _ = coursesInfo.append(courseDetails) %}
    {% endif %}
{% endfor %}

{# Step 3: Output the structured information as JSON #}
{{ output_json(coursesInfo) }}
"""  # Replace with the template string from Step 2

# Create and render the template
env = Environment()
ast = env.parse(template_string)
# print(ast.to_string())

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

chat_history = ChatHistory()
chat_history.add_system_message('''Instructions
Explain how to achieve the user's goal using the available functions with a Jinja2 Python template.

Example
If the user posed the goal below, you could answer with the following template.''')
chat_history.add_user_message('''Goal
I want you to generate 10 random numbers and send them to another function.''')
chat_history.add_assistant_message('''Here's a Jinja2 template that achieves the goal:
```Jinja2
{# Step 0: Extract key values #}
{% set count = 10 %}

{# Step 1: Loop using the count #}
{% for seed in range(0, count, 1) %}

  {# Step 2: Create random number #}
  {% set randomNumber = Example-Random(seed) %}

  {# Step 3: Call example ProcessNumber function with random number #}
  {% set result = Example-ProcessNumber(randomNumber) %}

  {# Step 4: Call output_json function to output result #}
  {{ output_json(result) }}
```''')
chat_history.add_system_message('''Now let's try the real thing.''')
chat_history.add_user_message('''The following functions are available to you:

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
- `{% set result = function_name(arg1, arg2, ....) %}` - for a function having one return value.
- `{% set result1, result2, ... = function_name(arg1, arg2, ....) %}` - for a function having multiple return values.
- `{{ function_name(arg1, arg2, ....) }}` - for a function having no return value or doesn't need to save the return value to a variable.

## helper functions
- `output_json(value)` - Serializes the given value and prints result as JSON string. No return value.
- `range(start, stop, step)` - Returns a sequence of numbers, starting from the start, and increments by the step, and stops right before the stop(exclusive).

## Complex types
Some functions require arguments that are complex objects. The JSON schemas for these complex objects are defined below:

### searchReturns-object:
{
  "properties": {
    "hits": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string"
          },
          "partners": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "duration": {
            "type": "string"
          },
          "partnerLogos": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "productDifficultyLevel": {
            "type": "string"
          },
          "entityType": {
            "type": "string"
          },
          "avgProductRating": {
            "type": "string"
          },
          "skills": {
            "type": "string"
          },
          "imageUrl": {
            "type": "string"
          },
          "isCourseFree": {
            "type": "string"
          },
          "isPartOfCourseraPlus": {
            "type": "string"
          },
          "objectUrl": {
            "type": "string"
          }
        }
      }
    }
  }
}

## Custom functions
Lastly, you have the following custom functions to use.

### `CourseraPlugin_search`
Description: A public API that searches the Coursera catalog for products (e.g. courses) that are relevant to the provided query string.
Inputs:
    - query: query-string - query (required)
Output: searchReturns-object
     - OK

IMPORTANT: You can only use the functions that are listed above. Do not use any other functions that are not explicitly listed here. For example, do not use `log()` or any `Example` functions, as they are not supported.''')
chat_history.add_user_message('''Goal
Show me courses, their and type only, about Artificial Intelligence from Coursera.''')
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
chat_history.add_assistant_message('''```Jinja2
{# Step 1: Search Coursera for courses about Artificial Intelligence #}
{% set courses = CourseraPlugin_search("Artificial Intelligence") %}

{# Step 2: Extract and format the relevant information from the search results #}
{% set formattedCourses = [] %}
{% for course in courses.hits %}
  {% set courseInfo = {
    "name": course.name,
    "type": course.entity,
    "year": course.year
  } %}
  {% if courseInfo not in formattedCourses %}
    {% set _ = formattedCourses.append(courseInfo) %}
  {% endif %}
{% endfor %}

{# Step 3: Output the formatted list of courses #}
{{ output_json(formattedCourses) }}```''')

context = {
    'output_json': output_json,
    'CourseraPlugin_search': CourseraPlugin_search,
}
engine = AstExecutionEngine(plan=ast, context=context, semantic_kernel=kernel, service_id=service_id,
                            chat_history=chat_history)

engine.execute()

# engine.execute(template=ast, context=context)
