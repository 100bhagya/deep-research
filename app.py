"""Hugging Face Space entry point.

Exposes a Gradio `demo` object for the Space runtime. Secrets (e.g. OPENAI_API_KEY)
must be configured as Space secrets — never commit them to the repo.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv

from deep_research.ui.gradio_app import build_research_ui

# Local dev only: load .env if present. On Hugging Face, secrets are injected as env vars.
# override=False ensures Space secrets are never overwritten by a stray .env file.
if Path(".env").is_file():
    load_dotenv(override=False)

demo = build_research_ui()
