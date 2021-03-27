from PyPDF2 import PdfFileWriter,PdfFileReader,PdfFileMerger


input = PdfFileReader(open("docs/FeilListe.pdf", "rb"))
output = PdfFileWriter()

numPages = input.getNumPages()
print("document has %s pages." % numPages)

for i in range(numPages):
    page = input.getPage(i)
    page.mediaBox.lowerLeft  = (20, 50)
    page.mediaBox.lowerRight = (575, 50)
    page.mediaBox.upperRight = (575, 735)
    page.mediaBox.upperLeft  = (20, 735)
    output.addPage(page)

with open("results/error_list_cropped.pdf", "wb") as out_f:
    output.write(out_f)

# sdfsd
# page = input.getPage(0)
# print(page.cropBox.getLowerLeft())
# print(page.cropBox.getLowerRight())
# print(page.cropBox.getUpperLeft())
# print(page.cropBox.getUpperRight())