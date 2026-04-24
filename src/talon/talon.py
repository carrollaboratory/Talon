"""
Tools for simplifying interaction with the MapDragon
"""

import logging
import sys
from argparse import ArgumentParser  # , FileType

from talon import get_host_config

from . import Locu

if sys.stderr.isatty():
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.traceback import install

from talon.tools import load_tools

tools = load_tools()


def init_logging(loglevel: str | None = None):
    # When we are in the terminal, let's use the rich logging
    if loglevel is None:
        loglevel = "WARN"
    DATEFMT = "%Y-%m-%dT%H:%M:%SZ"
    if sys.stderr.isatty():
        install(show_locals=True)

        handler = RichHandler(
            level=loglevel,
            console=Console(stderr=True),
            show_time=False,
            show_level=True,
            rich_tracebacks=True,
        )
        FORMAT = "%(message)s"
    else:
        FORMAT = "%(asctime)s\t%(levelname)s\t%(message)s"
        handler = logging.StreamHandler()

    logging.basicConfig(
        level=loglevel, format=FORMAT, datefmt=DATEFMT, handlers=[handler]
    )


def exec(args: list[str] | None = None):

    # init_logging()
    host_config = get_host_config()

    parser = ArgumentParser(
        prog="talon",
        description="""MD assistant""",
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

    args = parser.parse_args(args)
    args.host_config = host_config
    init_logging(args.log_level)

    # Make sure we aren't provided both a host and a URL
    if hasattr(args, "host"):
        apiurl = host_config["hosts"][args.host]

        if args.md_url is not None:
            logging.error("Provide either --md-url or --host. Refusing to proceed")
            sys.exit(1)
    else:
        apiurl = args.md_url

    # These applications do require an endpoint to work with, so verify
    # that the information does exist
    if not hasattr(args, "host") and args.md_url is None:
        logging.error(
            f"You must provide either the API URL or a configured host to proceed"
        )
        if len(args.host_config["hosts"]) > 0:
            logging.error(
                f"Available hosts include: {', '.join(args.host_config['hosts'].keys())}"
            )
        sys.exit(1)

    locu = Locu(apiurl)

    if host_config.get("missing_host_config"):
        logging.warn(
            f"The host configuration, {host_config.get('missing_host_config')}, is missing. This file is intended to make runs less prone to mistake."
        )

    # Now, we run the command the user selected
    tools[args.command].exec(args, locu)
