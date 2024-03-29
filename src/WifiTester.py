from tkinter import *
from functools import partial
from threading import Thread
import socket
import base64
import cv2
import numpy as np
import struct

def receive_message_with_size(conn):
    try:
        data = conn.recv(4)
        if len(data) == 0:
            return None
        else:
            number_of_bytes = struct.unpack("!I", data)[0]
            received_packets = b''
            bytes_to_receive = number_of_bytes
            while len(received_packets) < number_of_bytes:
                packet = conn.recv(bytes_to_receive)
                bytes_to_receive -= len(packet)
                received_packets += packet
            return received_packets
    except socket.timeout:
        return None
    except:
        return None

def send_message_with_size(conn, data):
    number_of_bytes = len(data)
    packet_length = struct.pack("!I", number_of_bytes)
    packet_length += data
    conn.sendall(packet_length)
class window():
    def __init__(self):
        self.window = Tk()
        self.window.geometry('400x300')

        self.ip_label = Label(self.window, text="ip:")
        self.ip_text_box = Text(
            self.window,
            height=2,
            width=20
        )
        self.port_label = Label(self.window, text="port:")
        self.port_text_box = Text(
            self.window,
            height=2,
            width=20
        )
        self.message_label = Label(self.window, text="message:")
        self.message_text_box = Text(
            self.window,
            height=2,
            width=20
        )
        self.ip_label.pack()
        self.ip_text_box.pack()
        self.message_label.pack()
        self.message_text_box.pack()
        self.port_label.pack()
        self.port_text_box.pack()
        self.fake_wifi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fake_bluetooth_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.wifi_socket_thread = Thread(target=self.connect_fake_wifi_server)
        self.bluetooth_socket_thread = Thread(target=self.connect_fake_bluetooth_server)
        self.stopped = False
        C = Button(self.window, text="connect to fake bluetooth server", command=lambda: self.bluetooth_socket_thread.start())
        D = Button(self.window, text="connect to fake wifi server", command=lambda: self.wifi_socket_thread.start())
        E = Button(self.window, text="send fake wifi server command", command=self.send_wifi_message)
        F = Button(self.window, text="send fake bluetooth server command", command=self.send_bluetooth_message)
        G = Button(self.window, text="close connection", command=self.close_fake_wifi_server)

        B = Button(self.window, text="send test", command=self.button_callback)

        B.pack()
        C.pack()
        D.pack()
        E.pack()
        F.pack()
        G.pack()
        self.window.protocol("WM_DELETE_WINDOW", self.quit)
        self.window.mainloop()


    def button_callback(self):
        print("Sending Message...")
        HOST = self.ip_text_box.get("1.0",'end-1c')
        PORT = int(self.port_text_box.get("1.0",'end-1c'))
        print(HOST)
        print(PORT)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.settimeout(2)
            s.send(b"PHOTO/PHOTO")
            try:
                data = receive_message_with_size(s)
                if data is not None:
                    #print("received [%s] from wifi" % data)
                    raw_string = data.decode("utf-8")
                    raw_string = raw_string[10:]
                    img_bytes = base64.b64decode(raw_string.encode("utf-8"))
                    jpg_as_np = np.frombuffer(img_bytes, dtype=np.uint8)
                    img = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
                    ## DISPLAY IMAGE
                    cv2.imshow('s', img)
                    #im_cv = cv2.imread("dummycatimage.jpg")

                    #print('Same image: {}'.format(np.all(im_cv == img)))
            except socket.timeout:
                pass

    def connect_fake_wifi_server(self):
        self.fake_wifi_socket.connect(("127.0.0.1", 25565))
        self.fake_wifi_socket.settimeout(2)
        while not self.stopped:
            try:
                data = receive_message_with_size(self.fake_wifi_socket)
                if data is not None:
                    print("received [%s] from wifi" % data)
            except socket.timeout:
                pass
        self.fake_wifi_socket.close()
        print("stopping")
    def close_fake_wifi_server(self):
        self.fake_wifi_socket.close()

    def connect_fake_bluetooth_server(self):
        self.fake_bluetooth_socket.connect(("127.0.0.1", 50000))
        self.fake_bluetooth_socket.settimeout(2)
        while not self.stopped:
            try:
                data = receive_message_with_size(self.fake_bluetooth_socket)
                if data is not None:
                    print("received [%s] from bluetooth" % data)
            except socket.timeout:
                pass
        self.fake_bluetooth_socket.close()
        print("stopping")

    def send_wifi_message(self):
        message = self.message_text_box.get("1.0", 'end-1c')
        send_message_with_size(self.fake_wifi_socket, message.encode("utf-8"))

    def send_bluetooth_message(self):
        message = self.message_text_box.get("1.0", 'end-1c')
        send_message_with_size(self.fake_bluetooth_socket, message.encode("utf-8"))

    def quit(self):
        self.stopped = True
        if self.wifi_socket_thread.is_alive():
            self.wifi_socket_thread.join()
        if self.bluetooth_socket_thread.is_alive():
            self.bluetooth_socket_thread.join()
        self.window.destroy()

if __name__ == "__main__":
    e = window()
