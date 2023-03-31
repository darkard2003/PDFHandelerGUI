import subprocess
import threading
import os
import sys
from typing import Literal
from PyQt5 import QtWidgets, uic, QtGui
from pdf import compressPdf, mergePdf


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi("./ui/mainUi.ui", self)

        self.resize(1650, 800)
        self.setWindowIcon(QtGui.QIcon("./resources/icon.ico"))

        self.pdfs = {}
        self.compressedPdfs = {}
        self.mergedPdfs = {}

        self.pdfListView.itemClicked.connect(self.onPdfItemClicked)
        self.compressedListView.itemClicked.connect(self.onCompressedItemClicked)
        self.mergedListView.itemClicked.connect(self.onMergedItemClicked)

        self.pdfListView.itemDoubleClicked.connect(self.onPdfItemClicked)
        self.compressedListView.itemDoubleClicked.connect(self.onCompressedItemClicked)
        self.mergedListView.itemDoubleClicked.connect(self.onMergedItemClicked)

        self.setDefaultFolders()
        self.connectButtons()
        self.validateDirs()

    def toggle_selection(
        self,
        listWidget: QtWidgets.QListWidget,
        btn: QtWidgets.QPushButton,
    ):
        selectedItems = listWidget.selectedItems()

        if len(selectedItems) == 0:
            listWidget.selectAll()
        else:
            listWidget.clearSelection()

        self.setButtonLabel(listWidget, btn)

    def setButtonLabel(
        self,
        listWidget: QtWidgets.QListWidget,
        btn: QtWidgets.QPushButton,
    ):
        selectedItems = listWidget.selectedItems()
        if len(selectedItems) == 0:
            btn.setText("Select All")
        else:
            btn.setText("Clear Selection")

    def updateButtonLabels(self):
        self.setButtonLabel(self.pdfListView, self.pdfListViewToggleSelection)
        self.setButtonLabel(
            self.compressedListView,
            self.compressedListViewToggleSelection,
        )
        self.setButtonLabel(
            self.mergedListView,
            self.mergedListViewToggleSelection,
        )

    def connectButtons(self):
        self.removeButton.clicked.connect(self.removeItem)
        self.addItemButton.clicked.connect(self.addItem)
        self.addFolderButton.clicked.connect(self.addFolder)
        self.mergeSelectedButton.clicked.connect(self.mergeSelectedAction)
        self.compressSelectedButton.clicked.connect(self.compressSelected)

        self.openCompressedFolder.clicked.connect(
            lambda: subprocess.run(
                [
                    "explorer",
                    self.defaultCompressedFolder,
                ]
            )
        )

        self.openMergedFolder.clicked.connect(
            lambda: subprocess.run(
                [
                    "explorer",
                    self.defaultMergedFolder,
                ]
            )
        )

        self.pdfListViewToggleSelection.clicked.connect(
            lambda: self.toggle_selection(
                self.pdfListView,
                self.pdfListViewToggleSelection,
            )
        )
        self.compressedListViewToggleSelection.clicked.connect(
            lambda: self.toggle_selection(
                self.compressedListView,
                self.compressedListViewToggleSelection,
            )
        )
        self.mergedListViewToggleSelection.clicked.connect(
            lambda: self.toggle_selection(
                self.mergedListView,
                self.mergedListViewToggleSelection,
            )
        )

    def onPdfItemClicked(self, item):
        self.setButtonLabel(
            self.pdfListView,
            self.pdfListViewToggleSelection,
        )
        self.onItemClicked(item)

    def onCompressedItemClicked(self, item):
        self.setButtonLabel(
            self.compressedListView,
            self.compressedListViewToggleSelection,
        )
        self.onItemClicked(item)

    def onMergedItemClicked(self, item):
        self.setButtonLabel(
            self.mergedListView,
            self.mergedListViewToggleSelection,
        )
        self.onItemClicked(item)

    def onItemClicked(self, item):
        pass

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
        self.updateButtonLabels()

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

        compressionLevel = self.compressionLevelSelector.currentText()
        print(compressionLevel)

        if len(allSelected) == 0:
            return

        compressionLevel = self.compressionLevelSelector.currentText()
        print(compressionLevel)

        t = threading.Thread(
            target=self.compress,
            args=(
                allSelected,
                compressionLevel,
            ),
        )
        t.start()

    def compress(
        self,
        inputFiles,
        compressionLevel: Literal[
            "default",
            "screen",
            "ebook",
            "printer",
            "prepress",
        ] = "default",
    ):
        for inputFile in inputFiles:
            inputFileBaseName = os.path.basename(inputFile)
            outputFilename = f"{os.path.splitext(inputFileBaseName)[0]}_compressed.pdf"
            outputFilePath = os.path.join(
                self.defaultCompressedFolder,
                outputFilename,
            )

            compressPdf(inputFile, outputFilePath, compressionLevel)

            self.compressedPdfs[outputFilename] = outputFilePath
            self.compressedListView.addItem(outputFilename)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    myWindow = MainWindow()
    myWindow.show()
    sys.exit(app.exec())
