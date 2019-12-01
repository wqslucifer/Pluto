import yaml
import os
import abc
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
        self.raw_project = None
        self.projectName = None
        self.projectPath = None
        self.createTime = None  # using utc time
        self.lastAccessTime = None  # using utc time
        self.projectFiles = None  # dict
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
        fileTree = self.projectFiles['root']
        key = list(fileTree.keys())[0]
        self.contents = fileTree[key]

    def checkFileTree(self):
        fileTree = self.projectFiles['root']
        key = list(fileTree.keys())[0]
        contents = fileTree[key]
        curPath = os.path.join(self.projectPath)
        self.checkDirs(curPath, contents)
        self.__logger.debug(self.projectFiles)
        self.projectFiles['root'][key] = contents
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
                self.raw_project = yaml.safe_load(f)
                self.projectName = self.raw_project['projectName']
                self.projectPath = self.raw_project['projectPath']
                self.createTime = self.raw_project['createTime']
                self.lastAccessTime = self.raw_project['lastAccessTime']
                self.projectFiles = self.raw_project['projectFiles']
                self.dataSource = self.raw_project['dataSource']
                self.modelSource = self.raw_project['modelSource']
                self.scriptSource = self.raw_project['scriptSource']
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

    def setLastAccessTime(self, time: datetime):
        # set property
        self.lastAccessTime = time
        self.updateToYamlDict()

    def setProjectName(self, name: str):
        self.projectName = name
        self.updateToYamlDict()

    def setProjectPath(self, path: str):
        self.projectPath = path
        self.updateToYamlDict()

    def setProjectFiles(self, files: dict):
        self.projectFiles = files
        self.updateToYamlDict()

    def updateToYamlDict(self):
        # update information to yaml dict
        self.raw_project['lastAccessTime'] = self.lastAccessTime
        self.raw_project['projectName'] = self.projectName
        self.raw_project['projectPath'] = self.projectPath
        self.raw_project['projectFiles'] = self.projectFiles
        self.raw_project['dataSource'] = self.dataSource
        self.raw_project['modelSource'] = self.modelSource
        self.raw_project['scriptSource'] = self.scriptSource

    def saveToYaml(self):
        # save yaml dict to project file
        with open(self.yamlFile, 'w') as f:
            yaml.safe_dump(self.raw_project, f, default_flow_style=False)


class sourceReader(metaclass=abc.ABCMeta):
    def __init__(self, yamlFile):
        self.yamlFile = yamlFile
        self.raw_data = None
        self.lastUpdateTime = None
        self.fileClassList = []

        # logger
        self.__logger = logging.getLogger('debug')
        self.__logger.setLevel(logging.INFO)

    @abc.abstractmethod
    def loadYaml(self):
        pass

    def setFileClassList(self, *args):
        for c in args:
            self.fileClassList.append(c)

    @property
    def lastUpdateTimeLocal(self):
        return self.lastUpdateTime.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%y/%m/%d %H:%M:%S')

    def updateToYaml(self):
        # update information to yaml dict
        with open(self.yamlFile, 'w') as f:
            yaml.safe_dump(self.raw_data, f, default_flow_style=False)

    def updateTime(self):
        self.lastUpdateTime = datetime.utcnow()
        self.raw_data['lastUpdateTime'] = self.lastUpdateTime
        self.updateToYaml()

    def getAllPath(self):
        r = []
        for d in self.fileClassList:
            if d:
                for uid, path in d.items():
                    r.append(path)
        return r


class dataSourceReader(sourceReader):
    def __init__(self, yamlFile):
        super().__init__(yamlFile)
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

        # local storage
        self.dataSourceWeb = None
        self.csvFiles = {}
        self.imageDirs = {}
        self.plutoDataSets = {}
        self.totalSize = ''

        # load yaml file
        self.loadYaml()

    def parseCSVFiles(self):
        parsedCSVDict = {
            'train_csv': [],
            'test_csv': [],
            'sample_submission_csv': [],
            'other_csv': [],
            'notFoundFile': [],
            'badUID': [],
        }
        if len(self.csvFiles) > 0:
            for uid, filePath in self.csvFiles.items():
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
        if len(self.imageDirs) > 0:
            for uid, filePath in self.imageDirs.items():
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

    def loadYaml(self):
        with open(self.yamlFile, 'r') as f:
            try:
                self.raw_data = yaml.safe_load(f)
                self.lastUpdateTime = self.raw_data['lastUpdateTime']
                self.csvFiles = self.raw_data['csvFiles']
                self.imageDirs = self.raw_data['imageDirs']
                self.totalSize = self.raw_data['totalSize']
                self.plutoDataSets = self.raw_data['plutoDataSet']
                super().setFileClassList(self.plutoDataSets)
            except yaml.YAMLError:
                self.__logger.error('yaml file error: ' + self.yamlFile)

    def addCSVFile(self, uid: str, filePath: str):  # TODO
        self.csvFiles[uid] = filePath
        self.raw_data['csvFiles'] = self.csvFiles
        self.updateToYaml()

    def addImageDir(self, uid: str, imageDir: str):  # TODO
        self.imageDirs[uid] = imageDir
        self.raw_data['imageDirs'] = self.imageDirs
        self.updateToYaml()


