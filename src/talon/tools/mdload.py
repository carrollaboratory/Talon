__name__ = "reuse"
__summary__ = "Update an existing MapDragon table or data-dictionary with terms from the curated mappings."
__description__ = "Update an existing MapDragon table or data-dictionary with terms from the curated mappings."

import logging
import pdb
import sys
from argparse import FileType
from csv import DictReader
from dataclasses import dataclass
from typing import Any, Dict, List, NamedTuple, Optional, Set, TextIO

import duckdb
import requests
from rich import print
from rich_argparse import RichHelpFormatter

from .. import Locu
from . import pull_table_content


@dataclass
class LoadableMapping:
    source_variable: str
    code: str
    display: str
    system: str
    table_id: str

    source_enumeration: Optional[str] = None
    mapping_relationship: Optional[str] = None
    provenance: Optional[str] = None
    comment: Optional[str] = None

    @classmethod
    def header(cls):
        return [
            "source_variable",
            "source_enumeration",
            "code",
            "display",
            "system",
            "provenance",
            "comment",
            "table_id",
            "mapping_relationship",
        ]

    def row(self):
        return [
            self.source_value,
            self.source_enumeration,
            self.code,
            self.display,
            self.system,
            self.provenance,
            self.comment,
            self.table_id,
            self.mapping_relationship,
        ]


class MappingLookup:
    def __init__(self, mapping_filename: str, case_insensitive: bool = True):
        self.filename = mapping_filename
        self.case_insensitive = case_insensitive
        self.db = None

        self.load_mappings()

    def load_mappings(self):
        self.db = duckdb.connect(database=":memory:")
        self.db.execute(
            f"CREATE TABLE data AS SELECT * FROM read_csv_auto('{self.filename}')"
        )

        if self.case_insensitive:
            self.db.execute(
                "ALTER TABLE data ALTER source_text SET DATA TYPE VARCHAR COLLATE NOCASE"
            )
        return self.db.execute("CREATE INDEX idx_source_text ON data (source_text)")

    def get_mappings_levenshtein(
        self, terms: List[str], max_distance: int = 2
    ) -> duckdb.DuckDBPyConnection:
        query = """
        WITH search_terms AS (SELECT unnest(?) AS term)
        SELECT data.*, levenshtein(data.source_text, s.term) as distance
        FROM data, search_terms s
        WHERE levenshtein(data.source_text, s.term) <= ?
        ORDER BY distance ASC
        """

        return self.db.execute(query, [terms, max_distance])

    def get_mappings_jw(
        self, terms: List[str], min_similarity: float
    ) -> duckdb.DuckDBPyConnection:
        query = """
        WITH search_terms AS (SELECT unnest(?) AS term)
        SELECT
            data.*,
            jaro_winkler_similarity(data.source_text, s.term) as score
        FROM data, search_terms s
        WHERE jaro_winkler_similarity(data.source_text, s.term) >= ?
        ORDER BY score DESC
            """

        return self.db.execute(query, [terms, min_similarity])

    def get_mappings_basic(
        self, terms: List[str], nocase: bool = True
    ) -> duckdb.DuckDBPyConnection:

        if nocase:
            lowered = [t.lower() for t in terms]
        else:
            lowered = terms

        return self.db.execute(
            "SELECT * FROM data WHERE source_text in ?", parameters=[lowered]
        )

    def get_mappings(
        self,
        terms: List[str],
        nocase: bool = True,
        fuzzy: str | None = None,
        fuzzy_threshold: str | None = None,
    ) -> Dict[str, Any]:
        """Accept one or more terms and return any matching, possibly without case sensitivity"""

        if fuzzy:
            if fuzzy == "Levenshtein":
                cur = self.get_mappings_levenshtein(terms, fuzzy_threshold)
            elif fuzzy == "Jaro–Winkler":
                cur = self.get_mappings_jw(terms, fuzzy_threshold)
        else:
            cur = self.get_mappings_basic(terms, nocase)

        columns = [desc[0] for desc in cur.description]

        return [dict(zip(columns, row)) for row in cur.fetchall()]


def ReuseMappings(
    locu: Locu,
    table_id: str,
    csvfile: TextIO,
    fuzzy: str | None = None,
    fuzzy_threshold: str | None = None,
) -> Dict[str, Any]:
    mappings = MappingLookup(csvfile.name)

    table = pull_table_content(locu, table_id=table_id)

    for variable in table["variables"]:
        matches = mappings.get_mappings(
            list(set([variable["name"], variable["code"]])),
            fuzzy=fuzzy,
            fuzzy_threshold=fuzzy_threshold,
        )

        print(matches)
        if variable["data_type"] == "ENUMERATION":
            for enum in variable["codes"]:
                search_terms = []
                if enum["code"] != "":
                    search_terms.append(enum["code"])
                if enum["display"]:
                    search_terms.append(enum["display"])

                matches = mappings.get_mappings(
                    list(set(search_terms)),
                    fuzzy=fuzzy,
                    fuzzy_threshold=fuzzy_threshold,
                )
                print(matches)
                pdb.set_trace()
    print(response)


def add_arguments(subparsers):
    local_parser = subparsers.add_parser(
        __name__,
        help=__summary__,
        description=__description__,
        formatter_class=RichHelpFormatter,
        epilog="Update either a [blue]single[/blue] table or an entire data dictionary with terms from the curated mappings file. ❗[yellow]Please note you should provide only one or the other for a single run.[/yellow]❗",
    )
    local_parser.add_argument(
        "mappings",
        type=FileType("rt"),
        help="CSV file containing the curated list of mappings",
    )
    local_parser.add_argument(
        "-dd",
        "--data-dictionary-id",
        type=str,
        help="Data dictionary ID whose tables should be updated",
    )
    local_parser.add_argument(
        "-t",
        "--table-id",
        type=str,
        help="Table ID whose tables should be updated",
    )
    local_parser.add_argument(
        "--fuzzy",
        choices=["Levenshtein", "Jaro–Winkler"],
        help="Optionally use fuzzy matching. When matching with one of these, you can also provide a threshold. Each will have a default (see docs for more details)",
    )
    local_parser.add_argument(
        "--fuzzy-threshold",
        type=float,
        default=None,
        help="Threshold used in identifying matches when using one of the similarity metrics. See docs for details and defaults.",
    )
    local_parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        default=False,
        help="When matching the **source_text** to a table's **variable name** or **enumerated value**, allow matches even if there is a difference in case.",
    )


def exec(args, locu):
    if args.table_id is not None and args.data_dictionary_id is not None:
        logging.error(
            f"You must provide either a single [blue]Table ID[/blue] or a single [blue]Data Dictionary ID[/blue]. Not both."
        )
        sys.exit(1)

    fuzzy = None
    fuzzy_threshold = None
    if args.fuzzy:
        fuzzy = args.fuzzy
        fuzzy_threshold = args.fuzzy_threshold

        if fuzzy_threshold is None:
            if fuzzy == "Levenshtein":
                fuzzy_threshold = 2
            elif fuzzy == "Jaro–Winkler":
                fuzzy_threshold = 0.9

    ReuseMappings(
        locu,
        table_id=args.table_id,
        csvfile=args.mappings,
        fuzzy=fuzzy,
        fuzzy_threshold=fuzzy_threshold,
    )
