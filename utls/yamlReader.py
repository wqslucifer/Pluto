import yaml
import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timezone

logging.basicConfig()


# Level	Numeric value
# CRITICAL	50
# ERROR	    40
# WARNING	30
# INFO	    20
# DEBUG	    10
# NOTSET	0

class ProjectReader(object):
    def __init__(self, yamlFile):
        self.yamlFile = yamlFile
        self.__raw_project = None
        self.__projectName = None
        self.__projectPath = None
        self.__createTime = None  # using utc time
        self.__lastAccessTime = None  # using utc time
        self.__projectFiles = None  # dict
        self.loadProject(yamlFile)
        self.__logger = logging.getLogger('debug')
        self.__logger.setLevel(logging.INFO)
        # handler = logging.FileHandler('output.log')
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # handler.setFormatter(formatter)
        # logger.addHandler(handler)
        self.checkFileTree()
        fileTree = self.__projectFiles['root']
        key = list(fileTree.keys())[0]
        self.contents = fileTree[key]

    def checkFileTree(self):
        fileTree = self.__projectFiles['root']
        key = list(fileTree.keys())[0]
        contents = fileTree[key]
        curPath = os.path.join(self.__projectPath)
        self.checkDirs(curPath, contents)
        self.__logger.debug(self.__projectFiles)
        self.__projectFiles['root'][key] = contents
        self.updateToYamlDict()

    def checkDirs(self, curPath, contents):
        self.__logger.debug([curPath, contents])
        del_index = []
        for i, c in enumerate(contents):
            if isinstance(c, dict):
                key = list(c.keys())[0]
                if not os.path.exists(os.path.join(curPath, key)):
                    self.__logger.debug(['del ', c])
                    del_index.append(i)
                else:
                    self.checkDirs(os.path.join(curPath, key), contents[i][key])
            elif isinstance(c, str):
                if not os.path.exists(os.path.join(curPath, c)):
                    self.__logger.debug(['del ', c])
                    del_index.append(i)
        for i in sorted(del_index, reverse=True):
            contents.pop(i)

    def loadProject(self, yamlFile: str):
        with open(yamlFile, 'r') as f:
            try:
                self.__raw_project = yaml.safe_load(f)
                self.__projectName = self.__raw_project['projectName']
                self.__projectPath = self.__raw_project['projectPath']
                self.__createTime = self.__raw_project['createTime']
                self.__lastAccessTime = self.__raw_project['lastAccessTime']
                self.__projectFiles = self.__raw_project['projectFiles']
            except yaml.YAMLError:
                self.__logger.error('yaml file error: ' + yamlFile)

    @property
    def lastAccessTime(self):
        return self.__lastAccessTime

    @property
    def createTime(self):
        return self.__createTime

    @property
    def projectName(self):
        return self.__projectName

    @property
    def projectPath(self):
        return self.__projectPath

    @property
    def projectFiles(self):
        return self.__projectFiles

    def setLastAccessTime(self, time: datetime):
        # set property
        self.__lastAccessTime = time
        self.updateToYamlDict()

    def setProjectName(self, name: str):
        self.__projectName = name
        self.updateToYamlDict()

    def setProjectPath(self, path: str):
        self.__projectPath = path
        self.updateToYamlDict()

    def setProjectFiles(self, files: dict):
        self.__projectFiles = files
        self.updateToYamlDict()

    def updateToYamlDict(self):
        # update information to yaml dict
        self.__raw_project['lastAccessTime'] = self.__lastAccessTime
        self.__raw_project['projectName'] = self.__projectName
        self.__raw_project['projectPath'] = self.__projectPath
        self.__raw_project['projectFiles'] = self.__projectFiles

    def saveToYaml(self):
        # save yaml dict to project file
        with open(self.yamlFile, 'w') as f:
            yaml.safe_dump(self.__raw_project, f, default_flow_style=False)

    def getModels(self):
        modelDir = os.path.join(self.__projectPath, 'model')
        if os.path.exists(modelDir):
            return modelDir, os.listdir(modelDir)
        else:
            return None, []

    def getData(self):
        dataDir = os.path.join(self.__projectPath, 'data')
        if os.path.exists(dataDir):
            return dataDir, os.listdir(dataDir)
        else:
            return None, []

    def getScripts(self):
        scriptDir = os.path.join(self.__projectPath, 'script')
        if os.path.exists(scriptDir):
            return scriptDir, os.listdir(scriptDir)
        else:
            return None, []

    def getResults(self):
        resultDir = os.path.join(self.__projectPath, 'result')
        if os.path.exists(resultDir):
            return resultDir, os.listdir(resultDir)
        else:
            return None, []


