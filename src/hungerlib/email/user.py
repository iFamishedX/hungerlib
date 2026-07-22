from __future__ import annotations
from .message import Email

class EmailUser:
    '''
    Represents a sender identity.
    The frontend API for sending emails.
    '''
    def __init__(self, name: str, address: str, manager):
        self.name = name
        self.address = address
        self.manager = manager  # backend EmailManager

    def send(
        self,
        subject: str,
        text: str | None = None,
        html: str | None = None,
        to: list | str | None = None,
        cc: list | str | None = None,
        bcc: list | str | None = None,
        template: str | None = None,
        template_ctx: dict | None = None
    ):
        email = Email(
            subject=subject,
            text=text,
            html=html,
            to=to,
            cc=cc,
            bcc=bcc,
            template=template,
            template_ctx=template_ctx
        )
        return self.manager.send_email(self, email)
