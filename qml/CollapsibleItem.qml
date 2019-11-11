import QtQuick 2.12
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.3
import QtQuick.Controls.Material 2.2


Item {
    id: rootItem
    property var headerHeight: 50
    property var listviewHeight: 300
    property var headerName: "none"
    property var count: 0

    width: 400
    height: 4*150

    Column {
        id: column
        width: parent.width
        height: parent.height

        Rectangle {
            id: header
            width: parent.width
            height: rootItem.headerHeight
            color: "#ffffff"

            Row {
                id: row
                anchors.fill: parent
                Label {
                    id: headerLabel
                    text: headerName
                }

                Image {
                    id: pointerImage
                    width: parent.height
                    height: parent.height
                    source: "../res/collapse_up.ico"
                    fillMode: Image.PreserveAspectFit
                }
            }
        }

        Pane {
            id: collapsiblePane
            width: parent.width
            height: rootItem.listviewHeight

            ListView {
                id: listView
                property int selected_index: -1
                anchors.fill: parent

                model: listModel
                delegate: Item {
                    width: parent.width
                    height: 120
                    id: wrapper
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
                ListModel {
                    id: listModel
                }
            }
        }

    }

}










