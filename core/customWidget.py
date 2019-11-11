import os
import sys

from datetime import datetime, timezone, time, date
from PyQt5.QtWidgets import QLabel, QGridLayout, QWidget, QDialog, QHBoxLayout, QApplication, QToolBar, \
    QPushButton, QVBoxLayout, QStylePainter, QStyleOptionTab, QSizePolicy, QStackedWidget, QScrollBar, \
    QScrollArea, QTreeView, QSplitter, QStylePainter, QStyle, QStyleOptionButton, QTableView, QTabWidget, \
    QTabBar
from PyQt5.QtCore import Qt, QPoint, QRectF, pyqtSignal, QSortFilterProxyModel, QModelIndex, QMimeData, \
    QAbstractTableModel, QVariant, QTimer, pyqtSlot, pyqtProperty
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QPainterPath, QIcon, QMouseEvent, QStandardItemModel, \
    QPaintEvent, QImage, QPixmap, QDrag, QDragEnterEvent, QDragMoveEvent, QTextOption, \
    QDropEvent, QPalette

from utls.yamlReader import ProjectReader


class ProjectWidget(QWidget):
    # signal
    triggered = pyqtSignal(ProjectReader)

    def __init__(self, projectName, projectLocation, lastOpenTime, projectHandle):
        super(ProjectWidget, self).__init__()
        self.setFixedSize(180, 180)
        self.mainLayout = QGridLayout(self)
        self.edge = None
        self.labelFont = QFont("Arial", 10, QFont.Bold)
        self.bgColor = None
        self.normColor = None
        self.enterColor = None
        self.pressColor = None
        self.ColorSet = {'normColor': '#BBAAFF', 'enterColor': '#7D5EF9', 'pressColor': '#7056DC'}

        # project info
        self.projectName = QLabel(projectName)
        self.projectLocation = RollingLabel(self)
        self.projectLocation.showScrollText(projectLocation)
        self.projectLocation.setToolTip(projectLocation)
        self.projectLocation.setStatusTip('Project Location: ' + projectLocation)

        # self.projectLastOpenTime = RollingLabel(self)
        # self.projectLastOpenTime.showScrollText()
        self.localTime = lastOpenTime.replace(tzinfo=timezone.utc).astimezone(tz=None)
        self.projectLastOpenTime = QLabel('Last Open: ' + self.localTime.strftime('%y/%m/%d %H:%M:%S'))
        self.projectLastOpenTime.setToolTip(self.localTime.strftime('%y/%m/%d %H:%M:%S'))
        self.projectLastOpenTime.setStatusTip('Last Open Time: ' + self.localTime.strftime('%y/%m/%d %H:%M:%S'))

        # project yaml handle
        self.projectHandle = projectHandle

        self.initUI()

    def initUI(self):
        self.setAutoFillBackground(True)
        self.setLayout(self.mainLayout)

        self.mainLayout.setContentsMargins(18, 18, 0, 0)
        self.mainLayout.addWidget(self.projectName, 0, 0, Qt.AlignTop)
        self.mainLayout.addWidget(self.projectLocation, 1, 0)
        self.mainLayout.addWidget(self.projectLastOpenTime, 2, 0)
        self.mainLayout.setRowStretch(3, 10)
        # set color set
        self.setColorSet(**self.ColorSet)

        self.bgColor = self.normColor
        self.edge = QRectF(5, 5, 170, 170)
        # bg translucent
        self.setStyleSheet("background-color: rgba(0,0,0,0)")

        self.projectName.setFont(QFont('Arial', 12, QFont.Black))
        self.projectLocation.setFont(QFont('Arial', 10, QFont.Thin))
        self.projectLastOpenTime.setFont(QFont('Arial', 10))
        self.projectLastOpenTime.setMaximumWidth(self.width() - 35)

    def paintEvent(self, ev):
        path = QPainterPath()
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 0, 0, 127), 6))
        painter.setRenderHint(QPainter.Antialiasing)
        path.addRoundedRect(self.edge, 15, 15)
        painter.drawPath(path)
        painter.fillPath(path, self.bgColor)

    def updateBgColor(self, color):
        self.bgColor = color
        self.update()

    def enterEvent(self, QEvent):
        self.updateBgColor(self.enterColor)

    def leaveEvent(self, QEvent):
        self.updateBgColor(self.normColor)

    def mousePressEvent(self, QMouseEvent):
        self.updateBgColor(self.pressColor)

    def mouseReleaseEvent(self, MouseEvent: QMouseEvent):
        self.updateBgColor(self.enterColor)
        if MouseEvent.button() == Qt.RightButton:
            print('right click menu')
        elif MouseEvent.button() == Qt.LeftButton:
            self.triggered.emit(self.projectHandle)

    def setColorSet(self, normColor, enterColor, pressColor):
        self.normColor = QColor(normColor)
        self.enterColor = QColor(enterColor)
        self.pressColor = QColor(pressColor)


