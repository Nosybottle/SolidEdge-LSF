import os
import logging

from config.config import _Config

logger = logging.getLogger("LSF")

_config_file = "config/settings.ini"
_language_folder = "config/lang"


def load_config() -> bool:
    """Load configuration and language data"""
    config.load_config(_config_file)

    language_file = f"{_language_folder}/{config.language}.ini"
    if not os.path.isfile(language_file):
        logger.error(f"Incorrect configuration|Selected language (\"{config.language}\") doesn't exist")
        return False

    lang.load_config(language_file)
    return True


config = _Config()
lang = _Config()
