# template file for xgboost model

class xgboost_classifier(object):
    def __init__(self, dataset):
        # init model
        pass

    def prepareData(self):
        # prepare data, like run preprocessing script and check the cache data
        pass

    def run(self):
        # train the model
        pass

    def chooseCV(self, strategy='kfold'):
        # choose to use what kind of cv method
        pass

    def predict(self):
        # predict test set
        pass
