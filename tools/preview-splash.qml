// QT_QPA_PLATFORM=offscreen qml6 tools/preview-splash.qml -- <Splash.qml> <out.png> <stage>
import QtQuick
import QtQuick.Window
Window {
    id: win; width: 1920; height: 1080; visible: true
    readonly property var args: Qt.application.arguments.slice(Qt.application.arguments.indexOf("--") + 1)
    Loader { id: l; anchors.fill: parent; source: "file://" + win.args[0]; onLoaded: item.stage = parseInt(win.args[2]) }
    Timer { interval: 1500; running: true; onTriggered: l.item.grabToImage(function (r) { r.saveToFile(win.args[1]); Qt.quit() }) }
}
