# Celes AI

**Turn a plain-English goal into a program an LLM writes, a human can read, and an engine can run, pause, and repair step by step.**

Celes AI is an experimental agent framework built on [Semantic Kernel](https://github.com/microsoft/semantic-kernel). You describe what you want done, optionally with a Standard Operating Procedure (SOP). The LLM writes a plan as a small **Jinja2 program** that calls your tools. Celes then runs that plan **one AST node at a time**, so when a step fails the AI can diagnose it, propose a fix for just that step, and continue from where it left off.

---

## The idea

Most LLM agents work in one of two ways:

- **One tool call at a time** (ReAct-style). Flexible, but slow and expensive, and the overall plan is never written down.
- **Generate the whole script, then run it.** Fast, but one bad line breaks the whole run and you start over.

Celes sits in between. The plan is a full program written up front, so you can read and review it before it runs. But the program runs inside an interpreter Celes controls, so a failure becomes a **conversation about one line of code**, not a restart.

```
 Goal + SOP ──▶ Planner (LLM) ──▶ Jinja2 plan ──▶ AST ──▶ Execution engine ──▶ Plugins
                                                   ▲              │
                                                   │    error on one node
                                                   │              ▼
                                                   └── patched node ◀── LLM diagnoses
                                                       (you approve)     syntax / logic / data
```

### Why Jinja2?

- **LLMs already write it well.** It looks like Python and shows up everywhere in their training data.
- **It's small.** `set`, `if / elif / else`, `for`, comparisons, and function calls. That covers most business workflows, with a much smaller surface for the model to get wrong than full Python.
- **It's readable.** Each step carries a `{# comment #}`, so the plan reads like a checklist a non-engineer can review.

### What a plan looks like

Goal: *"Email everyone in the spreadsheet we haven't contacted yet, then mark them as sent."*

```jinja
{# Step 1: Load the Excel file into a JSON list #}
{% set rows = ExcelPlugin___ExcelFileToJsonList(full_file_path = excel_file_path_from_user_input) %}

{# Step 2: Keep only people we haven't emailed #}
{% set pending = JsonPlugin___QueryJsonData(json_data = rows, query = "`Status` != 'Email sent'") %}

{# Step 3: Email each person and mark them as sent #}
{% for person in pending %}
    {% set ok = EmailPlugin___SendAnEmail(recipient_name = person['Creator name'], recipient_email = person['Email']) %}
    {% if ok %}
        {% set _ = JsonPlugin___UpsertObjectKeyValueWithConditionInList(json_data = rows, key_value_pair_to_check = ('Email', person['Email']), key_value_pair_to_upsert = ('Status', 'Email sent')) %}
    {% endif %}
{% endfor %}

{# Step 4: Save the result #}
{% set _ = ExcelPlugin___JsonListToExcelFile(json_data = rows, full_file_path = updated_excel_file_path_from_user_input) %}
```

The planner also returns the **inputs it needs from the user** (here, the two file paths) as structured fields, so the app can ask for them before running anything.

---

## Built to be extended

Extensibility is the core design goal. Every layer is a seam you can swap or grow.

### 1. Add a capability by writing a Python function

Any Semantic Kernel plugin becomes something the planner can use. There's no prompt to edit and no registry to update: the planner builds its "function manual" from the kernel at plan time, using each function's name, description, parameter types, and return type.

```python
from typing import Annotated
from semantic_kernel.functions import kernel_function

class SlackPlugin:
    @kernel_function(name="PostMessage", description="Post a message to a Slack channel.")
    def post_message(
        self,
        channel: Annotated[str, "The channel name, e.g. #ops."],
        text: Annotated[str, "The message body."],
    ) -> Annotated[bool, "True if the message was posted."]:
        ...

kernel.import_plugin_from_object(SlackPlugin(), "SlackPlugin")
```

The LLM can now write `{% set ok = SlackPlugin___PostMessage(channel = "#ops", text = summary) %}` in its plans. Plugins compose freely: Excel, JSON, and Email in this repo were written independently and the planner chains them together.

### 2. Steer the plan with an SOP, not code

Pass a Standard Operating Procedure alongside the goal and the planner must follow it. Business rules live in plain text that domain experts can own and edit, while the plugins stay generic.

### 3. Swap the model

The planner and the repair loop only talk to a Semantic Kernel `service_id`. Point it at any chat completion service Semantic Kernel supports (OpenAI, Azure OpenAI, and others) without touching the engine.

### 4. Extend the language itself

`jinja2_ast/` is a fork of Jinja2 where each AST node implements its own `eval()` and `to_string()`. To support a new construct, implement those two methods on the node. Because execution is driven by an explicit stack instead of Python recursion, a new node can:

- push child nodes to run next,
- re-push itself to resume later (this is how `for` loops survive a mid-iteration repair),
- be swapped out at runtime for a patched version.

### 5. Customize error recovery

When a node fails, the engine sends the failing snippet and the error to the LLM, which classifies it:

| Type | Example | What happens |
|---|---|---|
| **syntax** | Wrong function or argument name | LLM rewrites that snippet; you approve; the engine swaps the node and retries |
| **logic** | Missing check, wrong step order | Same as above, with guards added if needed |
| **data** | Undefined variable, unexpected value | You're asked for the missing values; the engine updates the context and retries |

The prompt, the categories, and the approval step all live in `AstExecutionEngine.mitigate_execution_error`. You can add categories, auto-approve low-risk fixes, or route approvals to a UI instead of the terminal.

---

## How it works

| Component | Path | Role |
|---|---|---|
| Planner | `planner/jinja2_planner.py` | Builds the prompt (goal, SOP, function manual, few-shot example) and parses the LLM's JSON into a plan AST plus required user inputs |
| Function manual | `planner/jinja2_planner_utils.py` | Turns every kernel function into a short spec the LLM can read |
| Execution engine | `execution_engine/AstExecutionEngine.py` | Stack-based interpreter with the AI repair loop and human approval |
| Kernel bridge | `extensions/kernel_extensions.py` | Resolves `Plugin___Function` names to Semantic Kernel functions |
| Plan language | `jinja2_ast/` | Jinja2 fork with node-level `eval()` / `to_string()` |
| Plugins | `plugins/` | Example tools: Excel ⇄ JSON, JSON query/upsert/print, email sending |

## Getting started

> **Status:** early prototype. It targets the pre-1.0 Semantic Kernel Python API (`sk.openai_settings_from_dot_env`, `kernel.import_plugin_from_object`).

```bash
pip install "semantic-kernel<1.0" pandas openpyxl python-dotenv sib-api-v3-sdk
```

Copy the example config and fill in your own keys:

```bash
cp .env.example .env
```

`.env` is git-ignored. It holds `OPENAI_API_KEY` / `OPENAI_ORG_ID` for the planner, plus `BREVO_API_KEY` and sender details if you use `EmailPlugin`.

Then run the end-to-end example:

```bash
python main7.py
```

It plans the spreadsheet-outreach workflow above, asks for the input file paths, and runs the plan, stopping to ask you whenever a step needs fixing.

## Roadmap ideas

- Plan review and editing before execution
- Pluggable approval handlers (CLI, web UI, auto-approve policies)
- Persisting and resuming a run from its execution stack
- Plan caching and reuse for repeated goals
- Tests and packaging
