import os
import yaml

plutoSetting = 'E:/project/Pluto/utls/plutoSetting.config'


class plutoVariables(object):
    def __init__(self):
        self.rawData = self.loadPlutoVariables()
        self.projectHome = self.rawData['projectHome']
        self.projectFiles = self.rawData['projectFiles']

    def loadPlutoVariables(self):
        rawData = {}
        with open(plutoSetting, 'r') as f:
            try:
                rawData = yaml.safe_load(f)
            except:
                raise Exception('load pluto setting error')
        return rawData

    def checkProjectFiles(self):
        for p in self.projectFiles:
            if not os.path.exists(p):
                self.projectFiles.remove(p)
                print(p)
                # log: record delete project file from list


class yamlReaderSetting(object):
    def __init__(self):
        self.dataSourceTypes = []
        self.modelSourceTypes = []
        self.scriptSourceTypes = []
        self.resultSourceTypes = []

    def addType(self, sourceType, source):
        pass