class TitleBar(QWidget):
    left = 0
    up = 1
    right = 2
    down = 3

    Horizontal = 0
    Vertical = 1

    def __init__(self, title, parent=None):
        super(TitleBar, self).__init__(parent=parent)
        self.Title = QLabel(title, self)
        self.Icon = QIcon('./res/collapse_left.ico')
        self.Height = 40
        self.currentOrient = self.left
        self.font = QFont('Arial', 12, QFont.Bold)
        self.CollapseButton = QPushButton(self.Icon, '', self)
        self.mainLayout = None
        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.addWidget(self.Title, 1, Qt.AlignLeft)
        self.mainLayout.addStretch(1)
        self.mainLayout.addWidget(self.CollapseButton, 1, Qt.AlignRight)
        self.setLayout(self.mainLayout)
        self.Title.setFont(self.font)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(self.Height)

    def setTitle(self, title):
        self.Title.setText(title)

    def setIcon(self, icon: QIcon):
        self.Icon = icon

    def setButtonOrient(self, orient):
        if orient == self.left:
            self.Icon = QIcon('./res/collapse_left.ico')
        elif orient == self.up:
            self.Icon = QIcon('./res/collapse_up.ico')
        elif orient == self.right:
            self.Icon = QIcon('./res/collapse_right.ico')
        elif orient == self.down:
            self.Icon = QIcon('./res/collapse_down.ico')
        self.CollapseButton.setIcon(self.Icon)
        self.currentOrient = orient

    def setHeight(self, size):
        self.Height = size
        self.setFixedHeight(self.Height)

    def onCollapseButtonClicked(self):
        if self.currentOrient == self.left:
            self.setButtonOrient(self.right)
        elif self.currentOrient == self.right:
            self.setButtonOrient(self.left)
        elif self.currentOrient == self.up:
            self.setButtonOrient(self.down)
        elif self.currentOrient == self.down:
            self.setButtonOrient(self.up)


