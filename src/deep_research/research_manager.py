import asyncio
import os
import re

from agents import Runner, gen_trace_id, trace

from deep_research.agents.email_agent import create_email_agent
from deep_research.agents.planner_agent import WebSearchItem, WebSearchPlan, planner_agent
from deep_research.agents.search_agent import search_agent
from deep_research.agents.writer_agent import ReportData, writer_agent

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ResearchManager:
    async def run(self, query: str, to_email: str | None = None):
        """Run the deep research process, yielding status updates and the final report."""
        recipient = self._resolve_recipient(to_email)

        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            trace_url = f"https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print(f"View trace: {trace_url}")
            yield f"View trace: {trace_url}"

            print("Starting research...")
            search_plan = await self.plan_searches(query)
            yield "Searches planned, starting to search..."

            search_results = await self.perform_searches(search_plan)
            yield "Searches complete, writing report..."

            report = await self.write_report(query, search_results)
            if recipient and self._is_sendgrid_configured():
                yield f"Report written, sending email to {recipient}..."
                await self.send_email(report, recipient)
                yield "Email sent, research complete"
            elif recipient and not self._is_sendgrid_configured():
                yield "Report written, email skipped (SendGrid not configured on server)"
                yield "Research complete"
            else:
                yield "Report written, email skipped (no recipient provided)"
                yield "Research complete"

            yield report.markdown_report

    def _resolve_recipient(self, to_email: str | None) -> str | None:
        """Use UI-provided email, or fall back to SENDGRID_TO_EMAIL for non-UI callers."""
        candidate = (to_email or "").strip() or os.environ.get("SENDGRID_TO_EMAIL", "").strip()
        if not candidate:
            return None
        if not _EMAIL_PATTERN.match(candidate):
            raise ValueError(f"Invalid email address: {candidate!r}")
        return candidate

    def _is_sendgrid_configured(self) -> bool:
        return bool(os.environ.get("SENDGRID_API_KEY") and os.environ.get("SENDGRID_FROM_EMAIL"))

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """Plan the searches to perform for the query."""
        print("Planning searches...")
        result = await Runner.run(planner_agent, f"Query: {query}")
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """Perform the searches for the query."""
        print("Searching...")
        num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results: list[str] = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """Perform a single search."""
        agent_input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(search_agent, agent_input)
            return str(result.final_output)
        except Exception:
            return None

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """Write the report for the query."""
        print("Thinking about report...")
        agent_input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(writer_agent, agent_input)
        print("Finished writing report")
        return result.final_output_as(ReportData)

    async def send_email(self, report: ReportData, to_email: str) -> None:
        print(f"Writing email to {to_email}...")
        agent = create_email_agent(to_email)
        await Runner.run(agent, report.markdown_report)
        print("Email sent")
