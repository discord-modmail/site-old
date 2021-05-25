import logging
import os
import typing
from pathlib import Path
from typing import Any, Dict, Tuple

import toml
from pydantic import BaseSettings as PydanticBaseSettings
from pydantic.env_settings import SettingsSourceCallable

log = logging.getLogger(__name__)

CONFIG_PATHS: list = [
    f"{os.getcwd()}/config.toml",
    f"{os.getcwd()}/site/config.toml",
    "./config.toml",
]

DEFAULT_CONFIG_PATHS = [os.path.join(os.path.dirname(__file__), "config-default.toml")]


def determine_file_path(
    paths: typing.Union[list, tuple], config_type: str = "default"
) -> typing.Union[str, None]:
    """Determine the location of a configuration file, given a list of paths."""
    path = None
    for file_path in paths:
        config_file = Path(file_path)
        if (config_file).exists():
            path = config_file
            log.debug(f"Found {config_type} config at {file_path}")
            break
    return path or None


DEFAULT_CONFIG_PATH = determine_file_path(DEFAULT_CONFIG_PATHS)
USER_CONFIG_PATH = determine_file_path(CONFIG_PATHS, config_type="")


def toml_default_config_source(settings: PydanticBaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a toml file.

    from within the module's source folder.
    """
    if DEFAULT_CONFIG_PATH is not None:
        return dict(**toml.load(DEFAULT_CONFIG_PATH))
    return dict()


def toml_user_config_source(settings: PydanticBaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a toml file.

    from within the module's source folder.
    """
    if USER_CONFIG_PATH is not None:
        return dict(**toml.load(USER_CONFIG_PATH))
    return dict()


class BaseSettings(PydanticBaseSettings):
    """
    Custom Pydantic base class for settings, with a Config that also loads directly from toml.

    Loading methods are from toml config files, class defaults, passed arguments, and env variables.
    """

    class Config:
        """BaseSettings custom default Config."""

        extra = "ignore"
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            """Modify Pydantic default settings to add toml as a source and priortise env variables."""
            return (
                env_settings,
                init_settings,
                file_secret_settings,
                toml_user_config_source,
                toml_default_config_source,
            )


class SiteConfig(BaseSettings):
    """Pydantic model for Site Settings."""

    CLIENT_ID: str
    CLIENT_SECRET: str


CONFIG = SiteConfig(_env_file="./.env")
