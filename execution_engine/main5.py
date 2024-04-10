from execution_engine.AstExecutionEngine import AstExecutionEngine
from jinja2_ast import Template, Environment
import json


def categorize_book(year):
    """Categorizes a book as 'Classic' or 'Modern' based on its publication year."""
    return ("Classic", 10) if year < 2000 else ("Modern", 20)


def format_title(title):
    """Formats the book title to be title case."""
    return title.title()


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


# Sample data: A list of books with titles, authors, and publication years
books = [
    {'title': 'The Great Gatsby', 'publication_year': 1925, 'author': 'A'},
    {'title': 'The Road', 'publication_year': 2006, 'author': 'C'},
    {'title': 'Pride and Prejudice', 'publication_year': 1813, 'author': 'B'},
]

author = {
    'name': 'A',
    'location': 'US'
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

{% set s = output_json(coursesInfo) %}
{# Step 3: Output the structured information as JSON #}
{{ output_json(coursesInfo) }}
"""  # Replace with the template string from Step 2

# Create and render the template
env = Environment()
ast = env.parse(template_string)
engine = AstExecutionEngine()
context = {
    'output_json': output_json,
    'CourseraPlugin_search': CourseraPlugin_search,
}
# engine.execute(template=ast, context=context)
print(ast.to_string())
