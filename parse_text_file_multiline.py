import numpy as np
import pandas as pd
import regex


# Make function to extract data from text-file.
def parse_error_code_whole_file(name: str, name_cropped: str) -> None:
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
        if idx <= number_of_objects - 2:
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

    #  When using find all, number of objects found is the same as for number of ID e.g.
    # Hence since it's not possible to know which ID pairs with the found values. Due to
    # this the extent of data associated each ID is used for a iterativ search for those found.
    # The number's found is 1193, the total number is 1201, hence is 8 values missing.
    line_05 = regex.findall(
        r"^Acknowledgement\s{1,2}.*(?=\n- Allowed)", text, regex.MULTILINE
    )
    if len(line_05) == number_of_objects - 1:
        pass
    else:
        k_t_1 = 0
        for k in range(0, number_of_objects - 1):
            start_pos = df["Start"][k]
            end_pos = df["End"][k]

            iter_value = regex.search(
                r"^Acknowledgement\s{1,2}.*(?=\n- Allowed)",
                text,
                regex.MULTILINE,
                pos=start_pos,
                end_pos=end_pos,
            )
            if iter_value is not None:
                if k - k_t_1 <= 1:
                    k_t_1 = k
                else:
                    print(k)
                    k_t_1 = k

                df["Acknowledgement"][k] = (
                    regex.search(
                        r"(?<=Acknowledgement\n??\s{0,2}).*(?=Shutdown)",
                        iter_value.group().strip(),
                    )
                    .group()
                    .strip()
                )
                df["Shutdown type"][k] = (
                    regex.search(
                        r"(?<=type\n??\s{0,2}).*(?=s{0,2}\n??)",
                        iter_value.group().strip(),
                    )
                    .group()
                    .strip()
                )

    # Reading the line that contains "Allowed attempts" and "Max time disconnected".
    line_06 = regex.findall(
        r"^- Allowed.*\n??.*\n??.*\n??.*\n??.*(?=\n- Time)", text, regex.MULTILINE
    )
    if len(line_06) == number_of_objects - 1:
        # Extract "Allowed attempts"
        df["Allowed attempts"] = [
            regex.search(r"(?<=attempts\n??\s{0,2}).*(?=- Max)", x).group(0).strip()
            for x in line_06
        ]
        # Extract "Max time disconnect"
        df["Max time disconnect"] = [
            regex.search(r"(?<=disconnect\s{1,3}).*", x).group(0).strip()
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
            regex.search(r"(?<=window\n??\s{0,2}).*(?=- Max)", x).group(0).strip()
            for x in line_07
        ]
        # Extract "Max time eliminate"
        df["Max time eliminate"] = [
            regex.search(r"(?<=eliminate\s{1,3}).*", x).group(0).strip()
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
            regex.search(r"(?<=period\n??\s{0,2}).*(?=Category)", x).group(0).strip()
            for x in line_08
        ]
        # Extract "Category"
        df["Category"] = [
            regex.search(r"(?<=Category\s{1,3}).*", x).group(0).strip() for x in line_08
        ]

    else:
        return

    delta = np.subtract(np.array(df["End"][:-1]), np.array(df["Start"][1:]))
    if min(delta) != 0 or max(delta) != 0:
        print("Feil")

    # Due to the "text-noice" from header and footer, the cropped text-file is used to extract "Criteria" for each error.
    # Checking if start and end positions are unique.

    # Open the file, so that all text/sentences can be read at once.
    ifile = open(name_cropped, "r", encoding="utf8")
    text = ifile.read()
    ifile.close()

    # Creating the data-frame where data should be stored.
    Column_Names = ["Start", "End", "No", "Criteria"]

    # Finding the number of that starts with "No:"
    object_no = regex.findall(r"(?<=^No:\s{1,3})\d{1,4}", text, regex.MULTILINE)
    number_of_objects = len(object_no)

    # Setting the size of the data-frame which will hold the results.
    criteria_df = pd.DataFrame(
        columns=Column_Names, index=range(0, number_of_objects - 1)
    )

    # Write id-numbers to pandas-dataframe.
    criteria_df["No"] = object_no[0:-1]

    # Finding start position for each object, so search can be matched to each ID.
    object_no = regex.finditer(r"^No:\s{1,3}\d{1,4}", text, regex.MULTILINE)

    # Storing the start and end position for each "No: ####" found in the file.
    # When multistring search return less then the number of objects, then a iterativ serach
    # referencing the start and end position is done, in order to place found data on correct object.
    idx = 0
    for iter_no in object_no:
        if idx <= number_of_objects - 2:
            criteria_df["Start"][idx] = iter_no.start()
        if idx > 0 & idx < number_of_objects - 1:
            criteria_df["End"][idx - 1] = iter_no.start()
        idx += 1

    line_09 = regex.findall(
        r"Criteria:[\s\S]*?(?=\n??No:)",
        text,
        regex.MULTILINE,
    )
    for k in range(0,len(line_09)):
        df["Criteria"][k] = regex.sub("Criteria:","",line_09[k],count=1)

    df.to_excel("results/Error_List.xlsx",sheet_name="Error_Codes")


if __name__ == "__main__":
    file_name = "results/text_kopiert_fra_pdf.txt"
    file_name_cropped = "results/text_cropped_copied_from_pdf.txt"
    parse_error_code_whole_file(file_name, file_name_cropped)


