# Define the function to pass to the template
from src.jinja2 import Template


def calculate_age(birth_year):
    from datetime import datetime
    current_year = datetime.now().year
    return current_year - birth_year

# Define a Jinja2 template string
template_string = """
<!DOCTYPE html>
<html>
<head>
    <title>Age Calculator</title>
</head>
<body>
    <p>If you were born in {{ birth_year }}, you are {{ calculate_age(birth_year) }} years old.</p>
</body>
</html>
"""

# Create a Jinja2 template
template = Template(template_string)

# Render the template, passing the function and a birth year in the context
rendered_html = template.render(calculate_age=calculate_age, birth_year=1990)

# Print or save the rendered HTML
print(rendered_html)
