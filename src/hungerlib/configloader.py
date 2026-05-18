import os
import yaml
import importlib
from dataclasses import fields, MISSING


# yaml helpers
def load_yaml(path: str) -> dict:
    '''Loads a YAML file and always returns a dict.'''
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}


def deep_get(data: dict, path: str):
    '''Resolve dotted YAML paths like 'server.port\''''
    cur = data
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
        if cur is None:
            return None
    return cur


def convert_value(value, annotation):
    '''Convert YAML values to the dataclass field type.'''
    try:
        if annotation is int:
            return int(value)
        if annotation is float:
            return float(value)
        if annotation is bool:
            return bool(value)
    except Exception:
        pass
    return value


# main loader
def loadConfig(schema, runtime_path: str | None = None):
    '''
    Loads a config dataclass using:
    - schema.__config_path__ for default file
    - dataclass defaults as YAML key paths (mode="config")
    '''

    # 1. Resolve runtime path
    if runtime_path is None:
        runtime_path = getattr(schema, "__user_config_path__", "config/config.yaml")

    abs_runtime = os.path.abspath(runtime_path)
    os.makedirs(os.path.dirname(abs_runtime), exist_ok=True)

    # 2. Resolve default config path inside the package
    default_rel = getattr(schema, "__default_config_path__", None)
    abs_default = None

    if default_rel:
        module = importlib.import_module(schema.__module__)
        schema_file = os.path.abspath(module.__file__)
        package_dir = os.path.dirname(schema_file)
        abs_default = os.path.join(package_dir, default_rel.lstrip("/"))

    # 3. Ensure runtime config exists
    if not os.path.exists(abs_runtime):
        if abs_default and os.path.exists(abs_default):
            with open(abs_default, "r") as src, open(abs_runtime, "w") as dst:
                dst.write(src.read())
        else:
            with open(abs_runtime, "w") as f:
                f.write("# No default config found.\n")

    # 4. Load YAML
    raw = load_yaml(abs_runtime)
    values = {}

    # 5. Map YAML → dataclass fields
    mode = getattr(schema, "__mode__", None)

    for f in fields(schema):
        if f.name.startswith("__"):
            continue

        default = f.default

        # mode="config": default string = YAML path
        if mode == "config" and isinstance(default, str):
            yaml_path = default
            value = deep_get(raw, yaml_path)
            if value is not None:
                values[f.name] = convert_value(value, f.type)
                continue

        # fallback to dataclass default
        if default is not MISSING:
            values[f.name] = convert_value(default, f.type)

    return schema(**values)
