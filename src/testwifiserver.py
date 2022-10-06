from CameraModule import CameraModule
# from DummyCameraModule import DummyCameraModule as CameraModule
from WifiTester import receive_message_with_size, send_message_with_size
import socket
import cv2
import base64
import struct
import argparse

# parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("--testwifi", help="use test wifi server on PC and dummy camera instead of real rpi",
                    action="store_true")

FORMAT = "UTF-8"
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
                        print("received [%s]" % data)
                        raw_string = data.decode(FORMAT)
                        command = raw_string.split("/")
                        print(raw_string)
                        if command[0] == "PHOTO":
                            self.on_receiving_photo_request(conn)
                        elif command[0] == "MOVEMENTS":
                            num_move = len(command[2].split(","))
                            send_message_with_size(conn, f"DONE/{num_move}/{command[1]}".encode("utf-8"))
                        print("finish action after receiving message")
    
    def on_receiving_photo_request(self, conn):
        print("phototaking command received!")
        image = self.camera.take_picture()
        if image is None:
            print("no image taken")
            return

        self.send_photo(conn, image)

    def send_photo(self, conn, image):
        bytes_to_send = self.encode_image_to_send(image)
        send_message_with_size(conn, bytes_to_send)

    def encode_image_to_send(self, image):
        buffer = cv2.imencode('.jpg', image)[1].tobytes()
        string_to_send = "PHOTODATA/" + base64.b64encode(buffer).decode(FORMAT)
        bytes_to_send = string_to_send.encode(FORMAT)
        return bytes_to_send

if __name__ == "__main__":
    args = parser.parse_args()
    if args.testwifi:
        from DummyCameraModule import DummyCameraModule as CameraModule
    server = Server()
