---
title: Deep Research
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 6.14.0
app_file: app.py
python_version: "3.12"
pinned: false
---

# Deep Research

Agent-driven web research: plan searches, gather results with the OpenAI Agents SDK, write a markdown report in a Gradio UI, and optionally email it via SendGrid.

## Hugging Face Space

This repo is configured for [SaubhagyaG/Deep-Research](https://huggingface.co/spaces/SaubhagyaG/Deep-Research).

### Secrets (required before the Space will work)

Add these under **Settings → Repository secrets** in the Space UI. **Never commit API keys to git.**

| Secret | Required | Description |
|--------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for the Agents SDK |
| `SENDGRID_API_KEY` | No | SendGrid API key (email is skipped if unset) |
| `SENDGRID_FROM_EMAIL` | No | Sender address (required with SendGrid) |

For local development, copy `.env.example` to `.env` and fill in values there instead.

### GitHub Actions (automatic deploy)

Pushes to `master` or `main` sync this repo to the Space via [huggingface/hub-sync](https://github.com/huggingface/hub-sync). The workflow respects `.gitignore`, so `.env` and other ignored files are never uploaded.

**One-time setup on GitHub:**

1. Create a [Hugging Face access token](https://huggingface.co/settings/tokens) with **write** access to `SaubhagyaG/Deep-Research` (a fine-grained token scoped to that Space is recommended).
2. In your GitHub repo, go to **Settings → Secrets and variables → Actions** and add a secret named `HF_TOKEN` with that token.

After that, every push to `master` or `main` deploys automatically. You can also run the workflow manually from the **Actions** tab.

### Keeping local and Hugging Face in sync

Both environments target **Python 3.12** and the same dependency set:

| | Local | Hugging Face Space |
|---|--------|---------------------|
| Python | 3.12 (`.python-version`, `pyproject.toml`) | 3.12 (`python_version` in README frontmatter) |
| Dependencies | `uv.lock` via `uv sync` | `requirements.txt` generated from `uv.lock` on deploy |
| Secrets | `.env` (gitignored) | Space repository secrets |
| Virtual env | `.venv/` (gitignored, local only) | Built by HF from `requirements.txt` |

The deploy workflow runs `uv sync --frozen` and imports `app.demo` on Python 3.12 before uploading. It then runs `uv export --no-emit-project` so Hugging Face gets pinned third-party deps only (no `-e .`, which breaks HF's Docker build). Application code is loaded from `src/` via `app.py`.

When you add or change dependencies locally:

```bash
uv add some-package          # updates pyproject.toml + uv.lock
uv export --no-dev --no-hashes --no-emit-project -o requirements.txt   # optional: commit for visibility
git add pyproject.toml uv.lock requirements.txt
git commit -m "Update dependencies"
```

You do not need to commit an updated `requirements.txt` for Hugging Face to get the right versions — the workflow regenerates it on every deploy. Committing it is still useful so PRs show dependency changes clearly.

### Manual deploy

```bash
git remote add space https://huggingface.co/spaces/SaubhagyaG/Deep-Research
git push space master
```

Hugging Face rebuilds the Space after each sync.

## Local development

### Requirements

- **[uv](https://docs.astral.sh/uv/)** — package manager and runner (the repo includes `uv.lock` for reproducible installs)
- **Python 3.12** (see `requires-python` in `pyproject.toml`; `.python-version` is set for pyenv and uv)
- An OpenAI API key

### Setup

From the repository root, install dependencies (this uses `uv.lock`):

```bash
uv sync
```

Create a `.env` file from `.env.example` and set:

- **Required**: `OPENAI_API_KEY`
- **Optional (email)**: `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL` (recipient comes from the UI, or 

### Run

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