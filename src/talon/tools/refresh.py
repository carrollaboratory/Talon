__name__ = "refresh"
__summary__ = "Curate mapping content for reuse"
__description__ = "Pull mapping contents from a MapDragon instance to curate a local copy of reusable mappings"

"""
This script allows for downloading content from Map Dragon for curation.
"""

import logging
import pdb
import shutil
import sys
from argparse import FileType
from csv import DictWriter
from dataclasses import dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Self, Set, TextIO

import pandas as pd
import xxhash
import yaml
from rich import print

from .. import Locu
from . import pull_harmony_content


def sync_mapping_with_audit(csv_path: str, web_data_list: list):
    csv_file = Path(csv_path)
    backup_root = csv_file.parent / "backup"
    # 1. Load data safely into memory
    if csv_file.exists():
        df_csv = pd.read_csv(csv_file, dtype=str)
    else:
        # Create empty structure if file is missing
        cols = [
            "source_text",
            "mapped_code",
            "mapped_display",
            "mapped_system",
            "mapping_relationship",
            "ignore",
        ]
        df_csv = pd.DataFrame(columns=cols)

    # 2. Standardize web data

    df_web = pd.DataFrame(web_data_list).astype(str)

    keys = ["source_text", "mapped_code"]
    # Fields where differences trigger a conflict report
    audit_fields = ["mapped_display", "mapped_system"]

    # 3. Detect Conflicts (Including ignored rows)
    # This finds where keys match but display or system differ
    overlap = pd.merge(df_csv, df_web, on=keys, suffixes=("_csv", "_web"))

    observed = set()
    conflict_report = []
    for field in audit_fields:
        mismatches = overlap[overlap[f"{field}_csv"] != overlap[f"{field}_web"]].copy()
        if not mismatches.empty:
            for _, row in mismatches.iterrows():
                # Not sure we need this, but we can add a flag to merge these together later
                line_data = {
                    "source_text": row["source_text"],
                    "mapped_code": row["mapped_code"],
                    "mapped_display": row["mapped_display_web"],
                    "mapped_system": row["mapped_system_web"],
                    "mapping_relationship": row["mapping_relationship"],
                    "ignore": row["ignore"],  # Keep original ignore
                }
                md_line = (
                    pd.DataFrame([line_data]).to_csv(index=False, header=False).strip()
                )

                conflict_entry = {
                    field: {
                        "CSV Value": row[f"{field}_csv"],
                        "MD Value": row[f"{field}_web"],
                        "MD Line": md_line,
                    }
                }

                details = yaml.dump(conflict_entry, sort_keys=True)
                hash = xxhash.xxh32(details)
                if hash not in observed:
                    conflict_report.append(conflict_entry)
                    observed.add(hash)

    # 4. Identify New Rows
    existing_keys = set(zip(df_csv["source_text"], df_csv["mapped_code"]))
    new_records = [
        r
        for r in web_data_list
        if (str(r.get("source_text")), str(r.get("mapped_code"))) not in existing_keys
    ]

    # 5. Prepare Final DataFrame
    if new_records:
        df_new = pd.DataFrame(new_records).astype(str)
        df_new["ignore"] = "False"
        final_df = pd.concat([df_csv, df_new], ignore_index=True)
    else:
        final_df = df_csv

    # 6. Commit Changes
    if csv_file.exists():
        backup_root.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_root / f"{csv_file.stem}_{ts}{csv_file.suffix}"

        # Safe copy: original remains until to_csv succeeds
        shutil.copy2(csv_file, backup_path)

    final_df.drop_duplicates().to_csv(
        csv_file,
        index=False,
        columns="source_text,mapped_code,mapped_display,mapped_system,mapping_relationship,ignore".split(
            ","
        ),
    )

    return {
        "new_rows_added": len(new_records),
        "conflicts_found": len(conflict_report),
        "detailed_conflicts": conflict_report,
    }


def refresh_dataset(
    locu: Locu,
    project_directory: str,
    study_ids: List[str] = [],
    dd_ids: List[str] = [],
    table_ids: List[str] = [],
):
    """Refresh the curated dataset with mappings from the specified sources"""

    harmony_content = pull_harmony_content(
        locu, study_ids=study_ids, dd_ids=dd_ids, table_ids=table_ids, format="FTD"
    )

    pdir = Path(project_directory)
    if not pdir.is_dir():
        if pdir.exists():
            raise NotADirectoryError(
                f"'{project_directory}' was found but must be a directory. "
            )
        else:
            pdir.mkdir(parents=True, exist_ok=True)

    base_dataset = pdir / "mappings.csv"
    sync_report = sync_mapping_with_audit(str(base_dataset), harmony_content)

    with open(pdir / "errors.yaml", "wt") as f:
        yaml.dump(
            sync_report,
            f,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            width=float("inf"),
        )

    print(f"""Rows Added: {sync_report["new_rows_added"]}
Confict Count: {sync_report["conflicts_found"]}""")


@dataclass
class MappingData:
    source_text: str
    mapped_code: str
    mapped_display: str
    mapped_system: str
    source_description: Optional[str] = None
    mapping_relationship: Optional[str] = None
    comment: Optional[str] = None
    ignore: Optional[bool] = None

    @classmethod
    def from_ftd(cls, data: Dict[str, str]) -> Self:
        """Extracts fields from the FTD formatted harmony export from MD"""

        return cls(
            source_text=data["source_text"],
            source_description=data.get("source_description"),
            mapped_code=data["mapped_code"],
            mapped_display=data["mapped_display"],
            mapped_system=data["mapped_system"],
            mapping_relationship=data.get("mapping_relationship"),
            comment=data.get("comment"),
        )

    @classmethod
    def from_whistle(cls, data: Dict[str, str]) -> Self:
        """Extracts fields from the FTD formatted harmony export from MD"""

        return cls(
            source_text=data["local code"],
            source_description=data.get("text"),
            mapped_code=data["code"],
            mapped_display=data["display"],
            mapped_system=data["code system"],
            mapping_relationship=data.get("mapping_relationship"),
            comment=data.get("comment"),
        )


def add_arguments(subparsers):
    local_parser = subparsers.add_parser(
        __name__, help=__summary__, description=__description__
    )

    local_parser.add_argument(
        "-p",
        "--project-dir",
        type=None,
        default="curated",
        help="Directory where the curated dataset file(s) will be found.",
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

    refresh_dataset(
        locu,
        project_directory=args.project_dir,
        study_ids=study_ids,
        table_ids=table_ids,
    )
