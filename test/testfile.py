import yaml
import os

class Project(object):
    def __init__(self, yamlFile):
        self.projectName = None
        self.projectPath = None
        self.createTime = None
        self.lastAccessTime = None
        self.projectFiles = None
        self.loadProject(yamlFile)

    def checkFileTree(self):
        fileTree = self.projectFiles['root']
        key = list(fileTree.keys())[0]
        contents = fileTree[key]
        curPath = os.path.join(self.projectPath)
        self.checkDirs(curPath, contents)
        print(self.projectFiles)

    def checkDirs(self, curPath, contents):
        print(curPath, contents)
        del_index = []
        for i, c in enumerate(contents):
            if isinstance(c, dict):
                key = list(c.keys())[0]
                if not os.path.exists(os.path.join(curPath, key)):
                    print('del ', c)
                    del_index.append(i)
                else:
                    self.checkDirs(os.path.join(curPath, key), contents[i][key])
            elif isinstance(c ,str):
                if not os.path.exists(os.path.join(curPath, c)):
                    print('del ', c)
                    del_index.append(i)

        for i in sorted(del_index, reverse=True):
            contents.pop(i)

    def loadProject(self, yamlFile:str):
        with open(yamlFile, 'r') as f:
            try:
                raw_project = yaml.safe_load(f)
                self.projectName = raw_project['projectName']
                self.projectPath = raw_project['projectPath']
                self.createTime = raw_project['createTime']
                self.lastAccessTime = raw_project['lastAccessTime']
                self.projectFiles = raw_project['projectFiles']

            except yaml.YAMLError:
                print('yaml file error: '+yamlFile)

if __name__ == '__main__':
    p = Project('testProject_1/project.pluto')
    p.checkFileTree()