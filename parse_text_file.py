import pandas as pd
import re
import linecache
import codecs
from collections import namedtuple


def parse_error_code_file(name: str) -> None:

    Column_Names = [
        "No",
        "SupervisionID",
        "Name",
        "Log text",
        "Subsystem name",
        "Type",
        "Timeout",
        "Acknowledgement",
        "Shutdown type",
        "Allowed attempts",
        "Max time disconnect",
        "Time window",
        "Max time eliminate",
        "Stabilize period",
        "Category",
        "Criteria",
    ]

    df = pd.DataFrame(columns=Column_Names, index=range(0, 1000))

    # Define regular expression for extracting data
    TypeNo01 = re.compile(r"^(No:)\s{1,3}\S*\s{1,3}(SupervisionID)")
    TypeNo02 = re.compile(r"^(Log)\s{1,3}(text)")
    TypeNo03 = re.compile(r"^(Subsystem)\s{1,3}(name)")
    TypeNo04 = re.compile(r"^(Type)\s{1,6}\w*\s{1,6}(Timeout)")
    TypeNo05 = re.compile(r"^(Acknowledgement)\s{1,6}\S*\s{1,6}(Shutdown)\s{1,6}(type)")
    TypeNo06 = re.compile(r'^(-)\s{1,2}(Allowed attempts|Allowed)\s{1,2}\S*\s{1,6}(-)\s{1,1}(Max time disconnect)')
    # TypeNo07 = re.compile('r^(-)\s{1,2}(Time window|Time)\s{1,2}\S*\s{1,6}(-)\s{1,1}(Max time eliminate)')
    # TypeNo08 = re.compile('r^(-)\s{1,2}(Stabilize period|Stabilize)\s{1,2}\S*\s{1,6}(Category)')
    # TypeNo09 = re.compile('r(?s)(?<=Criteria:\n).*?(?=No:\s{1,2})')
    line_number = -1
    pd_row = -1
    # (?<=No:\s{1,2})\S*(?=\s{1,2}\SupervisionID)

    with open(name, "r", encoding="utf-8-sig") as error_file:
        for line in error_file:
            line_number += 1
            match_no01 = re.search(TypeNo01, line)
            match_no02 = re.search(TypeNo02, line)
            match_no03 = re.search(TypeNo03, line)
            match_no04 = re.search(TypeNo04, line)
            match_no05 = re.search(TypeNo05, line)
            match_no06 = re.search(TypeNo05, line)

            # Getting "No", "SupervisionID" and "Name" values.
            if match_no01:
                row_no_update = True
                pd_row += 1
                # Extracting numeric "No:" from this line.
                no_value = re.search(
                    r"(?<=No:)\s{1,3}\S*(?=\s{1,2}\SupervisionID)", line
                )
                df["No"][pd_row] = no_value.group(0).strip().replace("/", "")
                supervision_id = re.search(
                    r"(?<=SupervisionID)\s{1,3}\S*(?=\s{1,2}(Name))", line
                )
                df["SupervisionID"][pd_row] = (
                    supervision_id.group(0).strip().replace("/", "")
                )
                no_name = re.search(r"(?<=Name)\s{1,5}\S{1,50}", line).group(0).strip()
                pattern = "[" + "{[()]}" + "]"
                df["Name"][pd_row] = re.sub(pattern, "", no_name)

            # Getting "Log text" value.
            if match_no02 and row_no_update:
                df["Log text"][pd_row] = (
                    re.search(r"(?<=Log text).*", line).group(0).strip()
                )

            # Getting "Subsystem name" value
            if match_no03 and row_no_update:
                df["Subsystem name"][pd_row] = (
                    re.search(r"(?<=name).*", line).group(0).strip()
                )

            # Getting "Type" and "Timeout" values
            if match_no04 and row_no_update:
                df["Type"][pd_row] = (
                    re.search(r"(?<=Type)\s{1,3}\S*(?=\s{1,3}Timeout)", line)
                    .group(0)
                    .strip()
                )
                df["Timeout"][pd_row] = (
                    re.search(r"(?<=Timeout).*", line).group(0).strip()
                )

            # Getting "Acknowledgement" and "Shutdown type" values
            if match_no05 and row_no_update:
                df["Acknowledgement"][pd_row] = (
                    re.search(
                        r"(?<=Acknowledgement)\s{1,3}\S*(?=\s{1,3}Shutdown)", line
                    )
                    .group(0)
                    .strip()
                )
                df["Shutdown type"][pd_row] = re.sub(
                    "stop[sS] [lL]ow|[sS][tT][oO][pP][sS]low",
                    "stopSlow",
                    re.search(r"(" r"?<=type).*", line).group(0).strip(),
                )
                # df["Shutdown type"][pd_row] = re.search(r"(?<=type).*", line).group(0).strip()
                row_no_update = False

    a = 1


if __name__ == "__main__":
    file_name = "tests/fifty_pages_ocr_error_list_cropped.txt"
    parse_error_code_file(file_name)
