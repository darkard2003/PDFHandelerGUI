import os
from PyPDF2 import PdfMerger
from datetime import datetime


def compressPdf(inputFile: str, outputFile: str):
    inputFile = f'"{inputFile}"'
    outputFile = f'"{outputFile}"'

    command = (
        "gswin64c.exe "
        "-sDEVICE=pdfwrite "
        "-dCompatibilityLevel=1.4 "
        "-dPDFSETTINGS=/screen "
        "-dNOPAUSE "
        "-dBATCH "
        f"-sOutputFile={outputFile} "
        f"{inputFile} "
    )

    os.system(command)



def mergePdf(filenames, outputdir: str) -> str:
    merger = PdfMerger()
    for file in filenames:
        merger.append(file)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    outFilename = f"Merged_{timestamp}.pdf"
    outFilePath = os.path.join(outputdir, outFilename)
    merger.write(outFilePath)
    merger.close()

    return outFilename
