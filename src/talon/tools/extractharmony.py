__name__ = "extract-harmony"
__description__ = "Pull harmony content from MapDragon API"


import logging
import sys
from argparse import FileType
from csv import DictWriter
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Set, TextIO

from .. import Locu


def export_harmony(
    locu: Locu,
    mapping_filename: str,
    study_ids: List[str] = [],
    dd_ids: List[str] = [],
    table_ids: List[str] = [],
    format: str = "FTD",
    replacecontent: bool = False,
):

    if len(study_ids) + len(dd_ids) + len(table_ids) < 1:
        logging.error(
            "This requires at least one Study ID, Data Dictionary ID or Table ID to continue."
        )
        sys.exit(1)

    arglist = [f"format={format}"]
    if len(study_ids) > 0:
        arglist.append(f"studies={','.join(study_ids)}")
    if len(table_ids) > 0:
        arglist.append(f"tables={','.join(table_ids)}")
    if len(dd_ids) > 0:
        arglist.append(f"datadictionaries={','.join(dd_ids)}")

    harmony_content = locu.get(f"harmony?{'&'.join(arglist)}")
    mappings = [Mapping.from_dict(item) for item in harmony_content]

    if replacecontent:
        with Path(mapping_filename).open("wt") as outf:
            writer = DictWriter(outf, fieldnames=list(vars(mappings[0].mapping).keys()))
            writer.writeheader()

            for mapping in mappings:
                mapping.mapping.writerow(writer)


class MappingResults(NamedTuple):
    mapping: "Mapping"
    dropped: Set[str]


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
    study_title: Optional[str] = None
    study_name: Optional[str] = None
    study_id: Optional[str] = None
    dd_name: Optional[str] = None
    dd_id: Optional[str] = None
    version: Optional[str] = None
    source_description: Optional[str] = None
    source_domain: Optional[str] = None
    parent_varname: Optional[str] = None
    mapping_relationship: Optional[str] = None
    comment: Optional[str] = None

    ignore: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MappingResults:
        """Convert the basic dict into a Mapping"""

        cleaned_fieldnames = {k.replace(" ", "_"): v for k, v in data.items()}
        # Extract field names to avoid extra keys in the dictionary
        class_fields = {f.name for f in fields(cls)}
        input_keys = set(cleaned_fieldnames.keys())
        filtered_data = {
            k: v for k, v in cleaned_fieldnames.items() if k in class_fields
        }

        extra_fields = input_keys - class_fields

        print(data)
        print(filtered_data)
        return MappingResults(mapping=cls(**filtered_data), dropped=extra_fields)

    def writerow(self, writer: TextIO):
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
        logging.error(
            f"You must provide either the API URL or a configured host to proceed"
        )
        if len(args.host_config["hosts"]) > 0:
            logging.error(
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
