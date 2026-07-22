from importlib.metadata import version as _pkg_version, PackageNotFoundError
from types import SimpleNamespace

# package version
try:
    __version__ = _pkg_version('hungerlib')
except PackageNotFoundError:
    __version__ = '0.0.0'

# modules
from .configloader import loadConfig
from .messagerouter import MessageRouter
from .panel import Panel
from .servers import GenericServer, MinecraftServer
from .bridgeclient import BridgeClient
from .discord_bot_webhook import DiscordBotWebhook
from .validator import (
    Validator,
    ValidationError,
    FatalError,
    TypeMismatchError,
    FallbackError,
    RecommendedError,
)

from .utils import (
    snapSchedule,
    runCountdownEvents,
    waitForOnline,
    waitForOffline,
    secsUntil,
    minsUntil,
    Snapshot,
    clearTerminal,
    validateAll,

    # exceptions
    HungerLibError,
    InvalidLevelError,
    InvalidModeError,
    HungerBridgeError
)

# namespaces
utils = SimpleNamespace(
    snapSchedule = snapSchedule,
    runCountdownEvents = runCountdownEvents,
    waitForOnline = waitForOnline,
    waitForOffline = waitForOffline,
    secsUntil = secsUntil,
    minsUntil = minsUntil,
    Snapshot = Snapshot,
    clearTerminal = clearTerminal,
    validateAll = validateAll,
)

servers = SimpleNamespace(
    Panel = Panel,
    Generic = GenericServer,
    Minecraft = MinecraftServer,
)



__all__ = [
    '__version__',

    # core modules
    'loadConfig',
    'MessageRouter',
    'Panel',
    'GenericServer',
    'MinecraftServer',
    'BridgeClient',
    'DiscordBotWebhook',
    'Validator',

    # sub-modules
    'snapSchedule',
    'runCountdownEvents',
    'waitForOnline',
    'waitForOffline',
    'secsUntil',
    'minsUntil',
    'Snapshot',
    'clearTerminal',
    'validateAll',

    # errors
    'ValidationError',
    'FatalError',
    'TypeMismatchError',
    'FallbackError',
    'RecommendedError',

    'HungerLibError',
    'InvalidLevelError',
    'InvalidModeError',
    'HungerBridgeError',

    # namespaces
    'utils',
    'servers',
]
