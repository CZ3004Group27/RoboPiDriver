from CameraModule import CameraModule
# from DummyCameraModule import DummyCameraModule as CameraModule
from WifiTester import receive_message_with_size
import socket
import cv2
import base64
import struct


class Server:
    HOST = ''  # Standard loopback interface address (localhost)
    PORT = 25565  # Port to listen on (non-privileged ports are > 1023)
    def __init__(self):
        self.camera = CameraModule()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.HOST, self.PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                print("wifi thread listening for commands")

                while True:
                    # Get data from wifi connection
                    data = receive_message_with_size(conn)
                    if len(data) == 0:
                        pass
                    else:
                        raw_string = data.decode("utf-8")
                        command = raw_string.split("/")
                        print(raw_string)
                        if command[0] == "PHOTO":
                            print("phototaking command received!")
                            image = self.camera.take_picture()
                            if image is not None:
                                buffer = cv2.imencode('.jpg', image)[1].tobytes()
                                #string_to_send = base64.b64encode(buffer).decode("utf-8")
                                string_to_send = "PHOTODATA/" + base64.b64encode(buffer).decode("utf-8")
                                bytes_to_send = string_to_send.encode("utf-8")
                                number_of_bytes = len(bytes_to_send)
                                print(number_of_bytes)
                                packet_length = struct.pack("!I", number_of_bytes)
                                print("sending photo image")
                                packet_length += bytes_to_send
                                conn.sendall(packet_length)
                        print("received [%s]" % data)


server = Server()
