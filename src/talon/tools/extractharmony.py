__name__ = "extract-harmony"
__summary__ = "Pull harmony content from MapDragon API"
__description__ = "Pull all harmony content from a MapDragon API for a given set of studies, tables and data-dictionaries"


import logging
import sys
from csv import DictWriter
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, NamedTuple

from .. import Locu
from . import pull_harmony_content

logger = logging.getLogger(__name__)


def export_harmony(
    locu: Locu,
    mapping_filename: str,
    study_ids: list[str] | None = None,
    dd_ids: list[str] | None = None,
    table_ids: list[str] | None = None,
    format: str = "FTD",
    replacecontent: bool = False,
):

    harmony_response = pull_harmony_content(
        locu, study_ids=study_ids, dd_ids=dd_ids, table_ids=table_ids, format=format
    )
    harmony_content = harmony_response["harmony"]
    harmony_omissions = harmony_response["omitted"]
    if len(harmony_omissions) > 0:
        logger.warning(
            "one or more members of your request was not authorized for release: "
        )
        logger.warning(f"{', '.join(harmony_omissions.keys())}")

    mappings = [Mapping.from_dict(item) for item in harmony_content]

    if not Path(mapping_filename).exists() or replacecontent:
        with Path(mapping_filename).open("wt") as outf:
            writer = DictWriter(outf, fieldnames=list(vars(mappings[0].mapping).keys()))
            writer.writeheader()

            for mapping in mappings:
                mapping.mapping.writerow(writer)


class MappingResults(NamedTuple):
    mapping: "Mapping"
    dropped: set[str]


@dataclass
class Mapping:
    # Required Fields
    table_id: str
    source_text: str
    source_system: str
    mapped_code: str
    mapped_display: str
    mapped_system: str

    # Optional Fields (Default to None)
    study_title: str | None = None
    study_name: str | None = None
    study_id: str | None = None
    dd_name: str | None = None
    dd_id: str | None = None
    version: str | None = None
    source_description: str | None = None
    source_domain: str | None = None
    parent_varname: str | None = None
    mapping_relationship: str | None = None
    comment: str | None = None

    ignore: bool | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MappingResults:
        """Convert the basic dict into a Mapping"""

        cleaned_fieldnames = {k.replace(" ", "_"): v for k, v in data.items()}
        # Extract field names to avoid extra keys in the dictionary
        class_fields = {f.name for f in fields(cls)}
        input_keys = set(cleaned_fieldnames.keys())
        filtered_data = {
            k: v for k, v in cleaned_fieldnames.items() if k in class_fields
        }

        extra_fields = input_keys - class_fields

        return MappingResults(mapping=cls(**filtered_data), dropped=extra_fields)

    def writerow(self, writer: DictWriter):
        writer.writerow(vars(self))


def add_arguments(subparsers):
    local_parser = subparsers.add_parser(__name__, help=__description__)

    local_parser.add_argument(
        "mappings",
        type=None,
        help="CSV file to be written to. Leave blank to write to stdout",
    )
    local_parser.add_argument(
        "--replace",
        action="store_true",
        help="When writing to file, --replace will replace any existing content. Otherwise, it will be merged in along with the existing values",
    )
    local_parser.add_argument(
        "-s",
        "--study-id",
        type=str,
        action="append",
        default=[],
        help="Pull all harmony for one or more studies (you may add more than one of these arguments to a single run)",
    )
    local_parser.add_argument(
        "-dd",
        "--data-dictionary-id",
        type=str,
        default=[],
        action="append",
        help="Pull all harmony for one or more data dictionaries (you may add more than one of these arguments to a single run)",
    )
    local_parser.add_argument(
        "-t",
        "--table-id",
        type=str,
        default=[],
        action="append",
        help="Pull all harmony for one or more tables (you may add more than one of these arguments to a single run)",
    )

    local_parser.add_argument(
        "-f",
        "--format",
        choices=["Whistle", "FTD"],
        default="FTD",
        help="Column structure may vary based on the formatting choice.",
    )


def exec(args, locu):
    if not hasattr(args, "host") and args.md_url is None:
        logger.error(
            "You must provide either the API URL or a configured host to proceed"
        )
        if len(args.host_config["hosts"]) > 0:
            logger.error(
                f"Available hosts include: {', '.join(args.host_config['hosts'].keys())}"
            )
        sys.exit(1)

    study_ids = args.study_id
    table_ids = args.table_id
    dataformat = args.format

    export_harmony(
        locu,
        study_ids=study_ids,
        table_ids=table_ids,
        mapping_filename=args.mappings,
        format=dataformat,
        replacecontent=args.replace,
    )
