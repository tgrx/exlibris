from typing import Any

from framework.config import settings
from framework.dirs import DIR_CONFIG_SECRETS


def main():
    settings_values = get_settings_values()
    for setting, value in settings_values.items():
        print(f"installing {setting}={value}")  # noqa: T001

        installed, value_actual = install_setting(setting, value)
        prefix = {False: "💤", True: "👍"}[installed]
        print(f"{prefix} {setting}={value_actual}")  # noqa: T001

        print()  # noqa: T001


def get_settings_values() -> dict[str, str]:
    props = settings.schema()["properties"].items()

    settings_values = {
        name: get_secret_value(prop)
        for name, prop in props
        if prop.get("make_secret")
    }

    return settings_values


def install_setting(setting: str, value: str) -> tuple[bool, Any]:
    path = DIR_CONFIG_SECRETS / setting
    if path.is_file():
        with path.open("r") as f:
            value = f.read().strip()
        return False, value

    with path.open("w") as f:
        f.write(value)

    return True, value


def get_secret_value(prop: dict[str, Any]) -> str:
    undef = object()

    default = prop.get("default", undef)
    if default is not undef:
        value = "" if default is None else default

    else:
        typ = prop["type"]
        value = {
            "boolean": False,
            "integer": 0,
            "string": "",
        }[typ]

    return str(value)


if __name__ == "__main__":
    main()
