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
        self.dataSource = None
        self.modelSource = None
        self.scriptSource = None
        self.dataSourceHandle = None
        self.modelSourceHandle = None
        self.scriptSourceHandle = None
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
                self.dataSource = self.__raw_project['dataSource']
                self.modelSource = self.__raw_project['modelSource']
                self.scriptSource = self.__raw_project['scriptSource']
                if self.dataSource:
                    self.loadDataSource()
                if self.modelSource:
                    self.loadModelSource()
                if self.scriptSource:
                    self.loadScriptSource()
            except yaml.YAMLError:
                self.__logger.error('yaml file error: ' + yamlFile)

    def loadDataSource(self):
        self.dataSourceHandle = dataSourceReader(self.dataSource)

    def loadModelSource(self):
        self.modelSourceHandle = modelSourceReader(self.modelSource)

    def loadScriptSource(self):
        self.scriptSourceHandle = scriptSourceReader(self.scriptSource)

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
        self.__raw_project['dataSource'] = self.dataSource
        self.__raw_project['modelSource'] = self.modelSource
        self.__raw_project['scriptSource'] = self.scriptSource

    def saveToYaml(self):
        # save yaml dict to project file
        with open(self.yamlFile, 'w') as f:
            yaml.safe_dump(self.__raw_project, f, default_flow_style=False)


class dataSourceReader(object):
    def __init__(self, yamlFile):
        self.code = {
            '00': 'train_csv',
            '01': 'test_csv',
            '02': 'other_csv',
            '0A': 'sample_submission_csv',
            'CC': 'trainImageDir',
            'DD': 'testImageDir',
            'EE': 'otherImageDir',
            'FF': 'plutoDataSets',
        }
        self.yamlFile = yamlFile
        # local storage
        self.__raw_data = None
        self.__lastUpdateTime = None
        self.__dataSourceWeb = None
        self.__csvFiles = {}
        self.__imageDirs = {}
        self.__plutoDataSets = {}
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
                self.__plutoDataSets = self.__raw_data['plutoDataSet']
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

    def getAllData(self, select='path'):
        r = []
        for d in [self.__plutoDataSets]:
            if d:
                for uid, dataPath in d.items():
                    dataHandle = dataLoader(dataPath)
                    if select == 'path':
                        r.append(dataPath)
                    else:
                        r.append((uid, dataPath, dataHandle))
        return r


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

    def getAllScript(self, select='path'):
        r = []
        for d in [self.__processScripts, self.__modelScripts, self.__visualizeScripts]:
            if d:
                for uid, scriptPath in d.items():
                    handle = scriptLoader(scriptPath)
                    if select == 'path':
                        r.append(scriptPath)
                    else:
                        r.append((uid, scriptPath, handle))
        return r