class CollapsibleTabWidget(QWidget):
    Horizontal = 0
    Vertical = 1
    doCollapse = pyqtSignal()

    def __init__(self, orientation=0, parent=None):
        super(CollapsibleTabWidget, self).__init__(parent=parent)
        self.frameLayout = None
        self.verticalLayout = None
        self.tabBar = None
        self.tabBarWidget = QWidget(self)
        self.orientation = orientation
        # self.orientation = self.Vertical
        self.splitter = None
        self.splitterPos = None
        self.splitterLower = None
        self.stackTitle = None
        self.stackWidget = None
        self.tabBarList = []

        # local data
        if self.orientation == self.Horizontal:
            self.initHorizontalUI()
            self.titleBarIcon = TitleBar.down
        elif self.orientation == self.Vertical:
            self.initVerticalUI()
            self.titleBarIcon = TitleBar.left

        self.tabBarWidget.setStyleSheet('background-color: #B2B2B2;')
        self.stackTitle.setStyleSheet('background-color: #B2B2B2;')

    def initHorizontalUI(self):
        self.frameLayout = QVBoxLayout(self)
        self.tabBar = QHBoxLayout(self.tabBarWidget)
        self.tabBarWidget.setLayout(self.tabBar)
        self.tabBar.setAlignment(Qt.AlignLeft)
        self.verticalLayout = QVBoxLayout()
        # fill stack
        self.stackTitle = QStackedWidget(self)
        self.stackWidget = QStackedWidget(self)
        self.verticalLayout.addWidget(self.stackTitle)
        self.verticalLayout.addWidget(self.stackWidget)
        # finish
        self.frameLayout.addLayout(self.verticalLayout)
        self.frameLayout.addWidget(self.tabBarWidget)
        self.setLayout(self.frameLayout)
        self.tabBarWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frameLayout.setContentsMargins(0, 0, 0, 0)
        self.tabBar.setContentsMargins(0, 0, 0, 0)

    def initVerticalUI(self):
        self.frameLayout = QHBoxLayout(self)
        self.verticalLayout = QVBoxLayout(self)
        # tab bar
        self.tabBar = QVBoxLayout(self)
        self.tabBarWidget.setLayout(self.tabBar)
        self.tabBar.setAlignment(Qt.AlignTop)
        # fill stack
        self.stackTitle = QStackedWidget(self)
        self.stackWidget = QStackedWidget(self)

        self.verticalLayout.addWidget(self.stackTitle)
        self.verticalLayout.addWidget(self.stackWidget)

        self.stackWidget.addWidget(QLabel('asdf', self))
        # finish
        self.frameLayout.addWidget(self.tabBarWidget)
        self.frameLayout.addLayout(self.verticalLayout)
        self.setLayout(self.frameLayout)
        self.tabBarWidget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)

    def setOrientation(self, orient):
        self.orientation = orient

    def onTabClicked(self, index):
        pass

    def addTab(self, widget: QWidget, title: str):
        titleBar = TitleBar(title, self)
        titleBar.setButtonOrient(self.titleBarIcon)
        titleBar.CollapseButton.clicked.connect(self.collapseStacks)
        self.stackTitle.addWidget(titleBar)
        self.stackWidget.addWidget(widget)
        tabButton = customPushButton(title, len(self.tabBarList), self.orientation, self)
        self.tabBarList.append(tabButton)

        tabButton.clicked.connect(self.collapseStacks)
        tabButton.clicked_index.connect(self.setCurStack)
        self.tabBar.addWidget(tabButton, 0, Qt.AlignLeft)

        self.stackTitle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.stackTitle.setFixedHeight(titleBar.Height)

    def collapseStacks(self):
        if self.stackWidget.isVisible():
            self.splitterPos = self.splitter.sizes()
            self.stackTitle.hide()
            self.stackWidget.hide()
            if self.orientation == self.Horizontal:
                self.splitter.setSizes([10000, 0])
            if self.orientation == self.Vertical:
                self.splitter.setSizes([0, 10000])
            self.splitter.handle(1).setDisabled(True)
        else:
            self.splitter.setSizes(self.splitterPos)
            self.stackTitle.show()
            self.stackWidget.show()
            self.splitter.handle(1).setDisabled(False)
        self.doCollapse.emit()

    def setCurStack(self, index):
        self.stackTitle.setCurrentIndex(index)
        self.stackWidget.setCurrentIndex(index)

    def setSplitter(self, splitter: QSplitter):
        self.splitter = splitter
        self.splitter.splitterMoved.connect(self.setSplitterRate)

    def setSplitterRate(self, pos, index):
        self.splitterLower = self.splitter.sizes()[1]


