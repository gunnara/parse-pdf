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
    TypeNo01 = re.compile(r"^(No:)\s{1,3}\d{1,4}\s{1,3}.*")
    TypeNo02 = re.compile(r"^(Log)\s{1,3}(text)")
    # TypeNo03 = re.compile('r^(Subsystem)\s{1,3}(name)')
    # TypeNo04 = re.compile('r^(Type)\s{1,6}\w*\s{1,6}(Timeout)')
    # TypeNo05 = re.compile('r^(Acknowledgement)\s{1,6}\w*\s{1,6}(Shutdown type)')
    # TypeNo06 = re.compile('r^(-)\s{1,2}(Allowed attempts|Allowed)\s{1,2}\S*\s{1,6}(-)\s{1,1}(Max time disconnect)')
    # TypeNo07 = re.compile('r^(-)\s{1,2}(Time window|Time)\s{1,2}\S*\s{1,6}(-)\s{1,1}(Max time eliminate)')
    # TypeNo08 = re.compile('r^(-)\s{1,2}(Stabilize period|Stabilize)\s{1,2}\S*\s{1,6}(Category)')
    # TypeNo09 = re.compile('r(?s)(?<=Criteria:\n).*?(?=No:\s{1,2})')
    line_number = -1
    pd_row = -1
    with open(name, "r") as error_file:
        for line in error_file:
            line_number += 1
            if len(line) > 5:

                match_no01 = re.search(TypeNo01, line)

                if match_no01 is not None:
                    pd_row += 1
                    string = match_no01.string
                    No_value = re.search("(?<=No:)\s+?\d*(?=\s+?\SupervisionID)", string)
                    df["No"][pd_row] =No_value.group().strip()
    a = 1


if __name__ == "__main__":
    file_name = "tests/fifty_pages_test_parseing.txt"
    parse_error_code_file(file_name)
