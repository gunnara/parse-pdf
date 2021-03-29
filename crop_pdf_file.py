from PyPDF2 import PdfFileWriter,PdfFileReader,PdfFileMerger

# Open basisfile as binary and create a output file.
input = PdfFileReader(open("docs/FeilListe.pdf", "rb"))
output = PdfFileWriter()

# Find number of pages in file.
numPages = input.getNumPages()
print("document has %s pages." % numPages)

# Crop every page.
for i in range(numPages):
    page = input.getPage(i)
    page.mediaBox.lowerLeft  = (20, 75)
    page.mediaBox.lowerRight = (575, 75)
    page.mediaBox.upperRight = (575, 735)
    page.mediaBox.upperLeft  = (20, 735)
    output.addPage(page)

# Write the cropped file to result folder.
with open("results/FeilListe_cropped.pdf", "wb") as out_f:
    output.write(out_f)

# Used to get dimension of pages, in order to determining cropping.
page = input.getPage(0)
print(page.cropBox.getLowerLeft())
print(page.cropBox.getLowerRight())
print(page.cropBox.getUpperLeft())
print(page.cropBox.getUpperRight())