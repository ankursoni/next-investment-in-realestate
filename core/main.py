""" Module for command line interface (cli). """

import dataclasses

from structlog import get_logger

from core import config, provider
from core.data_source import City, State
from core.lib import (
    configure_global_logging_level,
    log_config_settings,
    parse_cli_args_with_defaults,
    parse_env_vars_with_defaults,
)
from core.provider import configure_providers


def main() -> None:
    """Execute as console application."""

    print(
        provider.PROVIDERS.data_source.get_property_listing_for_buying(
            3, 400000, 500000, City.ADELAIDE, State.SA
        )
    )


def init() -> None:
    """Entry point if called as an executable."""

    logger = get_logger()
    logger.info("Starting init from main")

    # set configuration based on environment variables and cli arguments
    cli_args = parse_cli_args_with_defaults()
    env_vars = parse_env_vars_with_defaults()
    all_values = dataclasses.asdict(env_vars) | dataclasses.asdict(cli_args)
    config.CONFIG = config.Config(**all_values)
    configure_global_logging_level(config.CONFIG.debug_mode)
    log_config_settings(config.CONFIG)

    # configure providers based on the above configuration
    configure_providers()

    logger.info("Completed init from main")


if __name__ == "__main__":
    init()
    main()
