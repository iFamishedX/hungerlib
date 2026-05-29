# HungerLib exceptions
class HungerLibError(Exception): pass

class InvalidLevelError(HungerLibError): pass
class InvalidModeError(HungerLibError): pass

# HungerBridge exceptions
class HungerBridgeError(Exception): pass
