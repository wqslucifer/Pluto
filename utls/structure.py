import pandas
import numpy
import os
import sys


class ProjectQueue(object):
    def __init__(self):
        self.projectDict = dict()
        self.project_index = ['']
        self.length = 0
        self.currentIndex = 0

    def isExist(self, handle):
        if handle.yamlFile in self.projectDict:
            return True
        else:
            return False

    def add(self, handle):
        self.projectDict[handle.yamlFile] = handle
        self.project_index.append(handle.yamlFile)
        self.currentIndex += 1
        self.length += 1

        print(self.projectDict)

    def getHandle(self, index):
        return self.projectDict[self.project_index[index]]

    def getAllHandle(self):
        return self.projectDict

    def getAllID(self):
        return self.project_index

    def __len__(self):
        return self.length


class Queue(object):
    def __init__(self):
        self.__data = []
        self.length = 0

    def push(self, val):
        self.__data.append(val)
        self.length += 1

    def pop(self):
        if self.length > 0:
            self.length -= 1
        return self.__data.pop(-1)

    def __len__(self):
        return self.length

    def __str__(self):
        return self.__data


class TabManager(object):
    def __init__(self, tabWidget, handle):
        self.handle = handle
        self.tabWidget = tabWidget
        # tab manage
        self.mainPageWidget = None
        self.modelTabs = []
        self.dataTabs = []
        self.resultTabs = []
        self.runTabs = []

    def setMainPageWidget(self, widget):
        self.mainPageWidget = widget
