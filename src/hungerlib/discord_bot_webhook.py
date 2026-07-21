import requests

class DiscordBotWebhook:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
    
    def send(self, event: str, **ctx):
        requests.post(
            self.url,
            json={"event": event, **ctx},
            timeout=5
        ).raise_for_status()
