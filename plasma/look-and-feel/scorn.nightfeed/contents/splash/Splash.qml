/*
 * Nightfeed — KSplash. The tape rewinds, then plays; tape blocks fill as
 * Plasma's six startup stages arrive.
 */
import QtQuick

Rectangle {
    id: root
    color: "#03040a"
    property int stage
    readonly property real u: height / 1080
    readonly property real progress: Math.min(1, stage / 6)
    property int noiseFrame: 0

    FontLoader { id: osd; source: "images/TerminessNerdFontMono-Bold.ttf" }
    readonly property string mono: osd.status === FontLoader.Ready ? osd.font.family : "monospace"

    Timer { interval: 70; running: true; repeat: true; onTriggered: root.noiseFrame = (root.noiseFrame + 1 + Math.floor(Math.random() * 3)) % 4 }

    Image { anchors.fill: parent; source: "images/background-dim.jpg"; fillMode: Image.PreserveAspectCrop; horizontalAlignment: Image.AlignLeft }
    Image { anchors.fill: parent; source: "images/scanlines-1080.png"; smooth: false }
    Image { anchors.fill: parent; source: "images/noise_" + root.noiseFrame + ".png"; opacity: 0.5; smooth: false }
    Image {
        width: parent.width; height: 90 * root.u; source: "images/tracking.png"; opacity: 0.8
        // fast roll while "rewinding", then a slow drift
        NumberAnimation on y { from: -100 * root.u; to: root.height; duration: root.stage < 3 ? 1400 : 8000; loops: Animation.Infinite }
    }
    Image { anchors.fill: parent; source: "images/vignette.png" }

    component Osd: Item {
        property alias text: core.text
        property real size: 30
        property color ink: "#e6e8ff"
        implicitWidth: core.implicitWidth; implicitHeight: core.implicitHeight
        Text { x: -1.5 * root.u; text: core.text; font: core.font; color: "#7b5cff"; opacity: 0.45 }
        Text { x: 1.5 * root.u; y: 1 * root.u; text: core.text; font: core.font; color: "#7b5cff"; opacity: 0.3 }
        Text { id: core; font.family: root.mono; font.bold: true; font.pixelSize: size * root.u; font.letterSpacing: 2 * root.u; color: parent.ink }
    }

    Osd {
        x: 56 * root.u; y: 56 * root.u; size: 46
        text: root.stage < 3 ? "REW ◀◀" : "PLAY ▶"
    }

    Item {
        x: root.width * 0.705 - width / 2
        anchors.verticalCenter: parent.verticalCenter
        width: 560 * root.u; height: 200 * root.u
        Image { source: "images/glow.png"; anchors.centerIn: parent; width: parent.width * 1.5; height: parent.height * 1.8; opacity: 0.16 }
        Osd { id: logo; anchors.horizontalCenter: parent.horizontalCenter; y: 20 * root.u; size: 64; text: "NIGHTFEED" }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter; anchors.top: logo.bottom; anchors.topMargin: 10 * root.u
            text: root.stage < 3 ? "REWINDING" : "SIGNAL LOCKED"
            font.family: root.mono; font.pixelSize: 18 * root.u; font.letterSpacing: 5 * root.u; color: "#7a80b0"
        }
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            y: logo.y + logo.height + 54 * root.u
            spacing: 5 * root.u
            Repeater {
                model: 32
                Rectangle {
                    width: 11 * root.u; height: 20 * root.u
                    readonly property bool lit: index < Math.round(root.progress * 32)
                    color: lit ? "#7b5cff" : "#1e2552"
                    Rectangle { visible: parent.lit; width: parent.width; height: 1; color: "#c4b5ff" }
                    Behavior on color { ColorAnimation { duration: 200 } }
                }
            }
        }
    }

    OpacityAnimator on opacity { id: intro; from: 0; to: 1; duration: 300; running: true }
}
