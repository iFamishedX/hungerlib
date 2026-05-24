import requests
import json
from .utils.exceptions import HungerBridgeError, InvalidLevelError


class BridgeClient:
    def __init__(self, url: str, token: str):
        self.base = url.rstrip('/')
        self.headers = {
            'X-Auth-Key': token,
            'Content-Type': 'application/json'
        }

        # Detect v2 support once
        self._v2 = self._detect_v2()

    # internal helpers
    def _post(self, path, payload):
        r = requests.post(f'{self.base}{path}', headers=self.headers, json=payload)
        if not r.ok:
            raise HungerBridgeError(f'HungerBridge error {r.status_code}: {r.text}')
        try:
            return r.json()
        except:
            return r.text

    def _get(self, path):
        r = requests.get(f'{self.base}{path}', headers=self.headers)
        if not r.ok:
            raise HungerBridgeError(f'HungerBridge error {r.status_code}: {r.text}')
        try:
            return r.json()
        except:
            return r.text

    def _detect_v2(self) -> bool:
        try:
            resp = self._get('/v2/ping')
            return isinstance(resp, dict) and resp.get('ok') is True
        except:
            return False


    # public api
    def runCommand(
        self,
        command: str,
        show_console: bool = False,
        silent: bool = False,
        normalize: bool = True
    ):
        """
        Runs a command on the server.
        Automatically uses v2 if available, otherwise v1.
        """
        path = '/v2/run' if self._v2 else '/v1/run'

        data = self._post(path, {
            'command': command,
            'silent': silent,
            'show_console': show_console
        })
        if not normalize:
            return data
        if isinstance(data, list):
            return '\n'.join(str(x) for x in data)
        if isinstance(data, dict):
            out = data.get('output')
            if isinstance(out, list):
                return '\n'.join(str(x) for x in out)
            if isinstance(out, (str, bytes)):
                return out
            return None
        if isinstance(data, (str, bytes)):
            return data
        return None

    def log(self, message: str, level: str = 'info') -> dict:
        """
        Logs a message to the server
        """
        valid_levels = ['info', 'warn', 'error', None]
        if level not in valid_levels:
            raise InvalidLevelError(f'"{level}" is not a valid log level')

        path = '/v2/log' if self._v2 else '/v1/log'
        if level is not None:
            return self._post(path, {
                'level': level,
                'message': message
            })
        else:
            no_level_message = (
                '\b' * 20 + message     # removes level (crude method, may change later)
            )
            return self._post(path, {
                'level': 'info',
                'message': no_level_message
            })

    def ping(self) -> dict:
        """
        Returns latency info
        """
        if not self._v2:
            raise HungerBridgeError("The ping endpoint is not supported by this server")
        return self._get('/v2/ping')

    def getInfo(self) -> dict:
        """
        Returns bridge info
        """
        if not self._v2:
            raise HungerBridgeError("The info endpoint is not supported by this server")
        return self._get('/v2/info')

    def getStatus(self) -> dict:
        """
        Returns server status
        """
        if self._v2:
            return self._get('/v2/status')
        return self._get('/v1/status')

    def getVersion(self) -> dict:
        """
        Returns version info
        """
        if self._v2:
            return self.getInfo()
        return self._get('/v1/version')