class customPushButton(QPushButton):
    clicked_index = pyqtSignal(int)
    Horizontal = 0
    Vertical = 1

    def __init__(self, label, index, orientation=0, parent=None):
        super(customPushButton, self).__init__(parent=parent)
        self.setText(label)
        self.index = index
        self.orientation = orientation
        if orientation == self.Vertical:
            self.setFixedWidth(25)
        if orientation == self.Horizontal:
            self.setFixedHeight(25)

    def mouseReleaseEvent(self, event):
        self.clicked_index.emit(self.index)
        QPushButton.mouseReleaseEvent(self, event)

    def paintEvent(self, event: QPaintEvent):
        painter = QStylePainter(self)
        if self.orientation == self.Vertical:
            painter.rotate(270)
            painter.translate(-1 * self.height(), 0)
        painter.drawControl(QStyle.CE_PushButton, self.getStyleOptions())

    def minimumSizeHint(self):
        size = super(customPushButton, self).minimumSizeHint()
        if self.orientation == self.Vertical:
            size.transpose()
        return size

    def sizeHint(self):
        size = super(customPushButton, self).sizeHint()
        if self.orientation == self.Vertical:
            size.transpose()
        return size

    def getStyleOptions(self):
        options = QStyleOptionButton()
        options.initFrom(self)
        size = options.rect.size()
        if self.orientation == self.Vertical:
            size.transpose()
        options.rect.setSize(size)
        options.features = QStyleOptionButton.None_
        if self.isFlat():
            options.features |= QStyleOptionButton.Flat
        if self.menu():
            options.features |= QStyleOptionButton.HasMenu
        if self.autoDefault() or self.isDefault():
            options.features |= QStyleOptionButton.AutoDefaultButton
        if self.isDefault():
            options.features |= QStyleOptionButton.DefaultButton
        if self.isDown() or (self.menu() and self.menu().isVisible()):
            options.state |= QStyle.State_Sunken
        if self.isChecked():
            options.state |= QStyle.State_On
        if not self.isFlat() and not self.isDown():
            options.state |= QStyle.State_Raised

        options.text = self.text()
        options.icon = self.icon()
        options.iconSize = self.iconSize()
        return options


