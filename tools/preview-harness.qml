// Renders Main.qml off-screen with stand-ins for the SDDM context objects.
//   QT_QPA_PLATFORM=offscreen qml6 tools/preview-harness.qml -- <theme dir> <out.png> [user] [typed]
import QtQuick
import QtQuick.Window

Window {
    id: win
    width: 1920; height: 1080; visible: true; color: "black"
    readonly property var args: Qt.application.arguments.slice(Qt.application.arguments.indexOf("--") + 1)

    QtObject {
        id: sddm
        property bool canSuspend: true
        property bool canReboot: true
        property bool canPowerOff: true
        property string hostName: "vvardenfell"
        signal loginFailed()
        signal loginSucceeded()
        function login(u, p, i) { loginFailed() }
        function suspend() {} function reboot() {} function powerOff() {}
    }
    QtObject { id: userModel; property string lastUser: win.args[2] || "" }
    ListModel {
        id: sessionModel
        property int lastIndex: 0
        ListElement { name: "Plasma (Wayland)" }
        ListElement { name: "Plasma (X11)" }
    }
    QtObject { id: config }

    Loader {
        id: theme
        anchors.fill: parent
        source: "file://" + win.args[0] + "/Main.qml"
        onStatusChanged: if (status === Loader.Error) { console.error("theme failed to load"); Qt.exit(2) }
    }
    Timer {
        interval: 3000; running: true
        onTriggered: {
            if (win.args[3]) theme.item.passField.text = win.args[3]
            if (win.args[4] === "fail") sddm.login("", "", 0)
            grab.start()
        }
    }
    Timer {
        id: grab; interval: 900
        onTriggered: theme.item.grabToImage(function (r) { r.saveToFile(win.args[1]); Qt.quit() })
    }
}
