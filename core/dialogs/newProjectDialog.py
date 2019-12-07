import os

from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot, QSize
from PyQt5.QtWidgets import QDialog, QWidget, QLineEdit, QPushButton, QLayout, QVBoxLayout, QHBoxLayout, QStackedLayout, \
    QStackedWidget, QLabel, QFrame, QFileDialog, QMessageBox

from PyQt5.QtGui import QResizeEvent, QIcon, QCursor
from PyQt5.uic import loadUi
from utls.yamlReader import initProject
from utls.setting import plutoDefaults

import warnings

warnings.filterwarnings('ignore')


class newProjectDialog(QDialog):
    # page 1: set project name
    # page 2: add file to data
    # finish
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QStackedLayout(self)
        self.setLayout(self.layout)
        self.setFixedSize(750, 500)
        self.setModal(True)
        self.newProject = None
        self.projectName = None
        self.locationEdit = None

        self.plutoDefault = plutoDefaults()
        self.projectLocation = self.plutoDefault.projectHome

        page1Widget = self.page1()
        self.layout.addWidget(page1Widget)
        self.setLayout(self.layout)

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
        locationButton = QPushButton('...', widget)
        locationButton.setFixedWidth(30)
        self.locationEdit.setText(self.plutoDefault.projectHome)
        locationLine = QHBoxLayout(None)
        locationLine.addWidget(QLabel('Location:', widget))
        locationLine.addWidget(self.locationEdit)
        locationLine.addWidget(locationButton)
        locationLine.setAlignment(Qt.AlignLeft)
        locationLine.setContentsMargins(5, 5, 5, 0)
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

        projectNameEdit.textChanged.connect(self.onProjectNameChanged)
        locationButton.clicked.connect(self.onLocationButtonClicked)
        nextButton.clicked.connect(self.onNextButtonClicked)
        return widget

    def onProjectNameChanged(self, text):
        self.projectName = text
        self.locationEdit.setText(self.projectLocation + '/' + self.projectName)

    def onLocationButtonClicked(self):
        dialog = QFileDialog(self)
        # dialog.setDirectory(self.plutoDefault.projectHome)
        new_location = dialog.getExistingDirectory(self, "Location", self.plutoDefault.projectHome,
                                                   QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if new_location:
            self.projectLocation = new_location
            if self.projectName:
                self.locationEdit.setText(self.projectLocation + '/' + self.projectName)
            else:
                self.locationEdit.setText(self.projectLocation)

    def onNextButtonClicked(self):
        if self.projectName:
            path = os.path.join(self.projectLocation, self.projectName)
        else:
            path = os.path.join(self.projectLocation)
        if os.path.exists(path):
            r = QMessageBox.warning(self, 'New Project', 'Duplicated Path, if overwrite',
                                    QMessageBox.Yes | QMessageBox.No)
            if r == QMessageBox.Yes:
                print('yes')
            elif r == QMessageBox.No:
                print('No')