class dataSourceReader(object):
    def __init__(self, yamlFile):
        self.code = {
            '00': 'train_csv',
            '01': 'test_csv',
            '02': 'other_csv',
            '0A': 'sample_submission_csv',
            'CC': 'trainImageDir',
            'DD': 'testImageDir',
            'FF': 'otherImageDir',

        }
        self.yamlFile = yamlFile
        # local storage
        self.__raw_data = None
        self.__lastUpdateTime = None
        self.__dataSourceWeb = None
        self.__csvFiles = {}
        self.__imageDirs = {}
        self.__totalSize = ''
        # logger
        self.__logger = logging.getLogger('debug')
        self.__logger.setLevel(logging.INFO)
        # load yaml file
        self.loadYaml(yamlFile)

    def parseCSVFiles(self):
        parsedCSVDict = {
            'train_csv': [],
            'test_csv': [],
            'sample_submission_csv': [],
            'other_csv': [],
            'notFoundFile': [],
            'badUID': [],
        }
        if len(self.__csvFiles) > 0:
            for uid, filePath in self.__csvFiles.items():
                if os.path.exists(filePath):
                    if uid[:2] not in self.code:
                        parsedCSVDict['badUID'].append((uid, filePath))
                        continue
                    csv_type = self.code[uid[:2]]
                    parsedCSVDict[csv_type].append((uid, filePath))
                else:
                    parsedCSVDict['notFoundFile'].append((uid, filePath))
            return parsedCSVDict
        else:
            return None

    def parseImageDirs(self):
        parsedImageDict = {
            'trainImageDir': [],
            'testImageDir': [],
            'otherImageDir': [],
            'badUID': [],
            'notFoundFile': [],
        }
        if len(self.__imageDirs) > 0:
            for uid, filePath in self.__imageDirs.items():
                if os.path.exists(filePath):
                    if uid[:2] not in self.code:
                        parsedImageDict['badUID'].append((uid, filePath))
                        continue
                    dirType = self.code[uid[:2]]
                    parsedImageDict[dirType].append((uid, filePath))
                else:
                    parsedImageDict['notFoundFile'].append((uid, filePath))
            return parsedImageDict
        else:
            return None

    @property
    def lastUpdateTime(self):
        return self.__lastUpdateTime

    @property
    def lastUpdateTimeLocal(self):
        return self.__lastUpdateTime.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%y/%m/%d %H:%M:%S')

    @property
    def csvFiles(self):
        return self.__csvFiles

    @property
    def imageDirs(self):
        return self.__imageDirs

    def loadYaml(self, yamlFile: str):
        with open(yamlFile, 'r') as f:
            try:
                self.__raw_data = yaml.safe_load(f)
                self.__lastUpdateTime = self.__raw_data['lastUpdateTime']
                self.__csvFiles = self.__raw_data['csvFiles']
                self.__imageDirs = self.__raw_data['imageDirs']
                self.__totalSize = self.__raw_data['totalSize']

            except yaml.YAMLError:
                self.__logger.error('yaml file error: ' + yamlFile)

    def updateToYaml(self):
        with open(self.yamlFile, 'w') as f:
            yaml.safe_dump(self.__raw_data, f, default_flow_style=False)

    def addCSVFile(self, uid: str, filePath: str):  # TODO
        self.__csvFiles[uid] = filePath
        self.__raw_data['csvFiles'] = self.__csvFiles
        self.updateToYaml()

    def addImageDir(self, uid: str, imageDir: str):  # TODO
        self.__imageDirs[uid] = imageDir
        self.__raw_data['imageDirs'] = self.__imageDirs
        self.updateToYaml()

    def updateTime(self):
        self.__lastUpdateTime = datetime.utcnow()
        self.__raw_data['lastUpdateTime'] = self.__lastUpdateTime
        self.updateToYaml()


