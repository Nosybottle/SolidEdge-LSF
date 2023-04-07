from __future__ import annotations

import re
import configparser

config_file = "settings.ini"
language_folder = "lang"


def cast_value(value: str) -> str | int | float | list:
    value = value.strip()
    """Cast value to the correct type"""
    # int
    if re.match(r"^-?[0-9]+$", value):
        return int(value)
    # float
    if re.match(r"^-?[0-9]+\.?[0-9]*$", value):
        return float(value)
    # list
    if value.startswith("[") and value.endswith("]") and value.count("[") == 1 and value.count("]") == 1:
        return [cast_value(item) for item in value[1:-1].split(",")]
    # other
    return value


class ConfigNotLoadedError(Exception):
    """Exception when trying to access configuration before loading it"""


class _DirectAccessDict(dict):

    def _get_value(self, item):
        """Return item and convert any dicts into DirectAccessDict"""
        # When item isn't defined in self, try checking the DEFAULT section if one exists
        if item in self:
            value = super().__getitem__(item)
        elif "DEFAULT" in self:
            value = self["DEFAULT"].__getitem__(item)
        else:
            raise KeyError(item)

        # Cast any dicts to _DirectAccessDict
        if isinstance(value, dict):
            value = _DirectAccessDict(value)
        elif isinstance(value, (tuple, list)):
            value = [_DirectAccessDict(item) if isinstance(item, dict) else item for item in value]

        return value

    __getitem__ = _get_value
    __getattr__ = _get_value


class _Config:
    """Configuration loaded on demand supporting accessing options by dot notation"""

    def __init__(self):
        self.__dict__["_config"] = None

    def load_config(self, file: str) -> None:
        """Load configurations from .ini file"""
        # Add "unsectioned_values" at the beginning of the file to catch generic settings without a group
        # NOTE: this is probably a very bad practice going against .ini file standard
        cfg = configparser.ConfigParser()
        cfg.read(file)

        # Go through all loaded settings and try casting them to specific data types
        cast_cfg = {}
        for section, section_data in cfg.items():
            if section == "DEFAULT":
                continue

            # Cast data to their respective data types. Store settings from "global" section in the main cfg dict
            cast_section_data = {key: cast_value(item) for key, item in section_data.items()}
            if section == "global":
                cast_cfg.update(cast_section_data)
            else:
                cast_cfg[section] = cast_section_data

        self.__dict__["_config"] = _DirectAccessDict(cast_cfg)

    def _get_value(self, item):
        """Get given settings option"""
        if self._config is None:
            raise ConfigNotLoadedError("Configuration not loaded")
        return self._config[item]

    __getitem__ = _get_value
    __getattr__ = _get_value

    def __repr__(self):
        return "Direct access dict: " + repr(self._config)

    def __setattr__(self, key, value) -> None:
        """Raise an error when the user attempts to set an attribute of config object"""
        raise AttributeError(f"Cannot set/modify configuration attribute of class '{self.__class__.__name__}'")


def load_config() -> None:
    """Load configuration and language data"""
    config.load_config(config_file)
    lang.load_config(f"{language_folder}/{config.language}.ini")


config = _Config()
lang = _Config()
