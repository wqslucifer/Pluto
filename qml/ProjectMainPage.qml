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
    property var initHeight: 200
    property var projectName: ''
    property var lastAccessTime: ''

    function onInitMainPageItems(PanelItems){
        projectID = PanelItems['ID']
        modelList = PanelItems['model']
        dataList = PanelItems['data']
        scriptList = PanelItems['script']
        resultList = PanelItems['result']
        lastAccessTime = PanelItems['lastAccessTime']
        // init modelList
        listModel.append({panelMode:'Model',header: 'Model'})

        listModel.append({panelMode:'Data',header: 'Data'})

        listModel.append({panelMode:'Script',header: 'Script'})

        listModel.append({panelMode:'Result',header: 'Result'})

        count = modelList.length + dataList.length + scriptList.length + resultList.length
        root.height = initHeight+500*count
        //selectPage_DM.initModel(DMPageItems)
    }

    width: 800
    height: initHeight
    radius: 15
    border.width: 4
    color: 'transparent'

    Rectangle{
        id: projectInfo
        color: 'transparent'
        width: parent.width
        height: 80
        Column {
            id: column
            anchors.rightMargin: 5
            anchors.leftMargin: 5
            anchors.bottomMargin: 0
            anchors.topMargin: 10
            anchors.fill: parent
            spacing: 5
            Row {
                id: projectNameRow
                height: 20
                anchors.right: parent.right
                anchors.rightMargin: 5
                anchors.left: parent.left
                anchors.leftMargin: 5
                Layout.fillWidth: true
                Label{
                    id: projectNameLabel
                    width: parent.width
                    height: parent.height
                    color: "#2b2826"
                    text: 'projectName'
                    font.bold: false
                    font.weight: Font.DemiBold
                    font.pointSize: 15
                    font.family: "Verdana"
                    fontSizeMode: Text.HorizontalFit
                    verticalAlignment: Text.AlignVCenter
                }
            }
            Row{
                id: projectLocation
                height: 20
                anchors.right: parent.right
                anchors.rightMargin: 5
                anchors.left: parent.left
                anchors.leftMargin: 5
                Layout.fillWidth: true
                property var lastAccTimeWidth: 70
                Label{
                    id: projectLocationLabel
                    width: parent.width - projectLocation.lastAccTimeWidth
                    height: parent.height
                    text: 'location: '
                    font.pointSize: 10
                    font.family: "Verdana"
                }

                Text {
                    id: lastAccessTimeText
                    width: projectLocation.lastAccTimeWidth
                    height: parent.height
                    text: qsTr("Last Access: " + lastAccessTime)
                    font.weight: Font.Normal
                    font.family: "Verdana"
                    font.pointSize: 10
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignRight
                }
            }
        }
    }

    ListView {
        id: listView
        anchors.rightMargin: 5
        anchors.leftMargin: 5
        anchors.bottomMargin: 5
        anchors.top: projectInfo.bottom
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.topMargin: 0
        model: listModel
        delegate:delegate
    }

    Component{
        id: delegate
        CollapsibleItem{
            width: parent.width
            height: 40
            headerName: header
            mode:panelMode
        }
    }

    ListModel {
        id: listModel
    }




}



















/*##^## Designer {
    D{i:4;anchors_height:20;anchors_width:780}D{i:3;anchors_width:790}D{i:6;anchors_height:20;anchors_width:780}
D{i:5;anchors_width:790}D{i:2;anchors_height:100;anchors_width:100}
}
 ##^##*/
