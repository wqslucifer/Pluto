class plutoDefaults(object):
    def __init__(self):
        self.projectHome = 'E:/project/Pluto/test'


class yamlReaderSetting(object):
    def __init__(self):
        self.dataSourceTypes = []
        self.modelSourceTypes = []
        self.scriptSourceTypes = []
        self.resultSourceTypes = []

    def addType(self, sourceType, source):
        pass