__name__ = "sideload"
__summary__ = "Load mappings into a mapdragon instance using the API"
__description__ = "Load mappings into a mapdragon instance using the API"

import logging
from argparse import FileType
from csv import DictReader
from typing import TextIO

from .. import Locu

logger = logging.getLogger(__name__)
REQUIRED_COLS = [
    "table_id",
    "source_variable",
    "code",
    "display",
    "system",
    "provenance",
]


def sideload_csv(locu: Locu, csvfile: TextIO, editor: str):
    reader = DictReader(csvfile, delimiter=",", quotechar='"')

    missing_columns = set(REQUIRED_COLS) - set(reader.fieldnames or [])

    if len(missing_columns) > 0:
        msg = f"Invalid CSV header. Missing required columns: {', '.join(list(missing_columns))}"
        logger.error(msg)
        raise ValueError(msg)

    mappings = list(reader)
    body = {"editor": editor, "csvContents": mappings}

    response = locu.post("SideLoad", body)

    if response:
        logger.info(response)

    return len(mappings)


def add_arguments(subparsers):
    local_parser = subparsers.add_parser(
        __name__, help=__summary__, description=__description__
    )

    local_parser.add_argument(
        "-e", "--editor", type=str, required=True, help="The user submitting the job"
    )

    local_parser.add_argument(
        "mappings",
        type=FileType("rt", encoding="utf-8-sig"),
        nargs="+",
        help="1 or more CSV files that conform to the sideload format",
    )


def exec(args, locu):

    for csv in args.mappings:
        linecount = sideload_csv(locu, csv, args.editor)
        logger.info(
            f"'{csv.name}' with {linecount} mapping lines was successfully loaded."
        )
