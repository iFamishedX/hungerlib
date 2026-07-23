from jinja2 import Environment, FileSystemLoader
import pathlib
from cloudflare import Cloudflare
from .message import Email

# Templates live in: src/hungerlib/email/email_templates
TEMPLATE_DIR = pathlib.Path(__file__).resolve().parent / "email_templates"

class EmailManager:
    """
    Backend email system.
    Holds API token and account ID.
    Sends emails created by EmailClient.
    """

    def __init__(self, api_token: str, account_id: str):
        self.client = Cloudflare(api_token=api_token)
        self.account_id = account_id

        # Jinja2 environment configured for HTML emails
        self.jinja = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=False,        # Cloudflare rejects escaped HTML
            trim_blocks=False,       # preserve whitespace
            lstrip_blocks=False      # preserve indentation
        )

    def render_template(self, template: str, ctx: dict) -> str:
        tmpl = self.jinja.get_template(f"{template}.html")
        return tmpl.render(**ctx)

    def send_email(self, user, email: Email) -> bool:
        # Render template if needed
        if email.template and not email.html:
            email.html = self.render_template(email.template, email.template_ctx)

        payload = {
            "account_id": self.account_id,
            "from_": f"{user.name} <{user.address}>",
            "to": email.to,
            "subject": email.subject
        }

        if email.text:
            payload["text"] = email.text

        if email.html:
            print("=== FINAL HTML SENT TO CLOUDFLARE ===")
            print(email.html)
            print("=====================================")
            payload["html"] = email.html

        if email.cc:
            payload["cc"] = email.cc

        if email.bcc:
            payload["bcc"] = email.bcc

        resp = self.client.email_sending.send(**payload)
        return bool(getattr(resp, "delivered", None))
