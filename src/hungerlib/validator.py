from .utils.exceptions import ValidationError


class Validator:
    """
    Reusable base validator for dataclass-based config objects.

    Provides:
    - error/warning/default tracking
    - type checking
    - fallback checking
    - structured reporting
    - subclass hooks for project-specific rules
    """

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.defaults: list[str] = []

    # reusable helpers
    def validate_key_types(self, config_obj, schema):
        """
        Validate that each field in the dataclass matches its annotated type.
        """
        from dataclasses import fields

        for f in fields(schema):
            if f.name.startswith("__"):
                continue

            expected_type = f.type
            value = getattr(config_obj, f.name, None)

            if value is None:
                continue

            if not isinstance(value, expected_type):
                self.errors.append(
                    f'{schema.__name__}.{f.name}: expected {expected_type.__name__}, '
                    f'got "{type(value).__name__}" ({value!r})'
                )

    def check_field(self, config_obj, name: str, allow_fallback: bool = True):
        """
        Unified check for:
        - missing YAML key (config.raw.<name> is None)
        - fallback usage (config.<name> == config.fallbacks.<name>)
        - whether fallback is allowed or not
        """
        raw = config_obj.raw
        fb = config_obj.fallbacks

        val = getattr(config_obj, name)
        raw_val = getattr(raw, name)
        fb_val = getattr(fb, name)

        if raw_val is None:
            if allow_fallback:
                self.warnings.append(f'{name}: key does not exist, using fallback "{fb_val}"')
            else:
                self.errors.append(f'{name}: key does not exist and fallback is not allowed')
            return

        if val == fb_val and not allow_fallback:
            self.defaults.append(f'{name}: must not be left default or empty (got "{val}")')

    # subclass override hooks
    def validate_schema(self, config_obj):
        """
        Override in subclasses to implement project-specific validation rules.
        """
        pass

    # orchestration
    def run(self, *configs):
        """
        Run validation on one or more config objects.
        """
        for cfg in configs:
            self.validate_schema(cfg)

        # fatal errors first
        if self.errors:
            raise FatalValidationError(self.format_report())

        # defaults but no errors
        if self.defaults:
            raise ValidationFallbacks(self.format_report())

        return self.format_report()

    # reporting
    def format_report(self) -> str:
        """
        Format all errors, warnings, and defaults into a readable string.
        """
        out = []

        if self.errors:
            out.append("Errors:")
            for e in self.errors:
                out.append(f" - {e}")

        if self.defaults:
            out.append("Defaults:")
            for d in self.defaults:
                out.append(f" - {d}")

        if self.warnings:
            out.append("Warnings:")
            for w in self.warnings:
                out.append(f" - {w}")

        if not out:
            return "All configs are valid."

        return "\n".join(out)
