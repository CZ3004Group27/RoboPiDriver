from tkinter import *
from functools import partial
from threading import Thread
import socket
class window():
    def __init__(self):
        self.window = Tk()
        self.window.geometry('400x300')

        ip_label = Label(self.window, text="ip:")
        ip_text_box = Text(
            self.window,
            height=2,
            width=20
        )
        port_label = Label(self.window, text="port:")
        port_text_box = Text(
            self.window,
            height=2,
            width=20
        )
        ip_label.pack()
        ip_text_box.pack()
        port_label.pack()
        port_text_box.pack()
        self.fake_wifi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fake_bluetooth_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.wifi_socket_thread = Thread(target=self.connect_fake_wifi_server)
        self.bluetooth_socket_thread = Thread(target=self.connect_fake_bluetooth_server)
        self.stopped = False
        C = Button(self.window, text="connect to fake bluetooth server", command=lambda: self.bluetooth_socket_thread.start())
        D = Button(self.window, text="connect to fake wifi server", command=lambda: self.wifi_socket_thread.start())
        E = Button(self.window, text="send fake bluetooth server command", command=self.send_message)

        B = Button(self.window, text="send test", command=self.button_callback)

        B.pack()
        C.pack()
        D.pack()
        E.pack()
        self.window.protocol("WM_DELETE_WINDOW", self.quit)
        self.window.mainloop()


    def button_callback(self):
        print("Sending Message...")
        HOST = ip_text_box.get("1.0",'end-1c')
        PORT = int(port_text_box.get("1.0",'end-1c'))
        print(HOST)
        print(PORT)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b"PHOTO/PHOTO")

    def connect_fake_wifi_server(self):
        self.fake_wifi_socket.connect(("127.0.0.1", 25565))
        self.fake_wifi_socket.settimeout(2)
        while not self.stopped:
            try:
                data = self.fake_wifi_socket.recv(2048)
                if len(data) == 0:
                    pass
                else:
                    print("received [%s]" % data)
            except socket.timeout:
                pass
        print("stopping")

    def connect_fake_bluetooth_server(self):
        self.fake_bluetooth_socket.connect(("127.0.0.1", 50000))
        self.fake_bluetooth_socket.settimeout(2)
        while not self.stopped:
            try:
                data = self.fake_bluetooth_socket.recv(2048)
                if len(data) == 0:
                    pass
                else:
                    print("received [%s]" % data)
            except socket.timeout:
                pass

        print("stopping")

    def send_message(self):
        message = b"PHOTO/FOO"
        self.fake_wifi_socket.sendall(message)

    def quit(self):
        self.stopped = True
        if self.wifi_socket_thread.is_alive():
            self.wifi_socket_thread.join()
        if self.bluetooth_socket_thread.is_alive():
            self.bluetooth_socket_thread.join()
        self.window.destroy()

e = window()
