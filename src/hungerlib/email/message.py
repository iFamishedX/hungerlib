from __future__ import annotations

class Email:
    '''
    Simple email data container.
    '''
    def __init__(
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
        self.subject = subject
        self.text = text or ''
        self.html = html or ''
        self.to = self._normalize(to)
        self.cc = self._normalize(cc)
        self.bcc = self._normalize(bcc)
        self.template = template
        self.template_ctx = template_ctx or {}

    @staticmethod
    def _normalize(value) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [s.strip() for s in value.split(',') if s.strip()]
        return [str(x).strip() for x in value]
