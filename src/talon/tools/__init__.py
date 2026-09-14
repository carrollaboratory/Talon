import importlib
from pathlib import Path
from typing import Any

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


def get_table_ids_for_dd(locu: Locu, dd_id, arglist: str | None = None) -> list[str]:
    endpoint = f"DataDictionary/{dd_id}"
    if arglist:
        endpoint += f"&{arglist}"

    table_ids = []
    ddcontent = locu.get(endpoint)

    for tableref in ddcontent["tables"]:
        table_ids.append(tableref["reference"].split("/")[-1])

    return table_ids


def pull_table_content(
    locu: Locu, table_id: str, arglist: str | None = None
) -> dict[str, Any]:

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
    study_ids: list[str] | None = None,
    dd_ids: list[str] | None = None,
    table_ids: list[str] | None = None,
    format: str = "FTD",
) -> list[dict]:
    """Return the harmony content in dict format"""
    arglist = [f"format={format}"]
    if study_ids:
        arglist.append(f"studies={','.join(study_ids)}")
    if table_ids:
        arglist.append(f"tables={','.join(table_ids)}")
    if dd_ids:
        arglist.append(f"datadictionaries={','.join(dd_ids)}")

    content = locu.get(f"harmony?{'&'.join(arglist)}")

    return content
