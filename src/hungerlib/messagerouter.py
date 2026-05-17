from hungerlib.datamap import mapit
from hungerlib.utils.colormaps import ASCII_COLOR_MAP, MC_COLOR_MAP, STRIP_COLOR_MAP
import logging
from pathlib import Path
from datetime import datetime


class MessageRouter:
    def __init__(self,
        name: str,
        Servers: list,
        log_path: str,

        origin_maps:      list = [ASCII_COLOR_MAP],
        destination_maps: list = [ASCII_COLOR_MAP],
        broadcast_maps:   list = [MC_COLOR_MAP],
        file_maps:        list = [STRIP_COLOR_MAP],

        info_prefix:       str = "<white>[INFO]: ",
        warn_prefix:       str = "<orange>[WARN]: ",
        error_prefix:      str = "<red>[ERROR]: ",
    ):

        self.name = name
        self.Servers = Servers

        # default maps per route
        self.origin_maps = origin_maps
        self.destination_maps = destination_maps
        self.broadcast_maps = broadcast_maps
        self.file_maps = file_maps

        # origin prefixes
        self.info_prefix = info_prefix
        self.warn_prefix = warn_prefix
        self.error_prefix = error_prefix

        # file logger
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self._init_file_logger()

    def _init_file_logger(self):
        log_file = self.log_path / f"{self.name}_{datetime.now().strftime('%Y-%m-%d')}.log"
        if not self.logger.handlers:
            handler = logging.FileHandler(str(log_file))
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s",
                datefmt="%H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    # internal utils
    def _format(self, template, maps, **ctx):
        return mapit(template, only_maps=maps, **ctx)

    def _merge_maps(self, base, extra):
        maps = list(base)
        if extra:
            maps.extend(extra)
        return maps

    # routing primitives
    def origin(self, template, level="info", extra_maps=None, override_maps=None, **ctx):
        # format
        maps = self._merge_maps(override_maps or self.origin_maps, extra_maps)
        mapped = self._format(template, maps, **ctx)
        if level == "info":    prefix = mapit(self.info_prefix, [ASCII_COLOR_MAP])
        elif level == "warn":  prefix = mapit(self.warn_prefix, [ASCII_COLOR_MAP])
        elif level == "error": prefix = mapit(self.error_prefix, [ASCII_COLOR_MAP])
        else:                  prefix = ""
        msg = prefix + mapped

        # send
        print(msg)
        return msg

    def destination(self, template, level="info", extra_maps=None, override_maps=None, **ctx):
        # format
        maps = self._merge_maps(override_maps or self.destination_maps, extra_maps)
        msg = self._format(template, maps, **ctx)
        
        # send
        for server in self.Servers:
            if hasattr(server, "bridge"):
                server.bridge.log(msg, level)
        return msg

    def broadcast(self, template, extra_maps=None, override_maps=None, **ctx):
        # format
        maps = self._merge_maps(override_maps or self.broadcast_maps, extra_maps)
        msg = self._format(template, maps, **ctx)

        # send
        for server in self.Servers:
            if hasattr(server, "sendBroadcast"):
                server.sendBroadcast(msg)
        return msg

    def filelog(self, template, level="info", extra_maps=None, override_maps=None, **ctx):
        # format
        maps = self._merge_maps(override_maps or self.file_maps, extra_maps)
        msg = self._format(template, maps, **ctx)

        # send
        {
            "info": self.logger.info,
            "warn": self.logger.warning,
            "error": self.logger.error
        }[level](msg)
        return msg

    # simple passthrough helpers (origin + file)
    def info(self, template, extra_maps=None, override_maps=None, **ctx):
        msg = self.origin(template=template, level="info", extra_maps=extra_maps, override_maps=override_maps, **ctx)
        self.filelog(template=template, level="info", extra_maps=extra_maps, override_maps=override_maps, **ctx)
        return msg

    def warn(self, template, extra_maps=None, override_maps=None, **ctx):
        msg = self.origin(template=template, level="warn", extra_maps=extra_maps, override_maps=override_maps, **ctx)
        self.filelog(template=template, level="warn", extra_maps=extra_maps, override_maps=override_maps, **ctx)
        return msg

    def error(self, template, extra_maps=None, override_maps=None, **ctx):
        msg = self.origin(template=template, level="error", extra_maps=extra_maps, override_maps=override_maps, **ctx)
        self.filelog(template=template, level="error", extra_maps=extra_maps, override_maps=override_maps, **ctx)
        return msg