class scriptSourceReader(object):
    def __init__(self, yamlFile):
        self.scriptCode = {
            '00': 'preprocess',
            '01': 'postprocess',
            '20': 'visualization',
            '40': 'lightgbm',
            '41': 'xgboost',
            '42': 'catboost',
            '43': 'linear',
            '44': 'randomForest',
            'A0': 'vgg',
            'A1': 'resnet',
            'A2': 'inception',
            'A3': 'inceptionResnet',
            'A4': 'densenet',
            'A5': 'mobilenet',
            'A6': 'xception',
            'A7': 'squeezenet',
            'A8': 'googlenet',
            'A9': 'se_resnet',
            'AA': 'senet',
            'AB': 'efficientnet',
            'C0': 'unet',
            'C1': 'FPN',
            'C2': 'PSPNet',
            'C3': 'Linknet',
        }
        self.yamlFile = yamlFile
        # local storage
        self.__raw_data = None
        self.__lastUpdateTime = None
        self.__dataSourceWeb = None
        self.__processScripts = {}
        self.__visualizeScripts = {}
        self.__modelScripts = {}
        # logger
        self.__logger = logging.getLogger('debug')
        self.__logger.setLevel(logging.INFO)
        # load yaml file
        self.loadYaml(yamlFile)

    @property
    def lastUpdateTime(self):
        return self.__lastUpdateTime

    @property
    def lastUpdateTimeLocal(self):
        return self.__lastUpdateTime.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%y/%m/%d %H:%M:%S')

    @property
    def processScripts(self):
        return self.__processScripts

    @property
    def modelScripts(self):
        return self.__modelScripts

    @property
    def visualizeScripts(self):
        return self.__visualizeScripts

    def loadYaml(self, yamlFile: str):
        with open(yamlFile, 'r') as f:
            try:
                self.__raw_data = yaml.safe_load(f)
                self.__lastUpdateTime = self.__raw_data['lastUpdateTime']
                self.__processScripts = self.__raw_data['processScripts']
                self.__visualizeScripts = self.__raw_data['visualizeScripts']
                self.__modelScripts = self.__raw_data['modelScripts']

            except yaml.YAMLError:
                self.__logger.error('yaml file error: ' + yamlFile)

    def updateToYaml(self):
        # update information to yaml dict

        with open(self.yamlFile, 'w') as f:
            yaml.safe_dump(self.__raw_data, f, default_flow_style=False)

    def addScriptFile(self, uid: str, filePath: str, scriptType='processScripts'):  # TODO
        if scriptType == 'processScripts':
            self.__processScripts[uid] = filePath
            self.__raw_data['processScripts'] = self.__processScripts
        elif scriptType == 'visualizeScripts':
            self.__visualizeScripts[uid] = filePath
            self.__raw_data['visualizeScripts'] = self.__visualizeScripts
        elif scriptType == 'modelScripts':
            self.__modelScripts[uid] = filePath
            self.__raw_data['modelScripts'] = self.__modelScripts
        else:
            self.__logger.error('unknown script type: ' + str(scriptType))
        self.updateToYaml()

    def updateTime(self):
        self.__lastUpdateTime = datetime.utcnow()
        self.__raw_data['lastUpdateTime'] = self.__lastUpdateTime
        self.updateToYaml()


if __name__ == '__main__':
    p = scriptSourceReader('../test/testProject_1/script/scriptSource.source')
    print(p.processScripts, p.modelScripts)
