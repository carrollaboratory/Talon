"""
Tools for simplifying interaction with the MapDragon
"""

import logging
import os
import sys
from argparse import ArgumentParser  # , FileType

from talon import get_host_config

from . import Locu

if sys.stderr.isatty():
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.traceback import install

import importlib.metadata

MD_API_TOKEN = "MD_API_TOKEN"

try:
    __version__ = importlib.metadata.version("talon")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0.dev0"  # Fallback for uninstalled source code

from talon.tools import load_tools

logger = logging.getLogger(__name__)
tools = load_tools()


def init_logging(loglevel: str | None = None):
    # When we are in the terminal, let's use the rich logging
    if loglevel is None:
        loglevel = "WARN"
    DATEFMT = "%Y-%m-%dT%H:%M:%SZ"
    if sys.stderr.isatty():
        install(show_locals=True)  # pyright: ignore[reportPossiblyUnboundVariable]

        handler = RichHandler(  # pyright: ignore[reportPossiblyUnboundVariable]
            level=loglevel,
            console=Console(stderr=True),  # pyright: ignore[reportPossiblyUnboundVariable]
            show_time=False,
            show_level=True,
            markup=True,
            rich_tracebacks=True,
        )
        FORMAT = "%(message)s"
    else:
        FORMAT = "%(asctime)s\t%(levelname)s\t%(message)s"
        handler = logging.StreamHandler()

    logging.basicConfig(
        level=loglevel, format=FORMAT, datefmt=DATEFMT, handlers=[handler]
    )


def exec(arguments: list[str] | None = None):

    # init_logging()
    host_config = get_host_config()

    parser = ArgumentParser(
        prog="talon",
        description="""MD assistant""",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show application version and exit",
    )
    parser.add_argument(
        "-log",
        "--log-level",
        choices=["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level tolerated (default is INFO)",
    )
    if len(host_config["hosts"]) > 0:
        parser.add_argument(
            "--host",
            choices=host_config["hosts"].keys(),
            help="MapDragon host short cut as defined in ~/.mdhosts",
        )

    parser.add_argument("--md-url", type=str, help="MapDragon URL or locutus api URL")

    subparsers = parser.add_subparsers(
        title="command", dest="command", required=True, help="Command to be run"
    )
    for toolname in tools:
        tools[toolname].add_arguments(subparsers)

    args = parser.parse_args(arguments)
    args.host_config = host_config
    init_logging(args.log_level)

    apiurl = None
    token = os.getenv(MD_API_TOKEN)
    # Make sure we aren't provided both a host and a URL
    if hasattr(args, "host") and args.host is not None:
        if args.host:
            selected_host = host_config["hosts"][args.host]

            if type(selected_host) == str:
                apiurl = selected_host
                logger.warning(
                    "mdhosts doesn't have api-tokens. It is recommended you update the file."
                )
            else:
                apiurl = selected_host["host"]
                token = selected_host.get("token", token)

        if args.md_url is not None:
            logger.error("Provide either --md-url or --host. Refusing to proceed")
            sys.exit(1)
    else:
        if args.md_url:
            apiurl = args.md_url
        else:
            logger.error("You must provide either a host or a MapDragon URL.")
            sys.exit(1)

    if not token:
        logger.error(
            "Map Dragon now requires API tokens for all api connections. Unable to continue without one."
        )
        sys.exit(1)

    # These applications do require an endpoint to work with, so verify
    # that the information does exist
    if not hasattr(args, "host") and args.md_url is None:
        logger.error(
            "You must provide either the API URL or a configured host to proceed"
        )
        if len(args.host_config["hosts"]) > 0:
            logger.error(
                f"Available hosts include: {', '.join(args.host_config['hosts'].keys())}"
            )
        sys.exit(1)

    assert apiurl is not None
    assert token is not None
    locu = Locu(apiurl, token=token)

    if host_config.get("missing_host_config"):
        logger.warning(
            f"The host configuration, {host_config.get('missing_host_config')}, is missing. This file is intended to make runs less prone to mistake."
        )

    # Now, we run the command the user selected
    tools[args.command].exec(args, locu)
