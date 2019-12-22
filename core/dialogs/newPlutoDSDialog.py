import os

from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot, QSize
from PyQt5.QtWidgets import QDialog, QWidget, QLineEdit, QPushButton, QLayout, QVBoxLayout, QHBoxLayout, QStackedLayout, \
    QStackedWidget, QLabel, QFrame, QFileDialog, QMessageBox, QTextEdit, QSizePolicy, QListView, QAbstractItemView, \
    QTreeView

from PyQt5.QtGui import QResizeEvent, QIcon, QCursor
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

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.layout = QStackedLayout(self)
        self.setLayout(self.layout)
        self.setFixedSize(750, 500)
        self.setModal(True)
        # initProject handle
        self.projectHandle = None
        # init widgets
        self.locationEdit = None
        # self.showDataFileEdit = None
        # self.showScriptFileEdit = None

        # local variables
        self.projectName = None
        self.currentIndex = 0
        self.plutoVariables = plutoVariables()
        self.projectLocation = self.plutoVariables.projectHome
        self.defaultDataLocation = self.projectLocation + '/data'

        # add pages
        page1Widget = self.page1()
        self.layout.addWidget(page1Widget)
        # page2Widget = self.page2()
        # self.layout.addWidget(page2Widget)
        # page3Widget = self.page3()
        # self.layout.addWidget(page3Widget)
        # finish page init when all info is collected
        self.setLayout(self.layout)
        self.layout.setCurrentIndex(0)

    def page1(self):
        widget = QWidget(self)
        pageLayout = QVBoxLayout(widget)
        projectNameEdit = QLineEdit(widget)
        nameLine = QHBoxLayout(None)
        nameLine.addWidget(QLabel('Name:', widget))
        nameLine.addSpacing(13)
        nameLine.addWidget(projectNameEdit)
        nameLine.setAlignment(Qt.AlignLeft)
        nameLine.setContentsMargins(5, 10, 5, 0)
        pageLayout.addLayout(nameLine)

        self.locationEdit = QLineEdit(widget)
        locationButton = QPushButton('Browser', widget)
        locationLine = QHBoxLayout(None)
        locationLine.addWidget(QLabel('Location:', widget))
        locationLine.addWidget(self.locationEdit)
        locationLine.addWidget(locationButton)

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

        locationButton.clicked.connect(self.onLocationButtonClicked)
        nextButton.clicked.connect(self.onNextButton1Clicked)
        return widget

    def onNextButton1Clicked(self):
        self.currentIndex += 1
        self.layout.setCurrentIndex(self.currentIndex)

    def onLocationButtonClicked(self):
        dialog = QFileDialog(self)
        new_location = dialog.getExistingDirectory(self, "Location", self.projectLocation,
                                                   QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if new_location:
            self.projectLocation = new_location
            if self.projectName:
                self.locationEdit.setText(self.projectLocation)
            else:
                self.locationEdit.setText(self.defaultDataLocation)
