# Pluto File

## 1. File Type

### 1.1 Pluto Project File (*.pluto)

Pluto Project File (*.pluto) stores project detail information.

```yaml
createTime: 2018-01-03 21:59:43
lastAccessTime: 2019-11-09 22:23:43.079325
projectFiles:
  root:
    testProject_1:
    - data:
      - dataFile1
      - dataSource.source
      - train_images: []
      - test_images: []
      - train.csv
      - test.csv
      - train_data.ds
      - other.csv
      - sample_submission.csv
    - model:
      - modelFile1
      - model_lightgbm.md
      - modelSource.source
    - script:
      - script1
      - catboost.sc
      - lightgbm.sc
      - preprocessScript.sc
      - postprocessScript.sc
      - scriptSource.source
      - u-net.sc
      - vgg16.sc
      - visualizationScript.sc
      - xgboost.sc
    - project.pluto
    - delFile.1
    - delFile_2:
      - delfile_3
    - result:
      - resultFile1
projectName: testProject_1
projectPath: E:\project\Pluto\test\testProject_1
dataSource: E:\project\Pluto\test\testProject_1\data\dataSource.source
modelSource: E:\project\Pluto\test\testProject_1\model\modelSource.source
scriptSource: E:\project\Pluto\test\testProject_1\script\scriptSource.source

```





### 1.2 Source File

Source File is used to store all data, model and script files that can be used in the project. All source file is using Yaml syntax.
Each file stores in source file as a map **{UID: file path}**

> **UID** is the **unique** id for a type of file. 
> **UID** is formed using **File Code + Sequence Code**.
>
> **File Code** is used to classify type of files.

####   **1. Data source file**

Data source file is used to store **csv files**, **image directories** and **pluto datasets**.

```yaml
lastUpdateTime: 2019-11-09 22:23:43.079325
totalSize: '980 MB'
csvFiles:
  00FF0000: 'E:\project\Pluto\test\testProject_1\data\train.csv'
  01FF0000: 'E:\project\Pluto\test\testProject_1\data\test.csv'
  02FF0000: 'E:\project\Pluto\test\testProject_1\data\other.csv'
  0AFF0000: 'E:\project\Pluto\test\testProject_1\data\sample_submission.csv'

imageDirs:
  CCFF0000: 'E:\project\Pluto\test\testProject_1\data\train_images'
  DDFF0000: 'E:\project\Pluto\test\testProject_1\data\test_images'

plutoDataSet:
  FFFF0000: 'E:\project\Pluto\test\testProject_1\data\train_data.ds'
```

**Data Source Code: **

| Code   | Type                      |
| ------ | ------------------------- |
| **00** | **train csv**             |
| **01** | **test csv**              |
| **02** | **other csv**             |
| **0A** | **sample submission csv** |
| **CC** | **train image directory** |
| **DD** | **test image directory**  |
| **EE** | **other image directory** |
| **FF** | **pluto datasets**        |



#### 2.  **Model Source File**

Model source file is used to store **machine model**, **deep learning classification model** and **deep learning segmentation model**.

```yaml
lastUpdateTime: 2019-11-09 22:23:43.079325
ML_model:
  40FF0000: 'E:\project\Pluto\test\testProject_1\model\model_lightgbm.md'

DL_classification:
DL_segmentation:
```

**Model Source Code: **

| Code   | Type                |
| ------ | ------------------- |
| **40** | **lightgbm**        |
| **41** | **xgboost**         |
| **42** | **catboost**        |
| **43** | **linear**          |
| **44** | **randomForest**    |
| **A0** | **vgg**             |
| **A1** | **resnet**          |
| **A2** | **inception**       |
| **A3** | **inceptionResnet** |
| **A4** | **densenet**        |
| **A5** | **mobilenet**       |
| **A6** | **xception**        |
| **A7** | **squeezenet**      |
| **A8** | **googlenet**       |
| **A9** | **se_resnet**       |
| **AA** | **senet**           |
| **AB** | **efficientnet**    |
| **C0** | **unet**            |
| **C1** | **FPN**             |
| **C2** | **PSPNet**          |
| **C3** | **Linknet**         |

#### 3. Script Source File

Script source file is used to store **preprocess script**, **visualize script** and **model script**.

```yaml
lastUpdateTime: 2019-11-09 22:23:43.079325
processScripts:
  00FF0000: 'E:\project\Pluto\test\testProject_1\script\preprocessScript.sc'
  01FF0000: 'E:\project\Pluto\test\testProject_1\script\postprocessScript.sc'

visualizeScripts:
  20FF0000: 'E:\project\Pluto\test\testProject_1\script\visualizationScript.sc'

modelScripts:
  40FF0000: 'E:\project\Pluto\test\testProject_1\script\lightgbm.sc'
  41FF0000: 'E:\project\Pluto\test\testProject_1\script\xgboost.sc'
  42FF0000: 'E:\project\Pluto\test\testProject_1\script\catboost.sc'
  A0FF0000: 'E:\project\Pluto\test\testProject_1\script\vgg.sc'
  C0FF0000: 'E:\project\Pluto\test\testProject_1\script\u-net.sc'
```

**Script Source Code: **

| Code      | Type              |
| --------- | ----------------- |
| **00**    | **preprocess**    |
| **01**    | **postprocess**   |
| **20**    | **visualization** |
| **21**    | **utility**       |
| **other** | **model type**    |

### 1.3 Data File (*.ds)

**Data File (*.ds):** 

- **Data source**:  used to locate data. 
- **Script source**: used to locate processing script
- **Preprocess script**: script for preprocessing data
- **cacheLoc**: cache location, pluto will save the preprocessed data to this location, if last update time of data file is older than preprocess script update time, pluto will update this cache. Can be disabled by setting [saveCacheData](./PlutoSetting.md#saveCacheData) to False.

```yaml
lastUpdateTime: 2019-11-09 22:23:43.079325
dataSource: 'E:\project\Pluto\test\testProject_1\data\dataSource.source'
scriptSource: 'E:\project\Pluto\test\testProject_1\script\scriptSource.source'
dataType:
 - '00'
 - '02'
dataFiles:
  - '00FF0000'
  - '02FF0000'
dataDescribe: 'xxx xxx'
preprocessScript:
  - '00FF0000'
cacheLoc: 'E:\project\Pluto\test\testProject_1\data\processedData.pds'
```



### 1.4 Model File (*.md)

**model File (*.md):**

	- **scriptSource**: script source for model
	- **trainData**: the path to pluto train data file **(*.ds)**
	- **testData**: the path to pluto test data file **(*.ds)**
	- **usingValData**: a flag to indicate if using validation of train data
	- **modelType**: model type code
	- **param**: a dict of model's parameter 
	- **modelScript**: model definition script
	- **postProcessScript**: postprocessing script

### 1.5 Script File

**Script File(*.sc)** is python script file to define different models and functions. Script File has different template for different usages.

#### 1.5.1 preprocessing

```python
def preprocessing_func_name(
    trainSet, 			# train set
    testSet,  			# test set 
    mem_opt=False, 		# memory optimazation
    shuffle=False,		# shuffle the train set
):
    # code here
    return trainSet, testSet
```



#### 1.5.2 postprocessing

```python
def postprocessing_func_name(
    data, 				# post process data
):
    # code here
    return data
```



#### 1.5.3 utility

#### 1.5.4 metric function

#### 1.5.5 loss function

#### 1.5.6 machine learning model

```python
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
```

[Template File](../template/xgboost.tpl)

#### 1.5.7 deep learning classifier

#### 1.5.8 deep learning segmentation model

