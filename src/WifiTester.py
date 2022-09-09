from tkinter import *
from functools import partial
import socket

window = Tk()
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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"PHOTO/PHOTO")


B = Button(window, text="send test", command=buttonCallBack)

B.pack()
window.mainloop()
