from mapres import MapResolver, maps
import logging
from pathlib import Path
from datetime import datetime
from .utils.exceptions import InvalidLevelError

class MessageRouter:
    def __init__(
        self,
        name: str,
        Servers: list,
        log_path: str,

        origin_maps      = [maps.ascii_colors],
        destination_maps = [maps.ascii_colors],
        broadcast_maps   = [maps.mc_colors],
        file_maps        = [maps.strip_colors],
        prefix_maps      = [maps.ascii_colors, maps.time],

        info_prefix  = '<white>[%hh%:%mm%:%ss%] [INFO]: ',
        warn_prefix  = '<yellow>[%hh%:%mm%:%ss%] [WARN]: ',
        error_prefix = '<red>[%hh%:%mm%:%ss%] [ERROR]: ',
    ):
        self.name = name
        self.Servers = Servers

        # default maps per route
        self.origin_maps = origin_maps
        self.destination_maps = destination_maps
        self.broadcast_maps = broadcast_maps
        self.file_maps = file_maps
        self.prefix_maps = prefix_maps

        # prefixes
        self.info_prefix = info_prefix
        self.warn_prefix = warn_prefix
        self.error_prefix = error_prefix

        # resolver
        self.resolver = MapResolver()
        self.res = self.resolver.res

        # file logger
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self._init_file_logger()

    def _init_file_logger(self):
        log_file = self.log_path / f'{self.name}_{datetime.now().strftime("%Y-%m-%d")}.log'
        if not self.logger.handlers:
            handler = logging.FileHandler(str(log_file))
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    # like this, lowercase, no fancy bs
    def _format(self, text, maps, **ctx):
        return self.res(text, override_maps=maps, **ctx)

    def _merge_maps(self, base, extra):
        maps = list(base)
        if extra:
            maps.extend(extra)
        return maps

    # routing primitives
    def origin(self, text, level='info', extra_maps=None, override_maps=None, **ctx):
        maps = self._merge_maps(override_maps or self.origin_maps, extra_maps)
        mapped = self._format(text, maps, **ctx)
        level = level.lower() if isinstance(level, str) else level

        if level == 'info':
            prefix = self.res(self.info_prefix, override_maps=self.prefix_maps)
        elif level == 'warn':
            prefix = self.res(self.warn_prefix, override_maps=self.prefix_maps)
        elif level == 'error':
            prefix = self.res(self.error_prefix, override_maps=self.prefix_maps)
        elif level is None:
            prefix = ''
        elif level == 'custom':
            prefix = ctx.get('prefix', '')
        else:
            prefix = self.res(level, override_maps=self.prefix_maps)

        msg = prefix + mapped
        print(msg)
        return msg

    def destination(self, text, level='info', extra_maps=None, override_maps=None, **ctx):
        maps = self._merge_maps(override_maps or self.destination_maps, extra_maps)
        msg = self._format(text, maps, **ctx)

        for server in self.Servers:
            if hasattr(server, 'bridge'):
                server.bridge.log(msg, level)
        return msg

    def broadcast(self, text, extra_maps=None, override_maps=None, **ctx):
        maps = self._merge_maps(override_maps or self.broadcast_maps, extra_maps)
        msg = self._format(text, maps, **ctx)

        for server in self.Servers:
            if hasattr(server, 'sendBroadcast'):
                server.sendBroadcast(msg)
        return msg

    def filelog(self, text, level='info', extra_maps=None, override_maps=None, **ctx):
        maps = self._merge_maps(override_maps or self.file_maps, extra_maps)
        msg = self._format(text, maps, **ctx)

        {
            'info': self.logger.info,
            'warn': self.logger.warning,
            'error': self.logger.error
        }[level](msg)
        return msg

    # passthrough helpers
    def info(self, text, extra_maps=None, override_maps=None, **ctx):
        msg = self.origin(text, 'info', extra_maps, override_maps, **ctx)
        self.filelog(text, 'info', extra_maps, override_maps, **ctx)
        return msg

    def warn(self, text, extra_maps=None, override_maps=None, **ctx):
        msg = self.origin(text, 'warn', extra_maps, override_maps, **ctx)
        self.filelog(text, 'warn', extra_maps, override_maps, **ctx)
        return msg

    def error(self, text, extra_maps=None, override_maps=None, **ctx):
        msg = self.origin(text, 'error', extra_maps, override_maps, **ctx)
        self.filelog(text, 'error', extra_maps, override_maps, **ctx)
        return msg