class DragTableView(QTableView):
    def __init__(self, parent=None):
        super(DragTableView, self).__init__(parent=parent)
        self.setAcceptDrops(True)

        self.model = None
        self.ifValidPress = False
        self.startRow = 0
        self.targetRow = 0
        self.dragStartPoint = None
        self.dragPointAtItem = None
        self.dragText = None
        self.itemRowHeight = 30
        self.headerHeight = 0
        self.lineLabel = QLabel(self)
        self.lineLabel.setFixedHeight(2)
        self.lineLabel.setGeometry(1, 0, self.width(), 2)
        self.lineLabel.setStyleSheet("border: 1px solid #8B7500;")
        self.lineLabel.hide()
        self.curRow = 0

        self.setDropIndicatorShown(True)

    def setModel(self, model):
        QTableView.setModel(self, model)
        self.model = model
        self.model.notEmpty.connect(self.updateModelInfo)
        self.itemRowHeight = self.rowHeight(0) if not self.model.checkEmpty() else None
        self.headerHeight = self.horizontalHeader().sectionSizeFromContents(0).height()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                self.ifValidPress = True
                self.dragStartPoint = event.pos()
                self.dragText = '%s %s %s' % (self.model.data(self.model.index(index.row(), 0), Qt.DisplayRole),
                                              self.model.data(self.model.index(index.row(), 1), Qt.DisplayRole),
                                              self.model.data(self.model.index(index.row(), 2), Qt.DisplayRole))
                self.dragPointAtItem = self.dragStartPoint - QPoint(0, index.row() * self.itemRowHeight)
                self.startRow = index.row()
        QTableView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.ifValidPress:
            return
        if not event.buttons() & Qt.LeftButton:
            return
        if (event.pos() - self.dragStartPoint).manhattanLength() < QApplication.startDragDistance():
            return

        self.lineLabel.show()
        self.doDrag()
        self.lineLabel.hide()
        self.ifValidPress = False

    def doDrag(self):
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(self.dragText)
        drag.setMimeData(mimeData)

        drag_img = QPixmap(self.width(), self.itemRowHeight)
        drag_img.fill(QColor(255, 255, 255, 100))
        painter = QPainter(drag_img)
        painter.setPen(QColor(0, 0, 0, 200))
        painter.drawText(QRectF(40, 0, self.width(), self.itemRowHeight), self.dragText, QTextOption(Qt.AlignVCenter))
        painter.end()

        drag.setPixmap(drag_img)
        drag.setHotSpot(self.dragPointAtItem)
        if drag.exec(Qt.MoveAction) == Qt.MoveAction:
            print('drag')

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
            QTableView.dragEnterEvent(self, event)

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasText():
            self.curRow = 0
            index = self.indexAt(event.pos())
            if index.isValid():
                if event.pos().y() - index.row() * self.itemRowHeight >= self.itemRowHeight / 2:
                    self.curRow = index.row() + 1
                else:
                    self.curRow = index.row()
            else:
                self.curRow = self.model.rowCount()

            self.targetRow = self.curRow
            self.lineLabel.setGeometry(1, self.headerHeight + self.targetRow * self.itemRowHeight, self.width() - 2,
                                       2)
            event.acceptProposedAction()
            return
        event.ignore()
        QTableView.dragMoveEvent(self, event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasText():
            if self.startRow != self.targetRow - 1 and self.startRow != self.targetRow:
                print('move ', self.startRow, ' to ', self.targetRow)
                if self.targetRow > self.startRow:
                    self.model.moveProcess(self.startRow, self.targetRow - 1)
                else:
                    self.model.moveProcess(self.startRow, self.targetRow)
            event.acceptProposedAction()
            return
        event.ignore()
        QTableView.dropEvent(self, event)

    def updateModelInfo(self):
        # update height when adding rows to empty model
        self.itemRowHeight = self.rowHeight(0) if not self.model.checkEmpty() else None
        self.headerHeight = self.horizontalHeader().sectionSizeFromContents(0).height()


class RollingLabel(QLabel):
    def __init__(self, parent=None):
        super(RollingLabel, self).__init__(parent=parent)
        self.stepWidth = None
        self.stepTime = None
        self.curIndex = None
        self.showText = None
        self.scrollTimer = QTimer(self)

        self.setFixedWidth(150)
        self.setFixedHeight(20)
        self.initLabel()

    def initLabel(self):
        self.stepTime = 100
        self.stepWidth = 3
        self.curIndex = 0
        self.scrollTimer.timeout.connect(self.updateIndex)

    def showScrollText(self, text):
        if self.scrollTimer.isActive():
            self.scrollTimer.stop()
        self.showText = text
        self.scrollTimer.start(self.stepTime)

    def updateIndex(self):
        self.update()
        self.curIndex += 1
        if self.curIndex * self.stepWidth > self.width():
            self.curIndex = 0

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.drawText(0 - self.stepWidth * self.curIndex, 15, self.showText[self.curIndex:])
        painter.drawText(self.width() - self.stepWidth * self.curIndex, 15, self.showText[:self.curIndex])


class ColorfulTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super(ColorfulTabWidget, self).__init__(parent=parent)
        self.colorTabBar = QTabBar(self)


class ColorTabBar(QTabBar):
    def __init__(self, colors, parent=None):
        super(ColorTabBar, self).__init__(parent)
        self.mColors = colors

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            if opt.text in self.mColors:
                opt.palette.setColor(
                    QPalette.Button, self.mColors[opt.text]
                )
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)


class ColorTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super(ColorTabWidget, self).__init__(parent)
        d = {
            "Model: ": QColor("#ff8566"),  # red
            "Data: ": QColor("#ffe680"),  # yellow
            "Script: ": QColor("#b3ff99"),  # green
            "Result: ": QColor("#80ccff"),  # blue
            "Run: ": QColor("#aa80ff"),  # pink
            "MainPage": QColor("#eb99ff"),  #
        }
        self.setTabBar(ColorTabBar(d))
