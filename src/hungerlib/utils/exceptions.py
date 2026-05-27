# HungerLib exceptions
class HungerLibError(Exception): pass
class InvalidLevelError(HungerLibError): pass

# HungerBridge exceptions
class HungerBridgeError(Exception): pass
class InvalidModeError(HungerBridgeError): pass
