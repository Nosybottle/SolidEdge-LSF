from config.config import _Config

_config_file = "config/settings.ini"
_language_folder = "config/lang"


def load_config() -> None:
    """Load configuration and language data"""
    config.load_config(_config_file)
    lang.load_config(f"{_language_folder}/{config.language}.ini")


config = _Config()
lang = _Config()
