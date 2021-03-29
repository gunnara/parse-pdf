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
    type_no_01 = re.compile(r"^(No:)\s{1,3}\S*\s{1,3}(SupervisionID)")
    type_no_02 = re.compile(r"^(Log)\s{1,3}(text)")
    type_no_03 = re.compile(r"^(Subsystem)\s{1,3}(name)")
    type_no_04 = re.compile(r"^(Type)\s{1,6}\w*\s{1,6}(Timeout)")
    type_no_05 = re.compile(
        r"^(Acknowledgement)\s{1,6}\S*\s{1,6}(Shutdown)\s{1,6}(type)"
    )
    type_no_06 = re.compile(
        r"^(-)\s{1,2}(Allowed attempts|Allowed)\s{1,2}\S*\s{1,6}(-)\s{1,1}(Max time disconnect)"
    )
    type_no_07 = re.compile(
        r"^(-)\s{1,2}(Time window|Time)\s*.*(-)\s{1,3}(Max)\s{1,3}(time)"
    )
    type_no_08 = re.compile(
        r"^(-)\s{1,2}(Stabilize period|Stabilize)\s{1,2}.*(Category)"
    )
    # TypeNo09 = re.compile('r(?s)(?<=Criteria:\n).*?(?=No:\s{1,2})')
    line_number = -1
    pd_row = -1

    with open(name, "r", encoding="utf-8-sig") as error_file:
        for line in error_file:
            line_number += 1
            match_no01 = re.search(type_no_01, line)
            match_no02 = re.search(type_no_02, line)
            match_no03 = re.search(type_no_03, line)
            match_no04 = re.search(type_no_04, line)
            match_no05 = re.search(type_no_05, line)
            match_no06 = re.search(type_no_06, line)
            match_no07 = re.search(type_no_07, line)
            match_no08 = re.search(type_no_08, line)

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
# TODO Get SupervisionID from next line.
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

            # Getting "Allowed attempts" and "Max time disconnect" values
            if match_no06 and row_no_update:
                df["Allowed attempts"][pd_row] = (
                    re.search(
                        r"(?<=- Allowed)yes|(?<=- Allowed attempts)\s{1,3}.*(?=-\s{1,3}Max)",
                        line,
                    )
                    .group(0)
                    .strip()
                )
                max_time_disconnect = (
                    re.search(r"(?<=disconnect).*", line)
                    .group(0)
                    .strip()
                    .replace("O", "0")
                )
                max_time_disconnect = max_time_disconnect.replace("Q", "")
                max_time_disconnect = max_time_disconnect.replace("’", "")
                df["Max time disconnect"][pd_row] = max_time_disconnect.strip()

            # Getting "Time window" and "Max time eliminate" values
            if match_no07 and row_no_update:
                a = 1
                time_window = (
                    re.search(
                        r"(?<=- Time)yes|(?<=- Time window)\s{1,3}.*(?=-\s{1,3}Max)",
                        line,
                    )
                    .group(0)
                    .strip()
                    .replace("O", "0")
                )
                time_window = time_window.replace("Q", "0")
                time_window = time_window.replace("’", "")
                df["Time window"][pd_row] = time_window.strip()

                max_time_eliminate = (
                    re.search(r"(?<=eliminate).*", line)
                    .group(0)
                    .strip()
                    .replace("O", "0")
                )
                max_time_eliminate = max_time_eliminate.replace("Q", "0")
                max_time_eliminate = max_time_eliminate.replace("’", "")
                df["Max time eliminate"][pd_row] = max_time_eliminate.strip()

            # Getting "Stabilize period" and "Category" values
            if match_no08 and row_no_update:
                a = 1
                stabilize_period = (
                    re.search(
                        r"(?<=- Stabilize)yes|(?<=- Stabilize period)\s{1,3}.*(?=Category)",
                        line,
                    )
                    .group(0)
                    .strip()
                    .replace("O", "0")
                )
                stabilize_period = stabilize_period.replace("Q", "0")
                stabilize_period = stabilize_period.replace("’", "")
                df["Stabilize period"][pd_row] = stabilize_period.strip()

                df["Category"][pd_row] = re.search(r"(?<=Category).*", line).group(0).strip()
                row_no_update = False

    a = 1


if __name__ == "__main__":
    file_name = "results/FeilListe_ocr_cropped.txt"
    parse_error_code_file(file_name)
