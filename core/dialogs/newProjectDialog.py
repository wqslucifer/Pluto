import os

from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot, QSize
from PyQt5.QtWidgets import QDialog, QWidget, QLineEdit, QPushButton, QLayout, QVBoxLayout, QHBoxLayout, QStackedLayout, \
    QStackedWidget, QLabel, QFrame, QFileDialog, QMessageBox, QTextEdit, QSizePolicy, QListView, QAbstractItemView, \
    QTreeView

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
        self.newProject = None  # initProject handle
        self.projectName = None
        self.locationEdit = None
        self.currentIndex = 0

        self.plutoDefault = plutoDefaults()
        self.projectLocation = self.plutoDefault.projectHome

        page1Widget = self.page1()
        self.layout.addWidget(page1Widget)
        self.setLayout(self.layout)

        page2Widget = self.page2()
        self.layout.addWidget(page2Widget)
        self.setLayout(self.layout)

        self.layout.setCurrentIndex(1)

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
        nextButton.clicked.connect(self.onNextButton1Clicked)
        return widget

    def page2(self):
        widget = QWidget(self)
        pageLayout = QVBoxLayout(widget)

        addFolderButton = QPushButton('Add Folders', widget)
        addDataFileButton = QPushButton('Add Files', widget)
        addDataFileLine = QHBoxLayout(None)
        addDataFileLine.addWidget(QLabel('Add Data Files:', widget))
        addDataFileLine.addStretch(0)
        addDataFileLine.addWidget(addFolderButton)
        addDataFileLine.addWidget(addDataFileButton)
        addDataFileLine.setAlignment(Qt.AlignLeft)
        addDataFileLine.setContentsMargins(5, 10, 5, 0)
        pageLayout.addLayout(addDataFileLine)

        showDataFileEdit = QTextEdit(widget)
        showDataFileEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        showDataFileEdit.setDisabled(True)
        showDataFileLine = QHBoxLayout(None)
        showDataFileLine.addWidget(showDataFileEdit)
        showDataFileLine.setAlignment(Qt.AlignLeft)
        showDataFileLine.setContentsMargins(5, 5, 5, 5)
        pageLayout.addLayout(showDataFileLine)

        line = QFrame()
        line.setFrameShape(QFrame.HLine | QFrame.Sunken)
        pageLayout.addWidget(line)

        nextButton = QPushButton('Next', widget)
        buttonLine = QHBoxLayout(None)
        buttonLine.addWidget(nextButton)
        buttonLine.setAlignment(Qt.AlignRight)
        buttonLine.setContentsMargins(5, 0, 5, 10)
        pageLayout.addLayout(buttonLine)

        addFolderButton.clicked.connect(self.onAddFolderButtonClicked)
        addDataFileButton.clicked.connect(self.onAddDataFileButtonClicked)
        nextButton.clicked.connect(self.onNextButton2Clicked)
        return widget

    def onProjectNameChanged(self, text):
        self.projectName = text
        if self.projectName:
            self.locationEdit.setText(self.projectLocation + '/' + self.projectName + '.pluto')
        else:
            self.locationEdit.setText(self.projectLocation)

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

    def onNextButton1Clicked(self):
        GO = True
        if self.projectName:
            path = os.path.join(self.projectLocation, self.projectName)
        else:
            path = os.path.join(self.projectLocation)
        if os.path.exists(path):
            r = QMessageBox.warning(self, 'New Project', 'This path is already existed, if still create project here?',
                                    QMessageBox.Yes | QMessageBox.No)
            if r == QMessageBox.Yes:
                print('yes')
            elif r == QMessageBox.No:
                print('No')
                GO = False
        if GO:
            self.newProject = initProject(path, self.projectName)
            self.currentIndex += 1
            self.layout.setCurrentIndex(self.currentIndex)

    def onNextButton2Clicked(self):
        pass

    def onAddDataFileButtonClicked(self):
        dialog = QFileDialog(self)
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        dataFiles, _ = dialog.getOpenFileNames(self, "Add Data Files", "", "Supported Data (*.ds, *.csv)"
                                                                           "Pluto Data (*.ds);; CSV Files (*.csv);; All Files (*.*)",
                                               options=options)
        print(dataFiles)

    def onAddFolderButtonClicked(self):
        dialog = QFileDialog(self)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)

        dataDirs = dialog.getExistingDirectory(self, "Add Directory", "",
                                               QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        print(dataDirs)

        # file_view = dialog.findChild(QListView, 'listView')
        # if file_view:
        #     file_view.setSelectionMode(QAbstractItemView.MultiSelection)
        # f_tree_view = dialog.findChild(QTreeView)
        # if f_tree_view:
        #     f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
        #
        # if dialog.exec():
        #     paths = dialog.selectedFiles()
