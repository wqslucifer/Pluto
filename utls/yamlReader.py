import yaml
import os
import logging
import datetime

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
        self.__logger.setLevel(logging.DEBUG)
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
            elif isinstance(c ,str):
                if not os.path.exists(os.path.join(curPath, c)):
                    self.__logger.debug(['del ', c])
                    del_index.append(i)
        for i in sorted(del_index, reverse=True):
            contents.pop(i)

    def loadProject(self, yamlFile:str):
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


if __name__ == '__main__':
    p = ProjectReader('../test/testProject_1/project.pluto')
    p.checkFileTree()
    print(p.projectFiles)
