import os
from typing import Dict

import sendgrid
from agents import Agent, function_tool
from sendgrid.helpers.mail import Content, Email, Mail, To


@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """Send an email with the given subject and HTML body."""
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        raise ValueError("SENDGRID_API_KEY is not set")

    from_email_str = os.environ.get("SENDGRID_FROM_EMAIL", "jeryt@getnada.com")
    to_email_str = os.environ.get("SENDGRID_TO_EMAIL", "gauravsaubhagya3@gmail.com")

    sg = sendgrid.SendGridAPIClient(api_key=api_key)
    from_email = Email(from_email_str)
    to_email = To(to_email_str)
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print("Email response", response.status_code)
    return {"status": "success", "status_code": str(response.status_code)}


INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the
report converted into clean, well presented HTML with an appropriate subject line."""


email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)

