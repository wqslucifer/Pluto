import os

from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot, QSize, QDir
from PyQt5.QtWidgets import QDialog, QWidget, QLineEdit, QPushButton, QLayout, QVBoxLayout, QHBoxLayout, QStackedLayout, \
    QStackedWidget, QLabel, QFrame, QFileDialog, QMessageBox, QTextEdit, QSizePolicy, QListView, QAbstractItemView, \
    QTreeView, QTableView, QHeaderView

from PyQt5.QtGui import QResizeEvent, QIcon, QCursor, QStandardItemModel, QStandardItem
from PyQt5.uic import loadUi
from utls.yamlReader import initProject
from utls.setting import plutoVariables

import warnings

warnings.filterwarnings('ignore')

"""
pluto dataset dialog
1. add data from dataSource and data describe
2. set cache flag
3. add process from scriptSource or skip
"""


class newPlutoDSDialog(QDialog):
    # pluto dataset wizard
    plutoDSInited = pyqtSignal(str)

    def __init__(self, projectHandle, parent=None):
        super().__init__(parent=parent)
        self.layout = QStackedLayout(self)
        self.setLayout(self.layout)
        self.setFixedSize(750, 500)
        self.setModal(True)
        # initProject handle
        self.projectHandle = projectHandle
        # init widgets
        self.locationEdit = None
        self.tableView = None
        self.tableModel = QStandardItemModel()

        # local variables
        self.plutoVariables = plutoVariables()
        self.projectLocation = self.plutoVariables.projectHome
        self.defaultDataLocation = self.projectHandle.projectPath + '\data'
        self.dsName = None
        self.dsLocation = self.defaultDataLocation
        self.currentIndex = 0

        # add pages
        page1Widget = self.page1()
        self.layout.addWidget(page1Widget)
        page2Widget = self.page2()
        self.layout.addWidget(page2Widget)
        # page3Widget = self.page3()
        # self.layout.addWidget(page3Widget)
        # finish page init when all info is collected
        self.setLayout(self.layout)
        self.layout.setCurrentIndex(1)

    def page1(self):
        widget = QWidget(self)
        pageLayout = QVBoxLayout(widget)
        DSNameEdit = QLineEdit(widget)
        nameLine = QHBoxLayout(None)
        nameLine.addWidget(QLabel('Name:', widget))
        nameLine.addSpacing(13)
        nameLine.addWidget(DSNameEdit)
        nameLine.setAlignment(Qt.AlignLeft)
        nameLine.setContentsMargins(5, 10, 5, 0)
        pageLayout.addLayout(nameLine)

        self.locationEdit = QLineEdit(widget)
        self.locationEdit.setText(QDir.cleanPath(self.defaultDataLocation))
        locationButton = QPushButton('Browser', widget)
        locationLine = QHBoxLayout(None)
        locationLine.addWidget(QLabel('Location:', widget))
        locationLine.addWidget(self.locationEdit)
        locationLine.addWidget(locationButton)
        pageLayout.addLayout(locationLine)

        pageLayout.addStretch(5)

        line = QFrame()
        line.setFrameShape(QFrame.HLine | QFrame.Sunken)
        pageLayout.addWidget(line)

        nextButton = QPushButton('Next', widget)
        buttonLine = QHBoxLayout(None)
        buttonLine.addWidget(nextButton)
        buttonLine.setAlignment(Qt.AlignRight)
        buttonLine.setContentsMargins(5, 0, 5, 10)
        pageLayout.addLayout(buttonLine)

        DSNameEdit.textChanged.connect(self.onDSNameChanged)
        locationButton.clicked.connect(self.onLocationButtonClicked)
        nextButton.clicked.connect(self.onNextButton1Clicked)
        return widget

    def page2(self):
        # load data from data source
        widget = QWidget(self)
        pageLayout = QVBoxLayout(widget)
        self.tableView = QTableView(widget)

        pageLayout.addWidget(self.tableView)
        self.tableModel.setHorizontalHeaderLabels(['File Name', 'Type', 'Location'])
        self.tableView.setModel(self.tableModel)
        self.tableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.loadDataSource()

        line = QFrame()
        line.setFrameShape(QFrame.HLine | QFrame.Sunken)
        pageLayout.addWidget(line)

        nextButton = QPushButton('Next', widget)
        buttonLine = QHBoxLayout(None)
        buttonLine.addWidget(nextButton)
        buttonLine.setAlignment(Qt.AlignRight)
        buttonLine.setContentsMargins(5, 0, 5, 10)
        pageLayout.addLayout(buttonLine)

        nextButton.clicked.connect(self.onNextButton2Clicked)
        return widget

    def onNextButton1Clicked(self):
        print(self.dsName, self.dsLocation)
        self.currentIndex += 1
        self.layout.setCurrentIndex(self.currentIndex)

    def onNextButton2Clicked(self):
        checkedList = self.getCheckedItem()
        print(checkedList)
        self.currentIndex += 1
        self.layout.setCurrentIndex(self.currentIndex)

    def onLocationButtonClicked(self):
        dialog = QFileDialog(self)
        new_location = dialog.getExistingDirectory(self, "Location", self.projectLocation,
                                                   QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if new_location:
            self.dsLocation = new_location
            self.locationEdit.setText(self.dsLocation)
        else:
            self.locationEdit.setText(self.defaultDataLocation)

    def onDSNameChanged(self, text):
        self.dsName = text

    def addRow(self, name, fileType, location):
        nameItem = QStandardItem(name)
        nameItem.setCheckable(True)
        nameItem.setCheckState(Qt.Unchecked)
        fileTypeItem = QStandardItem(fileType)
        locationItem = QStandardItem(location)
        self.tableModel.appendRow([nameItem, fileTypeItem, locationItem])

    def loadDataSource(self):
        dataHandle = self.projectHandle.dataSourceHandle
        csvFiles, imageDirs, plutoDataSets = dataHandle.getAllData()
        for code, location in {**csvFiles, **imageDirs, **plutoDataSets}.items():
            dataType = dataHandle.parseCode(code)
            name = QDir(location).dirName()
            self.addRow(name, dataType, location)

    def getCheckedItem(self):
        checkedList = []
        for r in range(self.tableModel.rowCount()):
            nameItem = self.tableModel.item(r, 0)
            typeItem = self.tableModel.item(r, 1)
            locationItem = self.tableModel.item(r, 2)
            if nameItem.checkState():
                name = nameItem.text()
                dataType = typeItem.text()
                location = locationItem.text()
                checkedList.append([name, dataType, location])
        return checkedList
