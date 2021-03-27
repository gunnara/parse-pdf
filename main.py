import os
import ocrmypdf
import pdfplumber
import pandas as pd
import re
from collections import namedtuple

def parse_error_code_file(name:str) -> None:


    # Line = namedtuple('Line','No Subsystem Type Acknowledgement Allowed TimeWindow Stabilize TimeOut Shoutdown '
    #                          'MaxTime MinTime Category')
    #
    # # Define regular expression for each line which should be read.
    # No_line = re.compile('r^(No: )\d{1,4}')
    # Subsystem_line = re.compile('r^(Subsystem name)')
    # Type_line = re.compile('r^(Type  )')
    # Acknow = re.compile('r^(Acknowledgement)')
    # AllowAtt = re.compile('r^(- Allowed attempts)')
    # TimeWind = re.compile('r^(- Time window)')
    # StabPer = re.compile('r^(- Stabilize period)')
    # Criteria = re.compile('r^(Criteria:)')
    #
    # lines= []


    # Leser pdf-filen
    with pdfplumber.open(name) as pdf:
        pages = pdf.pages
    for page in pdf.pages:
        text = page.extract_text()
        a = 1
        # for line in text.split('\n'):
        #     if No_line.search(line):
        #         print("test1")
        #     if Subsystem_line.search(line):
        #         print("test2")
                # if Type_line.search(line):
                #     print("test3")
                # if Acknow.search(line):
                #     print("test4")
                # if AllowAtt.search(line):
                #     print("test5")
                # if TimeWind.search(line):
                #     print("test6")
                # if    StabPer.search(line):
                #     print("test7")
                # if Criteria.search(line):
                #     print("test8")



if __name__ == '__main__':
    file_name = 'tests/TestFil.pdf'
    os.system('ocrmypdf --force-ocr --sidecar output.txt TestFil.pdf OutPut.pdf')
    # parse_error_code_file('OutPut.pdf')


