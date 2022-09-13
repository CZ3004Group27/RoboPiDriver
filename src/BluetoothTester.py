from tkinter import *
import bluetooth
from functools import partial
import socket

window = Tk()
window.title("bluetooth tester")
window.geometry('400x300')

ip_label = Label(window, text="ip:")
ip_text_box = Text(
    window,
    height=2,
    width=20
)
port_label = Label(window, text="port:")
port_text_box = Text(
    window,
    height=2,
    width=20
)
ip_label.pack()
ip_text_box.pack()
port_label.pack()
port_text_box.pack()


def buttonCallBack():
    print("Sending Message...")
    HOST = ip_text_box.get("1.0",'end-1c')
    PORT = int(port_text_box.get("1.0",'end-1c'))
    print(HOST)
    print(PORT)
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((HOST, PORT))
    sock.send(b"Hello, world")
    sock.settimeout(2)
    try:
        data = sock.recv(2048)
        if len(data) == 0:
            pass
        else:
            print("received [%s] from bluetooth" % data)
    except socket.timeout:
        pass


B = Button(window, text="send test", command=buttonCallBack)

B.pack()
nearby_devices = bluetooth.discover_devices(
    duration=8, lookup_names=True, flush_cache=True, lookup_class=False)
for addr, name in nearby_devices:
    print(addr)

window.mainloop()