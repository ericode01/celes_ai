from src.jinja2 import Template

def categorize_book(year):
    """Categorizes a book as 'Classic' or 'Modern' based on its publication year."""
    return ("Classic", 10) if year < 2000 else ("Modern", 20)

def format_title(title):
    """Formats the book title to be title case."""
    return title.title()


# Sample data: A list of books with titles, authors, and publication years
books = [
    {'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'publication_year': 1925},
    {'title': 'The Road', 'author': 'Cormac McCarthy', 'publication_year': 2006},
    {'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'publication_year': 1813},
]

# Initialize the Jinja2 environment
# env = Environment()

# Create the template (in a real application, you'd likely load this from a file)
template_string = """
<!DOCTYPE html>
<html>
<head>
    <title>Book List</title>
</head>
<body>
    <h1>Book List</h1>
    <ul>
    {% for book in books %}
        {% set category, count = categorize_book(book.publication_year) %}
        <li>
            <strong>{{ format_title(book.title) }}</strong> by {{ book.author }}
            <br>
            Published in: {{ book.publication_year }}
            <br>
            Category: <span style="{% if category == 'Classic' %}color: brown{% else %}color: blue{% endif %}">{{ category }}</span>
            <br>
            Count: <span style="{% if count == 10 %}color: brown{% else %}color: blue{% endif %}">{{ count }}</span>
        </li>
    {% endfor %}
    </ul>
</body>
</html>
"""  # Replace with the template string from Step 2

# Create and render the template
template = Template(template_string)
output = template.render(books=books, categorize_book=categorize_book, format_title=format_title)

print(output)
