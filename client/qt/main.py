from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from qt_material import apply_stylesheet
# import PySide6
import os
import os.path
import ui_main
import rich.console
import sys
import socket
import ui_connect
import time
import json

# Init
# dirname = os.path.dirname(PySide6.__file__) 
# plugin_path = os.path.join(dirname, 'plugins', 'platforms')
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
console = rich.console.Console()
address = ()
sock = None
thread1 = None
inUse = False

def send(resp_data):
    global sock, inUse
    while inUse:
        time.sleep(0.1)
    inUse = True

    sock.send(
        json.dumps(
            resp_data
        ).encode("utf-8")
    )

    return json.loads(sock.recv(10240))

# Connect
class Connect(ui_connect.Ui_Dialog, QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        apply_stylesheet(self, theme='dark_teal.xml')
        self.pushButton.clicked.connect(self.con)
        self.show()
    def con(self):
        global address,sock
        address = (
            self.lineEdit.text(),
            int(self.spinBox.text())
        )
        print(address)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        print(sock)
        recv = send(
            {
                "mode":"login",
                "data":{
                    "username":self.lineEdit_2.text(),
                    "version":"xchat-v2 qt"
                }
            }
        )
        if recv["code"] == 200:
            self.close()
        


# Main Window
class XChat(ui_main.Ui_MainWindow, QMainWindow):
    def __init__(self) -> None:
        global address
        super().__init__()
        self.setupUi(self)
        # apply_stylesheet(self, theme='dark_teal.xml')
        #self.textBrowser.setEnabled(False)
        # QTimer
        self.tim = QTimer()
        self.tim.setInterval(1)
        # Event
        self.tim.timeout.connect(self.getNewMessage)
        self.pushButton.clicked.connect(self.sendMsg)

        Connect().exec_()
        self.tim.start()

        # Title
        self.setWindowTitle("XChat - " + address[0])

        # Show
        self.show()
    
    def sendMsg(self):
        console.log(
            send(
                {
                    "mode":"sendMsg",
                    "data":{
                        "msg":self.lineEdit.text()
                    }
                }
            )
        )
        self.lineEdit.clear()
    
    def getNewMessage(self):
        msg = send(
            {
                "mode":"getMsg"
            }
        )["data"]["messages"]
        # console.log(msg)
        t = self.textBrowser.toHtml()
        len = 0
        for m in msg:
            len += 1
            t += f"[{time.strftime('%H:%M:%S', time.localtime(m['time']))}] <strong>{m['from']}</strong>: {m['msg']}"
            if len != msg.__len__():
                t += "<br>"
        self.textBrowser.setHtml(t)
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
        

# Launch
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XChat()
    sys.exit(app.exec_())


