import QtQuick 2.12
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.3
import QtQuick.Controls.Material 2.2

Rectangle {
    id: root
    property var count: 0
    property var projectID: ''
    property var modelList: []
    property var dataList: []
    property var scriptList: []
    property var resultList: []
    property var initHeight: 400

    function onInitMainPageItems(PanelItems){
        projectID = PanelItems['ID']
        modelList = PanelItems['model']
        dataList = PanelItems['data']
        scriptList = PanelItems['script']
        resultList = PanelItems['result']
        console.log(PanelItems['projectName'])
        listModel.append({'projectName':PanelItems['projectName']})
        count = modelList.length + dataList.length + scriptList.length + resultList.length
        root.height = initHeight+500*count
        //selectPage_DM.initModel(DMPageItems)
    }
    width: 800
    height: initHeight

    ListView {
        id: listView
        anchors.fill: parent
        model: listModel
        delegate:delegate
    }
    Component{
        id: delegate
        CollapsibleItem{
            width: parent.width
            height: 40
            headerName: projectName
        }
    }

    ListModel {
        id: listModel
    }


}
