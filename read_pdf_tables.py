import tabula
import PyPDF2
import numpy

if __name__ == "__main__":
    file_name = "tests/fifty_pages.pdf"
    pdf_file = open("tests/fifty_pages.pdf", "rb")
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    number_of_pages = read_pdf.getNumPages()
    page = read_pdf.getPage(2)
    page_content = page.extractText()
    table_list = page_content.split('\n')
    l = numpy.array_split(table_list, len(table_list) / 4)
    a =1