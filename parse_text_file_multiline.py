import itertools
import pandas as pd
import regex


# Make function to extract data from text-file.
def parse_error_code_whole_file(name: str) -> None:
    # Setting the version of regex to be used.
    regex.VERSION1 = True

    # Open the file, so that all text/sentences can be read at once.
    ifile = open(name, "r", encoding="utf8")
    text = ifile.read()
    ifile.close()

    # Creating the data-frame where data should be stored.
    Column_Names = [
        "Start",
        "End",
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

    # Finding the number of that starts with "No:"
    object_no = regex.findall(r"(?<=^No:\s{1,3})\d{1,4}", text, regex.MULTILINE)
    number_of_objects = len(object_no)

    # Setting the size of the data-frame which will hold the results.
    df = pd.DataFrame(columns=Column_Names, index=range(0, number_of_objects - 1))

    # Write id-numbers to pandas-dataframe.
    df["No"] = object_no[0:-1]

    # Finding start position for each object, so search can be matched to each ID.
    object_no = regex.finditer(r"^No:\s{1,3}\d{1,4}", text, regex.MULTILINE)

    # Storing the start and end position for each "No: ####" found in the file.
    # When multistring search return less then the number of objects, then a iterativ serach
    # referencing the start and end position is done, in order to place found data on correct object.
    idx = 0
    for iter_no in object_no:
        if idx < number_of_objects - 2:
            df["Start"][idx] = iter_no.start()
        if idx > 0 & idx < number_of_objects - 1:
            df["End"][idx - 1] = iter_no.start()
        idx += 1

    # Find the first line in each error-object. Due to some distortion in the text-layout
    # not everything is captured. Due to this, a modified of the text is done.
    # The modification will remove objects which not could be read properly.

    # Getting first line with information.
    line_01 = regex.findall(
        r"^No:\s{1,3}.*\n??.*\n??.*\n??.*\n??.*\n??.*\n??(?=\nLog text)",
        text,
        regex.MULTILINE,
    )

    if len(line_01) == number_of_objects - 1:
        # Extract "SupervisionID"
        df["SupervisionID"] = [
            regex.search(r"(?<=Supervision\n??I\n??D\n??\s{1,3})\d{1,5}", x).group(0)
            for x in line_01
        ]

        # Extract "Name"
        df["Name"] = [regex.search(r"(?<=Name\s{1,3}).*", x).group(0) for x in line_01]
    else:
        return

    # Reading the line that contains "Log text".
    line_02 = regex.findall(
        r"(?<=^Log\s{1,2}text\s{1,3}).*\n??.*\n??.*\n??.*\n??.*\n??.*\n??(?=\nSubsystem)",
        text,
        regex.MULTILINE,
    )
    if len(line_02) == number_of_objects - 1:
        df["Log text"] = line_02
    else:
        return

    # Reading the line that contains "Subsystem name".
    line_03 = regex.findall(
        r"(?<=^Subsystem\s{1,2}name\s{1,3}).*\n??.*\n??.*\n??.*\n??.*\n??.*\n??(?=\nType)",
        text,
        regex.MULTILINE,
    )
    if len(line_03) == number_of_objects - 1:
        df["Subsystem name"] = line_03
    else:
        return

    # Reading the line that contains "Type" and "Timeout".
    line_04 = regex.findall(r"^Type\s{1,2}.*Timeout.*(?=\n)", text, regex.MULTILINE)

    if len(line_04) == number_of_objects - 1:
        # Extract "Type"
        df["Type"] = [
            regex.search(r"(?<=Type\s{1,3}).*(?=\s{1,2}Timeout)", x).group(0)
            for x in line_04
        ]

        # Extract "Timeout"
        df["Timeout"] = [
            regex.search(r"(?<=Timeout\s{1,3}).*", x).group(0) for x in line_04
        ]
    else:
        return

    # TODO Read in Acknowledgement data, missing 8 values, must be read

    # Reading the line that contains "Allowed attempts" and "Max time disconnected".
    line_06 = regex.findall(
        r"^- Allowed.*\n??.*\n??.*\n??.*\n??.*(?=\n- Time)", text, regex.MULTILINE
    )
    if len(line_06) == number_of_objects - 1:
        # Extract "Allowed attempts"
        df["Allowed attempts"] = [
            regex.search(
                r"(?<=attempts\n??\s{0,2}).*(?=- Max)", x
            ).group(0).strip()
            for x in line_06
        ]
        # Extract "Max time disconnect"
        df["Max time disconnect"] = [
            regex.search(
                r"(?<=disconnect\s{1,3}).*", x
            ).group(0).strip()
            for x in line_06
        ]

    else:
        return

    # Reading the line that contains "Time window" and "Max time eliminate".
    line_07 = regex.findall(
        r"^- Time.*\n??.*\n??.*\n??.*\n??.*(?=\n- Stabilize)", text, regex.MULTILINE
    )

    if len(line_07) == number_of_objects - 1:
        # Extract "Time window"
        df["Time window"] = [
            regex.search(
                r"(?<=window\n??\s{0,2}).*(?=- Max)", x
            ).group(0).strip()
            for x in line_07
        ]
        # Extract "Max time eliminate"
        df["Max time eliminate"] = [
            regex.search(
                r"(?<=eliminate\s{1,3}).*", x
            ).group(0).strip()
            for x in line_07
        ]

    else:
        return

    # Reading the line that contains "Stabilize period" and "Category".
    line_08 = regex.findall(
        r"^- Stabilize.*\n??.*\n??.*\n??.*\n??.*(?=\nCriteria)", text, regex.MULTILINE
    )

    if len(line_08) == number_of_objects - 1:
        # Extract "Stabilize period"
        df["Stabilize period"] = [
            regex.search(
                r"(?<=period\n??\s{0,2}).*(?=Category)", x
            ).group(0).strip()
            for x in line_08
        ]
        # Extract "Category"
        df["Category"] = [
            regex.search(
                r"(?<=Category\s{1,3}).*", x
            ).group(0).strip()
            for x in line_08
        ]

    else:
        return





    a = 1
if __name__ == "__main__":
    file_name = "results/text_kopiert_fra_pdf.txt"
    parse_error_code_whole_file(file_name)
