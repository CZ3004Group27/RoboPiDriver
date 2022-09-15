from CameraModule import CameraModule
import socket
import cv2
import base64


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
                        if image is not None:
                            buffer = cv2.imencode('.jpg', image)[1].tobytes()
                            string_to_send = base64.b64encode(buffer).decode("utf-8")
                            #string_to_send = "PHOTODATA/" + base64.b64encode(buffer).decode("utf-8")
                            bytes_to_send = string_to_send.encode("utf-8")
                            number_of_bytes = len(bytes_to_send)
                            print(number_of_bytes)
                            packet_length = number_of_bytes.to_bytes(4,'big')
                            print("sending photo image")
                            packet_length += bytes_to_send
                            conn.send(packet_length)
                    print("received [%s]" % data)


server = Server()
