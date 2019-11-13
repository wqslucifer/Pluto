import QtQuick 2.12
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.3
import QtQuick.Controls.Material 2.2
import QtQml.Models 2.2


Rectangle {
    id: root
    property var count: 0
    property var projectID: ''
    property var modelList: []
    property var dataList: []
    property var scriptList: []
    property var resultList: []
    property var initHeight: 60
    property var projectName: ''
    property var lastAccessTime: ''

    function onInitMainPageItems(PanelItems){
        projectID = PanelItems['ID']
        modelList = PanelItems['model']
        dataList = PanelItems['data']
        scriptList = PanelItems['script']
        resultList = PanelItems['result']
        lastAccessTime = PanelItems['lastAccessTime']

        modelPanel.onInitListItems(modelList)
        //selectPage_DM.initModel(DMPageItems)
        console.log(modelPanel.height)
        root.height = initHeight+modelPanel.height+dataPanel.height+scriptPanel.height+resultPanel.height
    }

    width: 800
    height: 60
    radius: 3
    border.width: 4
    color: 'transparent'

    Rectangle{
        id: projectInfo
        height: 60
        color: 'transparent'
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0
        Column {
            id: column
            anchors.rightMargin: 5
            anchors.leftMargin: 5
            anchors.bottomMargin: 0
            anchors.topMargin: 10
            anchors.fill: parent
            spacing: 0
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

    Rectangle {
        id: rectangle
        x: 0
        y: 60
        //color: "#ffffff"
        color: 'transparent'
        anchors.top: projectInfo.bottom
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.topMargin: 0
        clip: true
        ScrollView {
            id: scrollView
            anchors.fill: parent
            ListView {
                id: listView
                anchors.fill: parent
                model: objectModel
            }
        }
    }

    ObjectModel {
        id: objectModel
        CollapsibleItem{
            id: modelPanel
            width: root.width
            headerName: 'Model'
            mode: 'Model'
        }
        CollapsibleItem{
            id: dataPanel
            width: root.width
            headerName: 'Data'
            mode: 'Data'
        }
        CollapsibleItem{
            id: scriptPanel
            width: root.width
            headerName: 'Script'
            mode: 'Script'
        }
        CollapsibleItem{
            id: resultPanel
            width: root.width
            headerName: 'Result'
            mode: 'Result'
        }
    }





}








/*##^## Designer {
    D{i:1;anchors_height:200;anchors_width:200}
}
 ##^##*/
