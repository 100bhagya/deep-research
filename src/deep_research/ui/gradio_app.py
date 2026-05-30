from pathlib import Path
from typing import Any

import gradio as gr
from dotenv import load_dotenv

from deep_research.research_manager import ResearchManager

APP_THEME = gr.themes.Default(primary_hue="sky")


def _wrap_launch_with_defaults(ui: gr.Blocks) -> gr.Blocks:
    """Inject Gradio 6 launch defaults (e.g. theme) for HF Spaces and local runs."""
    original_launch = ui.launch

    def launch(*args: Any, **kwargs: Any):
        kwargs.setdefault("theme", APP_THEME)
        return original_launch(*args, **kwargs)

    ui.launch = launch  # type: ignore[method-assign]
    return ui


def build_research_ui() -> gr.Blocks:
    """Build the Gradio UI (used by Hugging Face Spaces and local entry points)."""

    async def run(query: str, to_email: str):
        try:
            async for chunk in ResearchManager().run(query, to_email=to_email):
                yield chunk
        except ValueError as exc:
            yield f"**Error:** {exc}"

    with gr.Blocks() as ui:
        gr.Markdown("# Deep Research")
        query_textbox = gr.Textbox(label="What topic would you like to research?")
        email_textbox = gr.Textbox(
            label="Email report to (optional)",
            placeholder="you@example.com",
            info="If provided, the report is emailed here when SendGrid is configured on the server.",
        )
        run_button = gr.Button("Run", variant="primary")
        report = gr.Markdown(label="Report")

        inputs = [query_textbox, email_textbox]
        run_button.click(fn=run, inputs=inputs, outputs=report)
        query_textbox.submit(fn=run, inputs=inputs, outputs=report)

    return _wrap_launch_with_defaults(ui)


def main() -> None:
    if Path(".env").is_file():
        load_dotenv(override=True)
    build_research_ui().launch(inbrowser=True)


if __name__ == "__main__":
    main()
