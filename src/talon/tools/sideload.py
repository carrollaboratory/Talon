__name__ = "sideload"
__description__ = "Load mappings into a mapdragon instance using the API"

import logging
import pdb
import sys
from argparse import FileType
from csv import DictReader
from typing import TextIO

import requests

from .. import Locu


def sideload_csv(locu: Locu, csvfile: TextIO, editor: str):
    reader = DictReader(csvfile, delimiter=",", quotechar='"')

    mappings = list(reader)
    body = {"editor": editor, "csvContents": mappings}

    response = locu.post("SideLoad", body)
    if response:
        logging.info(response)

    return len(mappings)


def add_arguments(subparsers):
    local_parser = subparsers.add_parser(__name__, help=__description__)

    local_parser.add_argument(
        "-e", "--editor", type=str, required=True, help="The user submitting the job"
    )

    local_parser.add_argument(
        "mappings",
        type=FileType("rt"),
        nargs="+",
        help="1 or more CSV files that conform to the sideload format",
    )


def exec(args, locu):

    for csv in args.mappings:
        linecount = sideload_csv(locu, csv, args.editor)
        logging.info(
            f"'{csv.name}' with {linecount} mapping lines was successfully loaded."
        )
