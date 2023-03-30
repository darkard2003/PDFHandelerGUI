import os
import sys
from PyQt5 import QtWidgets, uic, QtGui
from pdfHandeler import compressPdf, mergePdf


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi("./ui/mainUi.ui", self)
        self.setWindowIcon(QtGui.QIcon('./resources/icon.png'))

        self.pdfs = {}
        self.compressedPdfs = {}
        self.mergedPdfs = {}

        self.setDefaultFolders()
        self.connectButtons()
        self.validateDirs()

    def connectButtons(self):
        self.removeButton.clicked.connect(self.removeItem)
        self.removeAllButton.clicked.connect(self.removeAll)
        self.addItemButton.clicked.connect(self.addItem)
        self.addFolderButton.clicked.connect(self.addFolder)
        self.mergePdfButton.clicked.connect(self.mergePdfAction)
        self.mergeCompressedButton.clicked.connect(self.mergeCompressedAction)
        self.mergeSelectedButton.clicked.connect(self.mergeSelectedAction)
        self.compressAllButton.clicked.connect(self.compressAll)
        self.compressSelectedButton.clicked.connect(self.compressSelected)

    def setDefaultFolders(self):
        self.defaultFiledialogOpenLocation = os.path.join(
            os.path.expanduser("~"),
            "Documents",
        )
        self.defaultSaveFolder = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "PDFHandeler",
        )
        self.defaultCompressedFolder = os.path.join(
            self.defaultSaveFolder,
            "Compressed",
        )
        self.defaultMergedFolder = os.path.join(
            self.defaultSaveFolder,
            "Merged",
        )

    def validateDirs(self):
        if not os.path.exists(self.defaultSaveFolder):
            os.mkdir(self.defaultSaveFolder)
        if not os.path.exists(self.defaultCompressedFolder):
            os.mkdir(self.defaultCompressedFolder)
        if not os.path.exists(self.defaultMergedFolder):
            os.mkdir(self.defaultMergedFolder)

    def removeItem(self):
        items = self.pdfListView.selectedItems()
        for item in items:
            row = self.pdfListView.row(item)
            self.pdfListView.takeItem(row)

        items = self.compressedListView.selectedItems()
        for item in items:
            row = self.compressedListView.row(item)
            self.compressedListView.takeItem(row)

        items = self.mergedListView.selectedItems()
        for item in items:
            row = self.mergedListView.row(item)
            self.mergedListView.takeItem(row)

    def removeAll(self):
        for _ in range(self.pdfListView.count()):
            self.pdfListView.takeItem(0)

        for _ in range(self.compressedListView.count()):
            self.compressedListView.takeItem(0)

        for _ in range(self.mergedListView.count()):
            self.mergedListView.takeItem(0)

    def addItem(self):
        res = QtWidgets.QFileDialog.getOpenFileNames(
            None,
            caption="Select PDFs",
            filter="PDF files (*.pdf)",
            directory=self.defaultFiledialogOpenLocation,
        )
        if not res:
            return

        filenames, _ = res
        for filename in filenames:
            basename = os.path.basename(filename)
            self.pdfs[basename] = filename
            self.pdfListView.addItem(basename)

    def addFolder(self):
        folderName = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            caption="Select Folder",
            directory=self.defaultFiledialogOpenLocation,
        )

        if not folderName:
            return

        items = os.listdir(folderName)

        for item in items:
            ext = os.path.splitext(item)[1]
            if ext != ".pdf":
                continue

            self.pdfs[item] = os.path.join(folderName, item)
            self.pdfListView.addItem(item)

    def mergePdfAction(self):
        items = [
            self.pdfs[self.pdfListView.item(row).text()]
            for row in range(self.pdfListView.count())
        ]
        if len(items) == 0:
            return
        mergedFilename = mergePdf(items, self.defaultMergedFolder)
        self.mergedListView.addItem(mergedFilename)
        self.mergedPdfs[mergedFilename] = os.path.join(
            self.defaultMergedFolder, mergedFilename
        )

    def mergeCompressedAction(self):
        items = [
            self.compressedPdfs[self.compressedListView.item(row).text()]
            for row in range(self.compressedListView.count())
        ]
        if len(items) == 0:
            return
        mergedFilename = mergePdf(items, self.defaultMergedFolder)
        self.mergedListView.addItem(mergedFilename)
        self.mergedPdfs[mergedFilename] = os.path.join(
            self.defaultMergedFolder, mergedFilename
        )

    def mergeSelectedAction(self):
        pdfSelected = [
            self.pdfs[item.text()] for item in self.pdfListView.selectedItems()
        ]

        compressedSelected = [
            self.compressedPdfs[item.text()]
            for item in self.compressedListView.selectedItems()
        ]

        mergedSelected = [
            self.mergedPdfs[item.text()] for item in self.mergedListView.selectedItems()
        ]

        allSelected = pdfSelected + compressedSelected + mergedSelected

        if len(allSelected) == 0:
            return

        mergedFilename = mergePdf(allSelected, self.defaultMergedFolder)
        self.mergedListView.addItem(mergedFilename)
        self.mergedPdfs[mergedFilename] = os.path.join(
            self.defaultMergedFolder, mergedFilename
        )

    def compressAll(self):
        inputFiles = [
            self.pdfListView.item(i).text() for i in range(self.pdfListView.count())
        ]

        for inputFile in inputFiles:
            inputFilePath = self.pdfs[inputFile]
            outputFilename = f"{os.path.splitext(inputFile)[0]}_compressed.pdf"
            outputFilePath = os.path.join(
                self.defaultCompressedFolder,
                outputFilename,
            )

            compressPdf(inputFilePath, outputFilePath)

            self.compressedPdfs[outputFilename] = outputFilePath
            self.compressedListView.addItem(outputFilename)

    def compressSelected(self):
        pdfSelected = [
            self.pdfs[item.text()] for item in self.pdfListView.selectedItems()
        ]

        compressedSelected = [
            self.compressedPdfs[item.text()]
            for item in self.compressedListView.selectedItems()
        ]

        mergedSelected = [
            self.mergedPdfs[item.text()] for item in self.mergedListView.selectedItems()
        ]

        allSelected = pdfSelected + compressedSelected + mergedSelected

        if len(allSelected) == 0:
            return

        for inputFile in allSelected:
            inputFileBaseName = os.path.basename(inputFile)
            outputFilename = f"{os.path.splitext(inputFileBaseName)[0]}_compressed.pdf"
            outputFilePath = os.path.join(
                self.defaultCompressedFolder,
                outputFilename,
            )

            compressPdf(inputFile, outputFilePath)

            self.compressedPdfs[outputFilename] = outputFilePath
            self.compressedListView.addItem(outputFilename)


app = QtWidgets.QApplication(sys.argv)

myWindow = MainWindow()
myWindow.show()
sys.exit(app.exec())
