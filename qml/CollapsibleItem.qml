import QtQuick 2.12
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.3
import QtQuick.Controls.Material 2.2


Item {
    id: rootItem
    property string selectColor: '#81D4FA'
    property string hoverColor: '#6A7FFC'
    property string transparentColor: 'transparent'
    property string textColor: '#000000'
    property string itemColor1: '#B7D7FF'
    property string itemColor2: '#A0B8FF'
    property string cellColor: itemColor1
    property string saveColor: ''

    property var headerHeight: 30
    property var listviewHeight: 30
    property var headerName: "none"
    property var count: 0
    property var mode: ''
    property var isCollapsed: false
    property var colorDict: {
        'Model':'#ff8566',
        'Data':'#ffe680',
        'Script':'#b3ff99',
        'Result':'#80ccff',
    }
    function onInitListItems(listContent){
        for(var i=0; i<listContent.length; i++){
            console.log(listContent[i])
            listModel.append({itemName:listContent[i]})
        }
        rootItem.height = header.headerHeight + rootItem.listviewHeight * listContent.length
        //listModel.append()
    }

    width: 400
    height: 4*200

    Column {
        id: column
        anchors.rightMargin: 0
        anchors.leftMargin: 0
        anchors.fill: parent
        spacing: 0
        Rectangle {
            id: header
            height: headerHeight
            color: colorDict[mode]
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0
            RowLayout {
                id: rowLayout
                spacing: 0
                anchors.rightMargin: 0
                anchors.leftMargin: 0
                anchors.fill: parent
                Label {
                    id: headerLabel
                    text: headerName
                }
                Image {
                    id: pointerImage
                    width: parent.height
                    height: parent.height
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    source: "../res/collapse_up.ico"
                    fillMode: Image.PreserveAspectFit
                    Component.onCompleted: {
                        if(isCollapsed){
                            pointerImage.source = "../res/collapse_up.ico"
                        }
                        else{
                            pointerImage.source = "../res/collapse_down.ico"
                        }
                    }
                }
            }
        }

        Pane {
            id: collapsiblePane
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0
            ListView {
                id: listView
                property int selected_index: -1
                anchors.fill: parent
                model: listModel
                delegate: delegate
                ListModel {
                    id: listModel
                }
            }
            Component{
                id: delegate
                Item {
                    id: delegateItem
                    width: parent.width
                    height: 100
                    Button {
                        id: listItem
                        width: parent.width
                        height: parent.height
                        anchors.fill: parent
                        flat: true
                        highlighted: true
                        checkable: true
                        checked:true
                        property int checked_index: -1
                        background: Rectangle{
                            id: itemBgColor
                            width:parent.width
                            height: parent.height
                            color:cellColor
                        }

                        Rectangle {
                            width: parent.width
                            height: parent.height
                            color: transparentColor
                            ColumnLayout{
                                width: parent.width
                                height: parent.height
                                Layout.fillWidth: true
                                Text {
                                    text: itemName
                                    font.bold: true
                                    color: textColor
                                    font.pointSize: 15
                                    Layout.topMargin: 5
                                    Layout.leftMargin: 5
                                    Layout.minimumWidth: 200
                                }
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                listItem.checked = true
                                // listView.currentIndex = index
                            }
                            onEntered: {
                                if (index != listView.selected_index){
                                    saveColor = itemBgColor.color
                                    itemBgColor.color = hoverColor
                                }
                            }
                            onExited: {
                                if (index != listView.selected_index){
                                    itemBgColor.color = saveColor
                                }
                            }
                        }
                    }
                }
            }

        }

    }

}









































/*##^## Designer {
    D{i:3;anchors_height:20;anchors_width:400}D{i:2;anchors_width:400}D{i:6;anchors_height:30;anchors_width:800}
D{i:1;anchors_height:600;anchors_width:400}
}
 ##^##*/
