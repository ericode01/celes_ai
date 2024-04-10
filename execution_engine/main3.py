from src.jinja2 import Template, Environment
from src.jinja2.AstExecutionEngine import AstExecutionEngine


def categorize_book(year):
    """Categorizes a book as 'Classic' or 'Modern' based on its publication year."""
    return ("Classic", 10) if year < 2000 else ("Modern", 20)

def format_title(title):
    """Formats the book title to be title case."""
    return title.title()


# Sample data: A list of books with titles, authors, and publication years
books = [
    {'title': 'The Great Gatsby',  'publication_year': 1925, 'author': 'A'},
    {'title': 'The Road',  'publication_year': 2006, 'author': 'C'},
    {'title': 'Pride and Prejudice',  'publication_year': 1813, 'author': 'B'},
]

author = {
    'name': 'A',
    'location': 'US'
}

# Initialize the Jinja2 environment
# env = Environment()

# Create the template (in a real application, you'd likely load this from a file)
template_string = """
{% set curAuthor = author %}
{% set authorList = [author.name, 'B', 'C'] %}

{% if curAuthor.name == 'b'  %}
    {% set curAuthorCondition = curAuthor.name ~ " is sick." %}
{% elif curAuthor.name == 'c' %}
    {% set curAuthorCondition =  curAuthor.name ~ " is bustard."  %}
{% else %}
    {% set curAuthorCondition = curAuthor.name ~ " looks okay --- so far." %}
{% endif %}

{% for tempAuthor in authorList %}
    {% for book in books %}
        {% set curBook = book %}
        {% set category, sells = categorize_book(curBook.publication_year) %}

        In loop for {{tempAuthor}}, {{curBook.title}}: category is {{category}} and sells is {{sells}}.

        {% if tempAuthor == book.author and book.author == curAuthor.name %}
           Author of book {{curBook.title}} is {{tempAuthor}}. Condition: {{curAuthorCondition}}
        {% elif tempAuthor == book.author %}
           Author of book {{curBook.title}} is {{tempAuthor}}. Condition unknown.
        {% else %}
            Author of book {{curBook.title}} is not {{tempAuthor}}.
        {% endif %}

    {% endfor %}
{% endfor %}
"""  # Replace with the template string from Step 2

# Create and render the template
env = Environment()
ast = env.parse(template_string)
# engine = AstExecutionEngine()
# context = {
#     'books': books,
#     'author': author,
#     'categorize_book': categorize_book,
#     'format_title': format_title
# }
# engine.execute(template=ast, context=context)

# template = Template(template_string)
output = template.render(books=books, author=author, categorize_book=categorize_book, format_title=format_title)

print(output)
