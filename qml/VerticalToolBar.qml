import QtQuick 2.12
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3

Item {
    width: 50
    height: 400

    TabBar {
        id: tabBar
        anchors.fill: parent
        transform: Rotation { origin.x: 0; origin.y: 0; angle: -90}

        TabButton {
            id: tabButton
            text: qsTr("Tab Button")
        }

        TabButton {
            id: tabButton1
            text: qsTr("Tab Button")
        }
    }
}
