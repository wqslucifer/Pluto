import os
import sys
import time
import json

from PyQt5.QtCore import QUrl, QObject, pyqtSlot, QUrlQuery, QByteArray, Qt, QJsonDocument, \
    qDebug, pyqtSignal, QVariant, QEvent, QFile, QIODevice, QDir, QAbstractItemModel, QSize

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.Qt import QSplitter, QFrame

from PyQt5.QtGui import QResizeEvent, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtQuick import QQuickView
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.uic import loadUi

from core.customLayout import FlowLayout
from core.customWidget import ProjectWidget, CollapsibleTabWidget, RollingLabel

from utls.yamlReader import ProjectReader

import warnings

warnings.filterwarnings('ignore')

PROJECT_HOME = 'E:/project/Pluto/test'  # path to default project dirs
PROJECT_PATHS = ['E:/project/Pluto/test/testProject_1/project.pluto',
                 'E:/project/Pluto/test/testProject_2/project2.pluto']  # project paths that are added to pluto


class mainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)
        self.ui = loadUi('UI/mainFrame.ui', self)
        self.mainWidget = QWidget(self)
        self.mainWidgetLayout = QVBoxLayout(self.mainWidget)
        self.setCentralWidget(self.mainWidget)
        ###############################
        # local variables
        self.defaultDir = '.'
        self.curOpenProjectHandle = None
        ###############################
        # menu
        openProjectMenu = self.ui.actionOpen_Project
        openProjectMenu.triggered.connect(self.openProjectDialog)
        ###############################
        # init toolbar status bar
        self.toolBar = QToolBar(self)
        self.statusBar = QStatusBar(self)
        self.openAction = QAction(QIcon('res/Open.ico'), 'Open Project', self)
        ###############################
        # init widgets
        self.leftStage = QTabWidget(self)
        self.mainStage = QWidget(self)
        self.bottomStage = QWidget(self)
        self.bottomLayout = QHBoxLayout(self.bottomStage)
        self.bottomTabWidget = CollapsibleTabWidget(0, self)
        self.mainLayout = QStackedLayout(self.mainStage)
        ###############################
        # splitter
        self.vertical_splitter = QSplitter(Qt.Horizontal)
        self.horizontal_splitter = QSplitter(Qt.Vertical)
        ###############################
        # left stage
        self.leftTreeView = QTreeView(self)
        ###############################
        # bottom stage
        self.bottomOutputView = QTextEdit(self)
        ###############################
        # main stage
        self.scrollarea = QScrollArea(self)
        self.scrollbar = QScrollBar(self)
        self.projectList = QWidget(self.scrollarea)
        self.projectListLayout = FlowLayout()

        self.initUI()
        self.initToolBar()

    def initUI(self):
        self.mainStage.setLayout(self.mainLayout)
        # setup splitter
        self.vertical_splitter.addWidget(self.leftStage)
        self.vertical_splitter.addWidget(self.mainStage)
        self.vertical_splitter.setStretchFactor(1, 1)
        self.vertical_splitter.setCollapsible(0, False)
        self.vertical_splitter.setCollapsible(1, False)

        self.horizontal_splitter.addWidget(self.vertical_splitter)
        self.horizontal_splitter.addWidget(self.bottomStage)
        self.horizontal_splitter.setStretchFactor(1, 1)
        self.horizontal_splitter.setCollapsible(0, False)
        self.horizontal_splitter.setCollapsible(1, False)

        self.vertical_splitter.setSizes([self.width() * 0.22, self.width() * 0.78])
        self.horizontal_splitter.setSizes([self.height() * 0.78, self.height() * 0.22])

        self.mainWidgetLayout.addWidget(self.horizontal_splitter)
        self.bottomStage.setLayout(self.bottomLayout)
        self.bottomTabWidget.setSplitter(self.horizontal_splitter)
        self.bottomLayout.addWidget(self.bottomTabWidget)
        # setup left stage
        self.leftStage.setTabPosition(QTabWidget.West)
        self.leftStage.addTab(self.leftTreeView, 'File')

        # setup bottom stage
        # self.bottomStage.setTabPosition(QTabWidget.South)
        self.bottomTabWidget.addTab(self.bottomOutputView, 'Output')
        self.bottomLayout.setContentsMargins(20, 0, 0, 0)
        # init main stage
        self.initProjectList()

    def initToolBar(self):
        self.statusBar.setContentsMargins(10, 0, 0, 10)
        self.addToolBar(self.toolBar)
        self.setStatusBar(self.statusBar)
        # open
        self.openAction.setStatusTip('Open Project')
        self.openAction.triggered.connect(self.openProjectDialog)
        self.toolBar.addAction(self.openAction)

    def initProjectList(self):
        self.scrollarea.setWidgetResizable(True)
        self.projectList.setLayout(self.projectListLayout)
        self.scrollarea.setWidget(self.projectList)
        self.scrollarea.setVerticalScrollBar(self.scrollbar)
        self.scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.mainLayout.addWidget(self.scrollarea)

        # init projects from PROJECT_PATHS
        projectHandleList = []
        # projectItemList = []
        for projectPath in PROJECT_PATHS:
            projectHandle = ProjectReader(projectPath)
            projectHandleList.append(projectHandle)

            # projectName, projectLocation, lastOpenTime, projectFiles
            projectItem = ProjectWidget(projectHandle.projectName, projectHandle.projectPath, \
                                        projectHandle.lastAccessTime, projectHandle)
            projectItem.triggered.connect(self.openProject)
            self.projectListLayout.addWidget(projectItem)

    def openProject(self, ProjectReader):  # TODO
        print('open project:', ProjectReader.projectName)
        self.curOpenProjectHandle = ProjectReader

    def saveProject(self):  # TODO
        pass

    def changeProjectName(self):  # TODO
        pass

    def updateProjectLastAccessTime(self):  # TODO
        pass

    def addFileToProject(self):  # TODO
        pass

    def delFileFromProject(self):  # TODO
        pass

    def openProjectDialog(self):  #TODO
        dialog = QFileDialog(self)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dialog.setDirectory(self.defaultDir)
        projectFile, _ = dialog.getOpenFileName(self, "Open Project", "",
                                                "Project File (*.pluto);;All Files (*.*)", options=options)
        if projectFile:
            self.openProject(projectFile)
        else:
            raise Exception('Open project failed')
