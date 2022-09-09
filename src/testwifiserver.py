from CameraModule import CameraModule
import socket
import cv2


class Server:
    HOST = ''  # Standard loopback interface address (localhost)
    PORT = 25565  # Port to listen on (non-privileged ports are > 1023)
    def __init__(self):
        self.camera = CameraModule()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                print("wifi thread listening for commands")
                # Get data from wifi connection
                data = conn.recv(2048)
                if len(data) == 0:
                    pass
                else:
                    raw_string = data.decode("utf-8")
                    command = raw_string.split("/")
                    print(raw_string)
                    if command[0] == "PHOTO":
                        print("phototaking command received!")
                        image = self.camera.take_picture()
                        string_to_send = "PHOTODATA/" + image.tostring()
                        print("sending photo image")
                        print(string_to_send)
                        conn.sendall(string_to_send.encode("utf-8"))
                    print("received [%s]" % data)


server = Server()
