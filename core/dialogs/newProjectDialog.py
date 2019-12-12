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
        # initProject handle
        self.newProject = initProject()
        # init widgets
        self.locationEdit = None
        self.showDataFileEdit = None
        self.showScriptFileEdit = None
        # local variables
        self.projectName = None
        self.currentIndex = 0
        self.dataFiles = set()
        self.dataDirs = set()
        self.scriptFiles = set()
        self.plutoVariables = plutoVariables()
        self.projectLocation = self.plutoVariables.projectHome

        # add pages
        page1Widget = self.page1()
        self.layout.addWidget(page1Widget)
        page2Widget = self.page2()
        self.layout.addWidget(page2Widget)
        page3Widget = self.page3()
        self.layout.addWidget(page3Widget)
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
        locationButton = QPushButton('...', widget)
        locationButton.setFixedWidth(30)
        self.locationEdit.setText(self.plutoVariables.projectHome)
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

        self.showDataFileEdit = QTextEdit(widget)
        self.showDataFileEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.showDataFileEdit.setReadOnly(True)
        showDataFileLine = QHBoxLayout(None)
        showDataFileLine.addWidget(self.showDataFileEdit)
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

    def page3(self):
        widget = QWidget(self)
        pageLayout = QVBoxLayout(widget)

        addScriptFileButton = QPushButton('Add Files', widget)
        addScriptFileLine = QHBoxLayout(None)
        addScriptFileLine.addWidget(QLabel('Add Script Files:', widget))
        addScriptFileLine.addStretch(0)
        addScriptFileLine.addWidget(addScriptFileButton)
        addScriptFileLine.setAlignment(Qt.AlignLeft)
        addScriptFileLine.setContentsMargins(5, 10, 5, 0)
        pageLayout.addLayout(addScriptFileLine)

        self.showScriptFileEdit = QTextEdit(widget)
        self.showScriptFileEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.showScriptFileEdit.setReadOnly(True)
        showScriptFileLine = QHBoxLayout(None)
        showScriptFileLine.addWidget(self.showScriptFileEdit)
        showScriptFileLine.setAlignment(Qt.AlignLeft)
        showScriptFileLine.setContentsMargins(5, 5, 5, 5)
        pageLayout.addLayout(showScriptFileLine)

        line = QFrame()
        line.setFrameShape(QFrame.HLine | QFrame.Sunken)
        pageLayout.addWidget(line)

        nextButton = QPushButton('Next', widget)
        buttonLine = QHBoxLayout(None)
        buttonLine.addWidget(nextButton)
        buttonLine.setAlignment(Qt.AlignRight)
        buttonLine.setContentsMargins(5, 0, 5, 10)
        pageLayout.addLayout(buttonLine)

        addScriptFileButton.clicked.connect(self.onAddScriptFileButtonClicked)
        nextButton.clicked.connect(self.onNextButton3Clicked)
        return widget

    def finishPage(self):
        widget = QWidget(self)
        pageLayout = QVBoxLayout(widget)

        showInfoEdit = QTextEdit(widget)
        showInfoEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        showInfoEdit.setReadOnly(True)
        showInfoLine = QHBoxLayout(None)
        showInfoLine.addWidget(showInfoEdit)
        showInfoLine.setAlignment(Qt.AlignLeft)
        showInfoLine.setContentsMargins(5, 5, 5, 5)
        pageLayout.addLayout(showInfoLine)
        self.displayInfo(showInfoEdit)

        line = QFrame()
        line.setFrameShape(QFrame.HLine | QFrame.Sunken)
        pageLayout.addWidget(line)

        finishButton = QPushButton('Finish', widget)
        buttonLine = QHBoxLayout(None)
        buttonLine.addWidget(finishButton)
        buttonLine.setAlignment(Qt.AlignRight)
        buttonLine.setContentsMargins(5, 0, 5, 10)
        pageLayout.addLayout(buttonLine)

        finishButton.clicked.connect(self.onFinishButtonClicked)
        return widget

    def onProjectNameChanged(self, text):
        self.projectName = text
        if self.projectName:
            self.locationEdit.setText(self.projectLocation + '/' + self.projectName)
        else:
            self.locationEdit.setText(self.projectLocation)

    def onLocationButtonClicked(self):
        dialog = QFileDialog(self)
        new_location = dialog.getExistingDirectory(self, "Location", self.plutoVariables.projectHome,
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
            QMessageBox.warning(self, 'New Project', 'Please enter a project name',
                                QMessageBox.Ok)
            return
        if os.path.exists(path):
            r = QMessageBox.warning(self, 'New Project', 'This path is already existed, if still create project here?',
                                    QMessageBox.Yes | QMessageBox.No)
            if r == QMessageBox.Yes:
                print('yes')
            elif r == QMessageBox.No:
                print('No')
                GO = False
        if GO:
            self.currentIndex += 1
            self.layout.setCurrentIndex(self.currentIndex)

    def onNextButton2Clicked(self):
        if self.dataFiles or self.dataDirs:
            self.newProject.parseData(self.dataFiles, self.dataDirs)
        self.currentIndex += 1
        self.layout.setCurrentIndex(self.currentIndex)

    def onNextButton3Clicked(self):
        if self.scriptFiles:
            self.newProject.parseScript(self.scriptFiles)
        finishPageWidget = self.finishPage()
        self.layout.addWidget(finishPageWidget)
        self.currentIndex += 1
        self.layout.setCurrentIndex(self.currentIndex)

    def onAddDataFileButtonClicked(self):
        dialog = QFileDialog(self)
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        dataFiles, _ = dialog.getOpenFileNames(self, "Add Data Files", self.plutoVariables.projectHome,
                                               "Supported Data (*.ds *.csv);;"
                                               "Pluto Data (*.ds);; CSV Files (*.csv);; All Files (*.*)",
                                               options=options)
        self.dataFiles |= set(dataFiles)
        print(self.dataFiles)
        self.freshShowDataFileEdit()

    def onAddFolderButtonClicked(self):
        dialog = QFileDialog(self)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)

        dataDirs = dialog.getExistingDirectory(self, "Add Directory", self.plutoVariables.projectHome,
                                               QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        self.dataDirs.add(dataDirs)
        print(self.dataDirs)
        self.freshShowDataFileEdit()

        # file_view = dialog.findChild(QListView, 'listView')
        # if file_view:
        #     file_view.setSelectionMode(QAbstractItemView.MultiSelection)
        # f_tree_view = dialog.findChild(QTreeView)
        # if f_tree_view:
        #     f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
        #
        # if dialog.exec():
        #     paths = dialog.selectedFiles()

    def onAddScriptFileButtonClicked(self):
        dialog = QFileDialog(self)
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        scriptFiles, _ = dialog.getOpenFileNames(self, "Add Script Files", self.plutoVariables.projectHome,
                                                 "Supported Data (*.py *.sc);;"
                                                 "Script Data (*.sc);; Python Files (*.py);; All Files (*.*)",
                                                 options=options)
        self.scriptFiles |= set(scriptFiles)
        print(self.scriptFiles)
        self.freshShowScriptFileEdit()

    def freshShowDataFileEdit(self):
        # self.showDataFileEdit = QTextEdit(None)
        self.showDataFileEdit.setText('')
        if self.dataFiles:
            self.showDataFileEdit.append('Data Files: ')
            for f in self.dataFiles:
                self.showDataFileEdit.append(f)

        if self.dataDirs:
            self.showDataFileEdit.append('Data Dirs: ')
            for d in self.dataDirs:
                self.showDataFileEdit.append(d)

    def freshShowScriptFileEdit(self):
        # self.showDataFileEdit = QTextEdit(None)
        self.showScriptFileEdit.setText('')
        if self.scriptFiles:
            self.showScriptFileEdit.append('Script Files: ')
            for f in self.scriptFiles:
                self.showScriptFileEdit.append(f)

    def onFinishButtonClicked(self):
        self.newProject.initProject(os.path.join(self.projectLocation, self.projectName), self.projectName)
        self.accept()

    def displayInfo(self, showInfoEdit: QTextEdit):
        showInfoEdit.setText('')
        showInfoEdit.setLineWrapMode(QTextEdit.FixedColumnWidth)
        showInfoEdit.setLineWrapColumnOrWidth(130)
        showInfoEdit.setFontPointSize(10)
        showInfoEdit.append('Project Name: ' + self.projectName)
        showInfoEdit.append('Project Location: ' + self.projectLocation + '/' + self.projectName)
        showInfoEdit.append('-' * showInfoEdit.lineWrapColumnOrWidth())

        showInfoEdit.append('Data Files: ' + str(len(self.dataFiles)) + ' Files')
        for f in self.dataFiles:
            showInfoEdit.append(f)
        showInfoEdit.append('')
        showInfoEdit.append('Data Dirs: ' + str(len(self.dataDirs)) + ' Dirs')
        for d in self.dataDirs:
            showInfoEdit.append(d)

        showInfoEdit.append('-' * showInfoEdit.lineWrapColumnOrWidth())
        showInfoEdit.append('Scripts: ' + str(len(self.scriptFiles)) + ' Scripts')
        for s in self.scriptFiles:
            showInfoEdit.append(s)