class scriptSourceReader(sourceReader):
    def __init__(self, yamlFile):
        super().__init__(yamlFile)
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
        self.raw_data = None
        self.lastUpdateTime = None
        self.processScripts = {}
        self.visualizeScripts = {}
        self.modelScripts = {}
        # logger
        self.__logger = logging.getLogger('debug')
        self.__logger.setLevel(logging.INFO)
        # load yaml file
        self.loadYaml()

    def loadYaml(self):
        with open(self.yamlFile, 'r') as f:
            try:
                self.raw_data = yaml.safe_load(f)
                self.lastUpdateTime = self.raw_data['lastUpdateTime']
                self.processScripts = self.raw_data['processScripts']
                self.visualizeScripts = self.raw_data['visualizeScripts']
                self.modelScripts = self.raw_data['modelScripts']
                super().setFileClassList(self.processScripts, self.modelScripts, self.visualizeScripts)
            except yaml.YAMLError:
                self.__logger.error('yaml file error: ' + self.yamlFile)

    def addScriptFile(self, uid: str, filePath: str, scriptType='processScripts'):  # TODO
        if scriptType == 'processScripts':
            self.processScripts[uid] = filePath
            self.raw_data['processScripts'] = self.processScripts
        elif scriptType == 'visualizeScripts':
            self.visualizeScripts[uid] = filePath
            self.raw_data['visualizeScripts'] = self.visualizeScripts
        elif scriptType == 'modelScripts':
            self.modelScripts[uid] = filePath
            self.raw_data['modelScripts'] = self.modelScripts
        else:
            self.__logger.error('unknown script type: ' + str(scriptType))
        self.updateToYaml()


class modelSourceReader(sourceReader):
    def __init__(self, yamlFile):
        super().__init__(yamlFile)
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
        self.raw_data = None
        self.lastUpdateTime = None
        self.DL_classification = {}
        self.DL_segmentation = {}
        self.ML_model = {}
        # logger
        self.__logger = logging.getLogger('debug')
        self.__logger.setLevel(logging.INFO)
        # load yaml file
        self.loadYaml()

    def loadYaml(self):
        with open(self.yamlFile, 'r') as f:
            try:
                self.raw_data = yaml.safe_load(f)
                self.lastUpdateTime = self.raw_data['lastUpdateTime']
                self.DL_classification = self.raw_data['DL_classification']
                self.DL_segmentation = self.raw_data['DL_segmentation']
                self.ML_model = self.raw_data['ML_model']
                super().setFileClassList(self.DL_classification, self.DL_segmentation, self.ML_model)
            except yaml.YAMLError:
                self.__logger.error('yaml file error: ' + self.yamlFile)

    def addModelFile(self, uid: str, filePath: str, modelType='DL_classification'):  # TODO
        if modelType == 'DL_classification':
            self.DL_classification[uid] = filePath
            self.raw_data['DL_classification'] = self.DL_classification
        elif modelType == 'DL_segmentation':
            self.DL_segmentation[uid] = filePath
            self.raw_data['DL_segmentation'] = self.DL_segmentation
        elif modelType == 'ML_model':
            self.ML_model[uid] = filePath
            self.raw_data['ML_model'] = self.ML_model
        else:
            self.__logger.error('unknown script type: ' + str(modelType))
        self.updateToYaml()


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
        self.raw_data = None
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
                self.raw_data = yaml.safe_load(f)
                self.lastUpdateTime = self.raw_data['lastUpdateTime']
                self.dataSourceWeb = self.raw_data['dataSourceWeb']
                self.dataSource = self.raw_data['dataSource']
                self.scriptSource = self.raw_data['scriptSource']
                self.dataType = self.raw_data['dataType']
                self.dataFiles = self.raw_data['dataFiles']
                self.dataDescribe = self.raw_data['dataDescribe']
                self.preprocessScript = self.raw_data['preprocessScript']
            except yaml.YAMLError:
                self.__logger.error('yaml file error: ' + yamlFile)

    def saveToYaml(self):
        self.raw_data['lastUpdateTime'] = self.lastUpdateTime
        self.raw_data['dataSourceWeb'] = self.dataSourceWeb
        self.raw_data['dataSource'] = self.dataSource
        self.raw_data['scriptSource'] = self.scriptSource
        self.raw_data['dataType'] = self.dataType
        self.raw_data['dataFiles'] = self.dataFiles
        self.raw_data['dataDescribe'] = self.dataDescribe
        self.raw_data['preprocessScript'] = self.preprocessScript
        with open(self.yamlFile, 'w') as f:
            yaml.safe_dump(self.raw_data, f, default_flow_style=False)


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
        self.raw_model = None
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
                self.raw_model = yaml.safe_load(f)
                self.lastUpdateTime = self.raw_model['lastUpdateTime']
                self.scriptSource = self.raw_model['scriptSource']
                self.trainData = self.raw_model['trainData']
                self.testData = self.raw_model['testData']
                self.usingValData = self.raw_model['usingValData']
                self.modelType = self.raw_model['modelType']
                self.param = self.raw_model['param']
                self.modelDescribe = self.raw_model['modelDescribe']
                self.modelScript = self.raw_model['modelScript']
                self.postProcessScript = self.raw_model['postProcessScript']
            except yaml.YAMLError:
                self.__logger.error('yaml file error: ' + yamlFile)

    def saveToYaml(self):
        self.raw_model['lastUpdateTime'] = self.lastUpdateTime
        self.raw_model['scriptSource'] = self.scriptSource
        self.raw_model['trainData'] = self.trainData
        self.raw_model['testData'] = self.testData
        self.raw_model['usingValData'] = self.usingValData
        self.raw_model['modelType'] = self.modelType
        self.raw_model['param'] = self.param
        self.raw_model['modelDescribe'] = self.modelDescribe
        self.raw_model['modelScript'] = self.modelScript
        self.raw_model['postProcessScript'] = self.postProcessScript

        with open(self.yamlFile, 'w') as f:
            yaml.safe_dump(self.raw_model, f, default_flow_style=False)


class scriptLoader(object):
    def __init__(self, scFile):
        self.scFile = scFile


if __name__ == '__main__':
    p = ProjectReader('../test/testProject_1/project.pluto')
    print(p.dataSourceHandle.getAllPath())
