import pandas as pd
import re
import regex
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

    df = pd.DataFrame(columns=Column_Names, index=range(0, 2000))

    # Define regular expression for extracting data
    # invalid_01 = regex.compile(r"^(No:)\s{0,20}\w\s{1,3}(SupervisionID)\s{1,3}.*?(Name)\s{1,3}\S{1,}")


    type_no_01_00 = regex.compile(r"^(No:)\s{1,3}\S*\s{1,3}(SupervisionID)\s{1,3}.*?(Name)\s{1,3}\S{1,}")
    type_no_01_01 = regex.compile(r"^(No:)\s{1,3}\S*\s{1,3}(Supervision(ID|I|))\s{0,20}\n")
    type_no_02 = regex.compile(r"^(Log)\s{1,3}(text)")
    type_no_03 = regex.compile(r"^(Subsystem)\s{1,3}(name)")
    type_no_04 = regex.compile(r"^(Type)\s{1,6}\w*\s{1,6}(Timeout)")
    type_no_05 = regex.compile(
        r"^(Acknowledgement)\s{1,6}\S*\s{1,6}(Shutdown)\s{1,6}(type)"
    )
    type_no_06 = regex.compile(
        r"^(-)\s{1,2}(Allowed attempts|Allowed)\s{1,2}\S*\s{1,6}(-)\s{1,1}(Max time disconnect)"
    )
    type_no_07 = regex.compile(
        r"^(-)\s{1,2}(Time window|Time)\s*.*(-)\s{1,3}(Max)\s{1,3}(time)"
    )
    type_no_08 = regex.compile(
        r"^(-)\s{1,2}(Stabilize period|Stabilize)\s{1,2}.*(Category)"
    )
    # TypeNo09 = regex.compile('r(?s)(?<=Criteria:\n).*?(?=No:\s{1,2})')
    line_number = -1
    pd_row = -1

    with open(name, "r", encoding="utf-8-sig") as error_file:
        for line in error_file:
            line_number += 1
            match_no01_00 = regex.search(type_no_01_00, line)
            match_no01_01 = regex.search(type_no_01_01, line)
            match_no02 = regex.search(type_no_02, line)
            match_no03 = regex.search(type_no_03, line)
            match_no04 = regex.search(type_no_04, line)
            match_no05 = regex.search(type_no_05, line)
            match_no06 = regex.search(type_no_06, line)
            match_no07 = regex.search(type_no_07, line)
            match_no08 = regex.search(type_no_08, line)

            # Getting "No", "SupervisionID" and "Name" values when output is on correct format.
            if match_no01_00:
                row_no_update = True
                pd_row += 1
                # Extracting numeric "No:" from this line.
                no_value = regex.search(
                    r"(?<=No:)\s{1,3}\S*(?=\s{1,2}\SupervisionID)", line
                )
                df["No"][pd_row] = no_value.group(0).strip().replace("/", "")
                supervision_id = regex.search(
                    r"(?<=SupervisionID)\s{1,3}\S*(?=\s{1,2}(Name))", line
                )
                if not supervision_id:
                    id_no = get_supervision_id(name,line_number)
                else:
                    id_no = supervision_id.group(0).strip().replace("/", "")

                df["SupervisionID"][pd_row] = id_no

                no_name = regex.search(r"(?<=Name)\s{1,5}\S{1,50}", line).group(0).strip()
                pattern = "[" + "{[()]}" + "]"
                df["Name"][pd_row] = regex.sub(pattern, "", no_name)
            # Getting "No", "SupervisionID" and "Name" values when output is on warped format.
            elif match_no01_01:
                row_no_update = True
                pd_row += 1
                # Extracting numeric "No:" from this line.
                no_value = regex.search(
                    r"(?<=No:)\s{1,3}\S*(?=\s{1,2}\Supervision)", line
                )
                df["No"][pd_row] = no_value.group(0).strip().replace("/", "")
                id_no = get_supervision_id(name,line_number)
                df["SupervisionID"][pd_row] = id_no
                no_name = get_name(name,line_number+1).strip()
                df["Name"][pd_row] = no_name


            # Getting "Log text" value.
            if match_no02 and row_no_update:
                df["Log text"][pd_row] = (
                    regex.search(r"(?<=Log text).*", line).group(0).strip()
                )

            # Getting "Subsystem name" value
            if match_no03 and row_no_update:
                df["Subsystem name"][pd_row] = (
                    regex.search(r"(?<=name).*", line).group(0).strip()
                )
            # Getting "Type" and "Timeout" values
            if match_no04 and row_no_update:
                df["Type"][pd_row] = (
                    regex.search(r"(?<=Type)\s{1,3}\S*(?=\s{1,3}Timeout)", line)
                    .group(0)
                    .strip()
                )
                df["Timeout"][pd_row] = (
                    regex.search(r"(?<=Timeout).*", line).group(0).strip()
                )
            # Getting "Acknowledgement" and "Shutdown type" values
            if match_no05 and row_no_update:
                df["Acknowledgement"][pd_row] = (
                    regex.search(
                        r"(?<=Acknowledgement)\s{1,3}\S*(?=\s{1,3}Shutdown)", line
                    )
                    .group(0)
                    .strip()
                )
                df["Shutdown type"][pd_row] = regex.sub(
                    "stop[sS] [lL]ow|[sS][tT][oO][pP][sS]low",
                    "stopSlow",
                    regex.search(r"(" r"?<=type).*", line).group(0).strip(),
                )

            # Getting "Allowed attempts" and "Max time disconnect" values
            if match_no06 and row_no_update:
                match_01 = regex.search(r"(?<=- Allowed attempts).*(?=-\s{1,3}Max)",line)
                match_02 = regex.search(r"(?<=- Allowed).*(?=-\s{1,3}Max)", line)
                if match_01:
                    df["Allowed attempts"][pd_row] = match_01.group(0).strip()
                elif match_02:
                    df["Allowed attempts"][pd_row] = match_02.group(0).strip()

                max_time_disconnect = (
                    regex.search(r"(?<=disconnect).*", line)
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
                    regex.search(
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
                    regex.search(r"(?<=eliminate).*", line)
                    .group(0)
                    .strip()
                    .replace("O", "0")
                )
                max_time_eliminate = max_time_eliminate.replace("Q", "0")
                max_time_eliminate = max_time_eliminate.replace("’", "")
                df["Max time eliminate"][pd_row] = max_time_eliminate.strip()

            # Getting "Stabilize period" and "Category" values
            if match_no08 and row_no_update:
                test = line_number
                match_01 = regex.search(r"(?<=- Stabilize period).*(?=Category)",line)
                match_02 = regex.search(r"(?<=- Stabilize).*(?=Category)", line)
                match_03 = regex.search(r"((?<=-\s{1,3}Stabilize\s{0,3}\n??period\s{0,3}\n??).*\s{1,}(?=Category)",
                                        line,regex.MULTILINE)
                if match_01:
                    stabilize_period = match_01.group(0).strip()
                elif match_02:
                    stabilize_period = match_02.group(0).strip()
                stabilize_period = stabilize_period.replace("O", "0")
                stabilize_period = stabilize_period.replace("Q", "0")
                stabilize_period = stabilize_period.replace("’", "")
                df["Stabilize period"][pd_row] = stabilize_period

                df["Category"][pd_row] = regex.search(r"(?<=Category).*", line).group(0).strip()
                row_no_update = False

    a = 1

def get_supervision_id(name: str,line_no:int) -> str:

    # Clearing cache to ensure updated values are used.


    for k in range(2,6):
        line_str = linecache.getline(name, line_no+k)
        match = regex.search("\s{0,10}\d{1,4}\s{0,10}\n",line_str)
        end_match = regex.search("(Log text|Name)", line_str)
        if match:
            return match.group(0).strip()
        elif end_match:
            return "Not found"

    return "Not found"

def get_name(name: str,line_no:int) -> str:

    for k in range(2,6):
        line_str = linecache.getline(name, line_no+k)
        on_same_line = regex.search("(?<=^Name)\s{0,10}\S{1,}\s{0,10}", line_str)
        not_on_same_line = regex.search("^Name\s{1,10}(\r|\n)",line_str)

        if on_same_line:
            return on_same_line.group(0).strip()
        elif not_on_same_line:
            line_str = linecache.getline(name, line_no + k + 1)
            return regex.search("{0,10}\S*\s{0,10}", line_str).group(0).strip()

    return "Not found"



if __name__ == "__main__":
    file_name = "results/text_kopiert_fra_pdf.txt"
    parse_error_code_file(file_name)