class modelSourceReader(object):
    def __init__(self, yamlFile):
        self.modelCode = {
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
        self.__DL_classification = {}
        self.__DL_segmentation = {}
        self.__ML_model = {}
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
    def DL_classification(self):
        return self.__DL_classification

    @property
    def DL_segmentation(self):
        return self.__DL_segmentation

    @property
    def ML_model(self):
        return self.__ML_model

    def loadYaml(self, yamlFile: str):
        with open(yamlFile, 'r') as f:
            try:
                self.__raw_data = yaml.safe_load(f)
                self.__lastUpdateTime = self.__raw_data['lastUpdateTime']
                self.__DL_classification = self.__raw_data['DL_classification']
                self.__DL_segmentation = self.__raw_data['DL_segmentation']
                self.__ML_model = self.__raw_data['ML_model']

            except yaml.YAMLError:
                self.__logger.error('yaml file error: ' + yamlFile)

    def updateToYaml(self):
        # update information to yaml dict

        with open(self.yamlFile, 'w') as f:
            yaml.safe_dump(self.__raw_data, f, default_flow_style=False)

    def addModelFile(self, uid: str, filePath: str, modelType='DL_classification'):  # TODO
        if modelType == 'DL_classification':
            self.__DL_classification[uid] = filePath
            self.__raw_data['DL_classification'] = self.__DL_classification
        elif modelType == 'DL_segmentation':
            self.__DL_segmentation[uid] = filePath
            self.__raw_data['DL_segmentation'] = self.__DL_segmentation
        elif modelType == 'ML_model':
            self.__ML_model[uid] = filePath
            self.__raw_data['ML_model'] = self.__ML_model
        else:
            self.__logger.error('unknown script type: ' + str(modelType))
        self.updateToYaml()

    def updateTime(self):
        self.__lastUpdateTime = datetime.utcnow()
        self.__raw_data['lastUpdateTime'] = self.__lastUpdateTime
        self.updateToYaml()

    def getAllModel(self, select='path'):
        r = []
        for d in [self.__DL_classification, self.__DL_segmentation, self.__ML_model]:
            if d:
                for uid, modelPath in d.items():
                    handle = modelLoader(modelPath)
                    if select == 'path':
                        r.append(modelPath)
                    else:
                        r.append((uid, modelPath, handle))
        return r


class dataLoader(object):
    def __init__(self, yamlFile):
        self.code = {
            '00': 'train_csv',
            '01': 'test_csv',
            '02': 'other_csv',
            '0A': 'sample_submission_csv',
            'CC': 'trainImageDir',
            'DD': 'testImageDir',
            'EE': 'otherImageDir',
            'FF': 'plutoDataSets',
        }
        self.__raw_data = None
        self.dataSourceWeb = None
        self.lastUpdateTime = None
        self.dataSource = None
        self.scriptSource = None
        self.dataType = None
        self.dataFiles = None
        self.dataDescribe = None
        self.preprocessScript = None
        self.yamlFile = yamlFile
        self.__logger = logging.getLogger('debug')
        self.__logger.setLevel(logging.INFO)
        self.loadData(yamlFile)

    def loadData(self, yamlFile):
        with open(yamlFile, 'r') as f:
            try:
                self.__raw_data = yaml.safe_load(f)
                self.lastUpdateTime = self.__raw_data['lastUpdateTime']
                self.dataSourceWeb = self.__raw_data['dataSourceWeb']
                self.dataSource = self.__raw_data['dataSource']
                self.scriptSource = self.__raw_data['scriptSource']
                self.dataType = self.__raw_data['dataType']
                self.dataFiles = self.__raw_data['dataFiles']
                self.dataDescribe = self.__raw_data['dataDescribe']
                self.preprocessScript = self.__raw_data['preprocessScript']
            except yaml.YAMLError:
                self.__logger.error('yaml file error: ' + yamlFile)

    def saveToYaml(self):
        self.__raw_data['lastUpdateTime'] = self.lastUpdateTime
        self.__raw_data['dataSourceWeb'] = self.dataSourceWeb
        self.__raw_data['dataSource'] = self.dataSource
        self.__raw_data['scriptSource'] = self.scriptSource
        self.__raw_data['dataType'] = self.dataType
        self.__raw_data['dataFiles'] = self.dataFiles
        self.__raw_data['dataDescribe'] = self.dataDescribe
        self.__raw_data['preprocessScript'] = self.preprocessScript
        with open(self.yamlFile, 'w') as f:
            yaml.safe_dump(self.__raw_data, f, default_flow_style=False)


class modelLoader(object):
    def __init__(self, yamlFile):
        self.modelCode = {
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
        self.__raw_model = None
        self.lastUpdateTime = None
        self.scriptSource = None
        self.trainData = None
        self.testData = None
        self.usingValData = None
        self.modelType = None
        self.param = None
        self.modelDescribe = None
        self.modelScript = None
        self.postProcessScript = None
        self.yamlFile = yamlFile
        self.__logger = logging.getLogger('debug')
        self.__logger.setLevel(logging.INFO)
        self.loadModel(yamlFile)

    def loadModel(self, yamlFile: str):
        with open(yamlFile, 'r') as f:
            try:
                self.__raw_model = yaml.safe_load(f)
                self.lastUpdateTime = self.__raw_model['lastUpdateTime']
                self.scriptSource = self.__raw_model['scriptSource']
                self.trainData = self.__raw_model['trainData']
                self.testData = self.__raw_model['testData']
                self.usingValData = self.__raw_model['usingValData']
                self.modelType = self.__raw_model['modelType']
                self.param = self.__raw_model['param']
                self.modelDescribe = self.__raw_model['modelDescribe']
                self.modelScript = self.__raw_model['modelScript']
                self.postProcessScript = self.__raw_model['postProcessScript']
            except yaml.YAMLError:
                self.__logger.error('yaml file error: ' + yamlFile)

    def saveToYaml(self):
        self.__raw_model['lastUpdateTime'] = self.lastUpdateTime
        self.__raw_model['scriptSource'] = self.scriptSource
        self.__raw_model['trainData'] = self.trainData
        self.__raw_model['testData'] = self.testData
        self.__raw_model['usingValData'] = self.usingValData
        self.__raw_model['modelType'] = self.modelType
        self.__raw_model['param'] = self.param
        self.__raw_model['modelDescribe'] = self.modelDescribe
        self.__raw_model['modelScript'] = self.modelScript
        self.__raw_model['postProcessScript'] = self.postProcessScript

        with open(self.yamlFile, 'w') as f:
            yaml.safe_dump(self.__raw_model, f, default_flow_style=False)


class scriptLoader(object):
    def __init__(self, scFile):
        self.scFile = scFile


if __name__ == '__main__':
    p = ProjectReader('../test/testProject_1/project.pluto')
    print(p.dataSourceHandle.getAllData())
