import os
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.Qt import QStyle
from PyQt5.QtCore import Qt, QSize
from core.mainWindow import mainWindow

windowInitWidthRatio = 0.65
windowInitHeightRatio = 0.7

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = mainWindow()
    availableSize = app.desktop().availableGeometry().size()
    width = availableSize.width()*windowInitWidthRatio
    height = availableSize.height()*windowInitHeightRatio
    window.setGeometry(
        QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, QSize(width, height), app.desktop().availableGeometry()))
    window.show()
    # exceptionHandler.errorSignal.connect(something)
    sys.exit(app.exec_())
