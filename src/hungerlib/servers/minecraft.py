import time
import re

from hungerlib.panel import Panel
from hungerlib.utils.colormaps import MC_COLOR_MAP, ASCII_COLOR_MAP
from hungerlib.servers import GenericServer
from hungerlib.bridgeclient import BridgeClient
from hungerlib.datamap import mapit


class MinecraftServer(GenericServer):
    def __init__(
        self,
        name,
        panel: Panel,
        server_id,
        server_domain,
        server_port,
        bridge_port,
        bridge_token,
        tpsCommand='tt20 tps',
    ):
        super().__init__(
            name,
            panel,
            server_id,
        )

        # Minecraft-specific fields
        self.server_domain = server_domain
        self.server_port = server_port
        self.tpsCommand = tpsCommand

        # HungerBridge client
        bridge_url = f"http://{server_domain}:{bridge_port}"
        self.bridge = BridgeClient(bridge_url, bridge_token)


    # getter methods
    def getPlayers(self):
        output = self.bridge.runCommand("list")
        if not output:
            return None
        m = re.search(r"There are (\d+)", output)
        return int(m.group(1)) if m else None

    def getTPS(self, type="raw", rounding=10):
        """
        This has limitations and is not yet complete. It currently ONLY parses TT20's tps command.
        Example: /tt20 tps
        This parser WILL NOT WORK with other configurations!
        """
        output = self.sendConsoleCommand(self.tpsCommand)
        if not output:
            return None
        clean = re.sub(r"§.", "", output)
        m = re.search(
            r"TPS\s+([0-9]+\.[0-9]+)\s+with average\s+([0-9]+\.[0-9]+)\s+accurate\s+([0-9]+\.[0-9]+)",
            clean
        )
        if not m:
            return None
        raw, avg, acc = map(float, m.groups())
        table = {"raw": raw, "avg": avg, "acc": acc}
        value = table.get(type, avg)
        return round(value, rounding) if rounding else value

    # commands
    def sendConsoleCommand(self, command, show_console=False, silent=False, normalize=True):
        return self.bridge.runCommand(
        command,
        show_console=show_console,
        silent=silent,
        normalize=normalize
    )

    def sendBroadcast(self, message):
        safe = message.replace('"', '\\"')
        cmd = f'tellraw @a {{"text":"{safe}"}}'
        return self.bridge.runCommand(cmd, show_console=True)
