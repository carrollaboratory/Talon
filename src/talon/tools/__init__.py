import importlib
import pdb
import sys
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Set, TextIO

from rich import print

from .. import Locu

# First, let's collect all of our tools so that we can add them to our kit

# The root dir is the current module directory where we will have one or
# more tools that we can execute.
rootdir = Path(__file__).absolute().parent / ".."


def load_tools():
    tools = {}

    # Anything inside the tools directory that starts with a letter is going
    # to be recognized as a tool, so don't put anything in there named like
    # a tool that doesn't exhibit the tool interface.
    for filename in Path(__file__).absolute().parent.glob("[A-Za-z]*.py"):
        toolname = filename.stem
        tool_lib = importlib.import_module(f"talon.tools.{toolname}")
        tools[tool_lib.__name__] = tool_lib
    return tools


def pull_table_content(
    locu: Locu, table_id: str, arglist: str | None = None
) -> Dict[str, Any]:

    endpoint = f"Table/{table_id}"
    if arglist:
        endpoint += f"&{arglist}"

    table_content = locu.get(endpoint)

    # pdb.set_trace()
    for var in table_content["variables"]:
        if var["data_type"] == "ENUMERATION":
            termep = var["enumerations"]["reference"]
            term_data = locu.get(termep)
            var["codes"] = term_data["codes"]
    return table_content


def pull_harmony_content(
    locu: Locu,
    study_ids: List[str] = [],
    dd_ids: List[str] = [],
    table_ids: List[str] = [],
    format: str = "FTD",
) -> Dict[str, Any]:
    """Return the harmony content in dict format"""
    arglist = [f"format={format}"]
    if len(study_ids) > 0:
        arglist.append(f"studies={','.join(study_ids)}")
    if len(table_ids) > 0:
        arglist.append(f"tables={','.join(table_ids)}")
    if len(dd_ids) > 0:
        arglist.append(f"datadictionaries={','.join(dd_ids)}")

    return locu.get(f"harmony?{'&'.join(arglist)}")
