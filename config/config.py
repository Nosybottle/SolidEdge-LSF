import configparser

config_file = "config/settings.ini"
language_folder = "config/lang"


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
        if isinstance(value, (dict, configparser.SectionProxy)):
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
        # noinspection PyTypeChecker
        with open(file, "r", encoding = "utf-8") as f:
            cfg_string = "[DEFAULT]\n" + f.read()
        cfg = configparser.ConfigParser()
        cfg.read_string(cfg_string)
        self.__dict__["_config"] = _DirectAccessDict(cfg)

    def _get_value(self, item):
        """Get given settings option"""
        if self._config is None:
            raise ConfigNotLoadedError("Configuration not loaded")
        return self._config[item]

    __getitem__ = _get_value
    __getattr__ = _get_value

    def __setattr__(self, key, value) -> None:
        """Raise an error when the user attempts to set an attribute of config object"""
        raise AttributeError(f"Cannot set/modify configuration attribute of class '{self.__class__.__name__}'")


def load_config() -> None:
    """Load configuration and language data"""
    config.load_config(config_file)
    lang.load_config(f"{language_folder}/{config.language}.ini")


config = _Config()
lang = _Config()
