import os
import sys
import time
import json
import gc

from functools import partial
from datetime import datetime, timezone, time

from PyQt5.QtCore import QUrl, QObject, pyqtSlot, QUrlQuery, QByteArray, Qt, QJsonDocument, \
    qDebug, pyqtSignal, QVariant, QEvent, QFile, QIODevice, QDir, QAbstractItemModel, QSize

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.Qt import QSplitter, QFrame
from PyQt5.QtGui import QResizeEvent, QIcon, QCursor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtQuick import QQuickView
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.uic import loadUi

from core.customLayout import FlowLayout
from core.customWidget import ProjectWidget, CollapsibleTabWidget, RollingLabel, ColorTabWidget
from core.dialogs.newProjectDialog import newProjectDialog
from core.dialogs.newPlutoDSDialog import newPlutoDSDialog
from utls.yamlReader import ProjectReader, dataLoader, dataSourceReader
from utls.structure import Queue, ProjectQueue, TabManager
from utls.setting import plutoVariables

import warnings

warnings.filterwarnings('ignore')


class mainWindow(QMainWindow):
    disableProjectMenu = pyqtSignal()
    enableProjectMenu = pyqtSignal()

    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)
        self.ui = loadUi('UI/mainFrame.ui', self)
        self.mainWidget = QWidget(self)
        self.mainWidgetLayout = QVBoxLayout(self.mainWidget)
        self.setCentralWidget(self.mainWidget)
        self.setWindowIcon(QIcon('res/pluto.ico'))
        ###############################
        # local variables
        self.defaultDir = '.'
        self.curOpenProjectHandle = None
        self.curProjectTabManager = None
        self.openedProject = ProjectQueue()
        self.handleToTabWidget = dict()
        self.plutoVariables = plutoVariables()
        # flags

        ###############################
        # menu
        newProjectMenu = self.ui.actionNew_Project
        newProjectMenu.triggered.connect(self.newProjectDialog)
        openProjectMenu = self.ui.actionOpen_Project
        openProjectMenu.triggered.connect(self.openProjectDialog)
        saveProjectMenu = self.ui.actionSave_Project
        saveProjectMenu.triggered.connect(self.saveProject)

        self.newProjectDataSetMenu = self.ui.actionNew_DataSet
        self.newProjectDataSetMenu.triggered.connect(self.onNewProjectDataSetMenu)
        self.newProjectModel = self.ui.actionNew_Model
        self.newProjectModel.triggered.connect(self.onNewProjectModel)
        self.newProjectScript = self.ui.actionNew_Script
        self.newProjectScript.triggered.connect(self.onNewProjectScript)

        self.newProjectDataSetMenu.setEnabled(False)
        self.newProjectModel.setEnabled(False)
        self.newProjectScript.setEnabled(False)
        ###############################
        # init toolbar status bar
        self.toolBar = QToolBar(self)
        self.statusBar = QStatusBar(self)
        self.openAction = QAction(QIcon('res/Open.ico'), 'Open Project', self)
        self.homePageAction = QAction(QIcon('res/homepage.png'), 'HOME', self)
        self.projectAction = QAction(QIcon('res/ProjectManager.ico'), 'Project Manager', self)
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
        self.downSize = 0.22 * self.height()
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
        self.setContextMenuPolicy(Qt.NoContextMenu)  # close right click of mainWindow

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
        # self.horizontal_splitter.setSizes([self.height() * 0.78, self.height() * 0.22])
        self.horizontal_splitter.setSizes([self.height() - self.downSize, self.downSize])

        self.horizontal_splitter.splitterMoved.connect(self.onHSplitterMoved)

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

        # connect
        self.disableProjectMenu.connect(self.onDisableProjectMenu)
        self.enableProjectMenu.connect(self.onEnableProjectMenu)

    def initToolBar(self):
        self.statusBar.setContentsMargins(10, 0, 0, 10)
        self.addToolBar(self.toolBar)
        self.setStatusBar(self.statusBar)

        # open
        self.openAction.setStatusTip('Open Project')
        self.openAction.triggered.connect(self.openProjectDialog)
        self.toolBar.addAction(self.openAction)

        self.homePageAction.setStatusTip('Home Page')
        self.homePageAction.triggered.connect(self.jumpToHomePage)
        self.toolBar.addAction(self.homePageAction)

        self.projectAction.setStatusTip('Project Manager')
        self.projectAction.triggered.connect(self.showOpenProject)
        self.toolBar.addAction(self.projectAction)

    def initProjectList(self):
        self.scrollarea.setWidgetResizable(True)
        self.projectList.setLayout(self.projectListLayout)
        self.scrollarea.setWidget(self.projectList)
        self.scrollarea.setVerticalScrollBar(self.scrollbar)
        self.scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.mainLayout.addWidget(self.scrollarea)

        # init projects from plutoVariables projectFiles
        projectHandleList = []
        # projectItemList = []
        for projectPath in self.plutoVariables.projectFiles:
            projectHandle = ProjectReader(projectPath)
            projectHandleList.append(projectHandle)

            # projectName, projectLocation, lastOpenTime, projectFiles
            projectItem = ProjectWidget(projectHandle.projectName, projectHandle.projectPath,
                                        projectHandle.lastAccessTime, projectHandle)
            projectItem.triggered.connect(self.openProject)
            self.projectListLayout.addWidget(projectItem)

    def newProjectDialog(self):
        dialog = newProjectDialog(self)
        dialog.projectInited.connect(self.onProjectInited)
        dialog.show()

    def openProject(self, handle: ProjectReader):
        if self.openedProject.isExist(handle):
            QMessageBox.information(self, 'open project', "project \"" + handle.projectName + "\" has been opened")
        else:
            print('open project:', handle.projectName)
            tabWidget = ColorTabWidget(self)
            tabManager = self.initTabWidget(tabWidget, handle)
            self.openedProject.add(handle, tabManager)
            self.mainLayout.addWidget(tabWidget)
            self.mainLayout.setCurrentIndex(self.openedProject.currentIndex)
            self.curOpenProjectHandle = handle  # self.openedProject.getHandle(self.openedProject.currentIndex)
            self.curProjectTabManager = tabManager
            self.updateProjectLastAccessTime()
            self.enableProjectMenu.emit()

    def closeProject(self):
        if self.curOpenProjectHandle:
            self.saveProject()
            self.curOpenProjectHandle = None
            gc.collect()

    def saveProject(self):  # TODO
        print('save project')
        if not self.curOpenProjectHandle:
            QMessageBox.information(self, 'Save Project', 'No open project', QMessageBox.Ok)
        else:
            self.curOpenProjectHandle.saveToYaml()
            QMessageBox.information(self, 'Save Project', 'Project Saved to ' + self.curOpenProjectHandle.yamlFile,
                                    QMessageBox.Ok)

    def changeProjectName(self, name):
        self.curOpenProjectHandle.setProjectName(name)
        self.curOpenProjectHandle.updateToYamlDict()

    def updateProjectLastAccessTime(self):
        currentTime = datetime.utcnow()
        self.curOpenProjectHandle.setLastAccessTime(currentTime)
        self.curOpenProjectHandle.updateToYamlDict()

    def addFileToProject(self):  # TODO
        pass

    def delFileFromProject(self):  # TODO
        pass

    def openProjectDialog(self):
        dialog = QFileDialog(self)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dialog.setDirectory(self.defaultDir)
        projectFile, _ = dialog.getOpenFileName(self, "Open Project", "",
                                                "Project File (*.pluto);;All Files (*.*)", options=options)
        if projectFile:
            handle = ProjectReader(projectFile)
            self.openProject(handle)
        else:
            raise Exception('Open project failed')

    def jumpToHomePage(self):
        self.mainLayout.setCurrentIndex(0)
        self.disableProjectMenu.emit()

    def showOpenProject(self):
        # display a pop menu of current open project
        if not len(self.openedProject):
            print('no opened project')
            return
        allOpenedProjectID = self.openedProject.getAllID()
        openedProjectMenu = QMenu()
        for index, ID in enumerate(allOpenedProjectID):
            if not ID:
                continue
            handle = self.openedProject.getHandle(index)
            oneProject = QAction(handle.projectName, self)
            oneProject.triggered.connect(partial(self.showProjectPage, index))
            openedProjectMenu.addAction(oneProject)

        self.projectAction.setMenu(openedProjectMenu)
        openedProjectMenu.exec(QCursor.pos())

    def showProjectPage(self, index):
        # show opened project page using index
        self.mainLayout.setCurrentIndex(index)
        self.curOpenProjectHandle, self.curProjectTabManager = self.openedProject.getHandle(index)
        self.enableProjectMenu.emit()

    def initTabWidget(self, tabWidget: ColorTabWidget, handle: ProjectReader):
        tabManager = TabManager(tabWidget, handle)
        # init qml main page list
        projectMainPage = QQuickWidget(tabWidget)
        projectMainPage.setResizeMode(QQuickWidget.SizeRootObjectToView)
        projectMainPage.setSource(QUrl.fromLocalFile('QML/ProjectMainPage.qml'))
        projectMainPage.setMinimumWidth(550)
        projectMainPage.setMinimumHeight(250)
        projectMainPage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        obj_projectMainPage = projectMainPage.rootObject()
        # send main page init dict
        obj_projectMainPage.onInitMainPageItems(self.getProjectDetail(tabManager))
        obj_projectMainPage.sendData.connect(self.getData_ProjectMainPage)
        tabManager.qmlHandle = obj_projectMainPage
        tabManager.qmlWidget = projectMainPage
        tabWidget.addTab(projectMainPage, 'MainPage:MainPage')
        return tabManager

    @staticmethod
    def getProjectDetail(tabManager: TabManager):
        info = dict()
        handle = tabManager.handle
        info['ID'] = handle.yamlFile
        info['projectName'] = handle.projectName
        info['lastAccessTime'] = handle.lastAccessTime.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime(
            '%y/%m/%d %H:%M:%S')
        info['model'] = handle.modelSourceHandle.getAllPath()
        info['data'] = handle.dataSourceHandle.getAllPath()
        info['script'] = handle.scriptSourceHandle.getAllPath()
        info['result'] = []
        return info

    def onProjectInited(self, projectFile: str):
        handle = ProjectReader(projectFile)
        self.openProject(handle)

    def getData_ProjectMainPage(self, data):
        dataType, itemIndex, itemName = data.toVariant()
        # print(dataType, itemIndex, itemName)
        if dataType == 'data':
            handle = dataLoader(itemName)
            self.openDSEditor(handle)

    def changeEvent(self, e: QEvent) -> None:
        if e.type() == QEvent.WindowStateChange and self.windowState() == Qt.WindowMaximized:
            self.horizontal_splitter.setSizes([self.height() - self.downSize, self.downSize])
        elif e.type() == QEvent.WindowStateChange and self.windowState() == Qt.WindowNoState:
            self.horizontal_splitter.setSizes([self.height() - self.downSize, self.downSize])

    def onHSplitterMoved(self, pos: int, index: int):
        self.downSize = self.height() - pos

    def onDisableProjectMenu(self):
        self.newProjectDataSetMenu.setEnabled(False)
        self.newProjectModel.setEnabled(False)
        self.newProjectScript.setEnabled(False)

    def onEnableProjectMenu(self):
        self.newProjectDataSetMenu.setEnabled(True)
        self.newProjectModel.setEnabled(True)
        self.newProjectScript.setEnabled(True)

    def onNewProjectDataSetMenu(self):
        dialog = newPlutoDSDialog(self.curOpenProjectHandle, self)
        r = dialog.exec()
        if r == QDialog.Accepted:
            obj_projectMainPage = self.curProjectTabManager.qmlWidget.rootObject()
            obj_projectMainPage.addData(dialog.target)
            handle = dataLoader(dialog.target)
            self.openDSEditor(handle)

    def onNewProjectModel(self):
        pass

    def onNewProjectScript(self):
        pass

    def openDSEditor(self, DSHandle):
        tabManager = self.curProjectTabManager
        tabWidget = tabManager.tabWidget
        if DSHandle.yamlFile in tabManager.dataTabs:
            print(tabManager.dataTabs[DSHandle.yamlFile])
            tabWidget.setCurrentIndex(tabManager.dataTabs[DSHandle.yamlFile][0])
        else:
            widget, title = self.DSEditor(DSHandle, tabWidget)
            tabWidget.addTab(widget, title)
            tabManager.dataTabs[DSHandle.yamlFile] = tabWidget.count() - 1, widget
            tabWidget.setCurrentIndex(tabWidget.count() - 1)

    def DSEditor(self, DSHandle: dataLoader, parent=None):
        handle = DSHandle
        widget = QWidget(parent)
        title = 'Data:' + QDir(handle.yamlFile).dirName()

        return widget, title
