# HungerLib exceptions
class HungerLibError(Exception): pass

class ValidationError(HungerLibError): pass
class FatalValidationError(ValidationError): pass
class ValidationFallbacks(ValidationError): pass

class InvalidLevelError(HungerLibError): pass
class InvalidModeError(HungerLibError): pass

# HungerBridge exceptions
class HungerBridgeError(Exception): pass
