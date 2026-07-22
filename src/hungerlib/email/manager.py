from __future__ import annotations
import pathlib
from cloudflare import Cloudflare
from mapres import res
from .message import Email

TEMPLATE_DIR = pathlib.Path(__file__).resolve().parent.parent / 'email_templates'

class EmailManager:
    '''
    Backend email system.
    Holds API token and account ID.
    Sends emails created by EmailClient.
    '''
    def __init__(self, api_token: str, account_id: str):
        self.client = Cloudflare(api_token=api_token)
        self.account_id = account_id

    # -------------------------
    # Template loader
    # -------------------------
    def load_template(self, name: str) -> str:
        path = TEMPLATE_DIR / f'{name}.html'
        return path.read_text(encoding='utf8')

    # -------------------------
    # Template renderer
    # -------------------------
    def render_template(self, template: str, ctx: dict) -> str:
        raw = self.load_template(template)
        return res(raw, **ctx)

    # -------------------------
    # Actual sending
    # -------------------------
    def send_email(self, user, email: Email) -> bool:
        to_str = ','.join(email.to)
        cc_str = ','.join(email.cc) if email.cc else None
        bcc_str = ','.join(email.bcc) if email.bcc else None

        if email.template and not email.html:
            email.html = self.render_template(email.template, email.template_ctx)

        resp = self.client.email_sending.send(
            account_id=self.account_id,
            from_=f'{user.name} <{user.address}>',
            to=to_str,
            cc=cc_str,
            bcc=bcc_str,
            subject=email.subject,
            text=email.text,
            html=email.html
        )

        return bool(getattr(resp, 'delivered', None))
