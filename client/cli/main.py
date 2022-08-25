import socket
from rich.console import Console
import threading
import json
import time

console = Console()
sock = None
sockThread = None
# inUse = False

def send(data):
    global sock, console
    # print(inUse)
    # while inUse:
        # time.sleep(0.1)
    # inUse = True
    sock.send(
        json.dumps(data).encode("utf-8")
    )
    recv = sock.recv(10240).decode("utf-8")
    # inUse = False

    return json.loads(
        recv
    )



def getMsg():
    global sock, console
    while True:
        msg = send(
            {
                "mode":"getMsg",
                "data":{}
            }
        )
        try:
            for m in msg["data"]["messages"]:
                t = time.strftime(
                    "%H:%M:%S",
                    time.localtime(m["time"])
                )

                console.print(
                    f'[{t}]<[yellow]{m["from"]}[/]> {m["msg"]}'
                )
        except:
            pass

if __name__ == "__main__":
    console.print("[green]XChat CLI V2")
    sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
    )

    console.print('[blue]Connecting to the server means that you have read and agreed to the "xchat and related components use statement and Disclaimer"（ https://www.thisisxd.tk/index.php/archives/262/ ）')

    sock.connect(
        (
            console.input("[yellow]IP: "),
            int(console.input("[yellow]Port: "))
        )
    )

    loginRecv = send(
        {
            "mode":"login",
            "data":{
                "username":console.input(
                    "[yellow]User: "
                ),
                "version":"xchat-v2 cli"
            }
        }
    )

    if loginRecv["code"] == 200:
        console.print(
            "[green]Server connected!"
        )

        sockThread = threading.Thread(
            None,
            getMsg
        )
        sockThread.start()

        while True:
            sendMsg = console.input("")
            mode = "sendMsg"
            if sendMsg == "/exit":
                mode = "exit"
            elif sendMsg == "/list":
                mode = "getList"
            a = send(
                {
                    "mode":mode,
                    "data":{
                        "msg":sendMsg
                    }
                }
            )

            if mode == "getList":
                try:
                    console.print(a["data"]["list"])
                except:
                    console.print("[red]Failed to get online list, please try again.")
