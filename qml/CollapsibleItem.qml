import QtQuick 2.12
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.3
import QtQuick.Controls.Material 2.2


Item {
    id: rootItem
    property var headerHeight: 20
    property var listviewHeight: 300
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

    property var componentDict: {
        'Model':modelDelegate,
        'Data':dataDelegate,
        'Script':scriptDelegate,
        'Result':resultDelegate,
    }

    function onInitListItems(items){

    }

    width: 400
    height: 4*150

    ColumnLayout {
        id: columnLayout
        anchors.fill: parent

        Rectangle {
            id: header
            height: headerHeight
            color: colorDict[mode]
            Layout.alignment: Qt.AlignHCenter | Qt.AlignTop
            Layout.fillHeight: false
            Layout.fillWidth: true

            RowLayout {
                id: rowLayout
                anchors.rightMargin: 5
                anchors.leftMargin: 5
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
            width: parent.height
            height: rootItem.listviewHeight
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignHCenter | Qt.AlignTop

            ListView {
                id: listView
                property int selected_index: -1
                anchors.rightMargin: 5
                anchors.leftMargin: 5
                anchors.fill: parent

                model: listModel
                delegate: componentDict[mode]
                ListModel {
                    id: listModel
                }
            }
            Component{
                id: modelDelegate
                Item {
                    id: modelDelegateItem
                    width: parent.width
                    height: 120
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
            Component{
                id: dataDelegate
                Item {
                    id: dataDelegateItem
                    width: parent.width
                    height: 120
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
                    }
                }
            }
            Component{
                id: scriptDelegate
                Item {
                    id: dataDelegateItem
                    width: parent.width
                    height: 120
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
                    }
                }
            }
            Component{
                id: resultDelegate
                Item {
                    id: dataDelegateItem
                    width: parent.width
                    height: 120
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
                    }
                }
            }
        }

    }

}



















/*##^## Designer {
    D{i:3;anchors_height:20;anchors_width:400}D{i:2;anchors_width:400}D{i:6;anchors_width:400}
D{i:1;anchors_height:600;anchors_width:400}
}
 ##^##*/
