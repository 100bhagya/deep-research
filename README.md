# Deep Research (Python)

A small “deep research” pipeline using the OpenAI Agents SDK:

- Plan web searches
- Run web searches
- Write a long-form markdown report
- Optionally email the report via SendGrid

## Requirements

- **[uv](https://docs.astral.sh/uv/)** — package manager and runner (the repo includes `uv.lock` for reproducible installs)
- **Python 3.12** (see `requires-python` in `pyproject.toml`; `.python-version` is set for pyenv and uv)
- An OpenAI API key

## Setup

From the repository root, install dependencies (this uses `uv.lock`):

```bash
uv sync
```

Create a `.env` file in the project root and set:

- **Required**: `OPENAI_API_KEY`
- **Optional (email)**: `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL`, `SENDGRID_TO_EMAIL`

## Run

Start the Gradio UI:

```bash
uv run src/main.py
```

Or use the installed console script:

```bash
uv run deep-research
```

Then open the browser window Gradio launches and submit a query.

### Without uv

If you prefer pip, use Python 3.12 and an editable install:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
python src/main.py
# or: deep-research
```

Dependencies may not match `uv.lock` exactly.

## Notes

- Tracing: the app prints and streams a trace URL from the OpenAI Agents SDK.
- Email: if SendGrid variables are not set, the run will skip emailing and still finish with the report shown in the UI.
