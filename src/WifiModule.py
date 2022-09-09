from multiprocessing import Process, Queue
import os
import socket
from Action import *
from CameraModule import CameraModule



# receives movement instructions and image result from PC, sends to it map information


def send_image(image, conn):
    # Send image
    string_to_send = "PHOTODATA/" + image.tostring()
    conn.sendall(string_to_send.encode("utf-8"))


class WifiModule(Process):
    HOST = ''  # Standard loopback interface address (localhost)
    PORT = 25565  # Port to listen on (non-privileged ports are > 1023)

    def __init__(self, stopped_queue, main_command_queue, android_command_queue, main_thread_override_queue):
        Process.__init__(self)
        self.stopped = False
        self.stopped_queue = stopped_queue
        self.main_command_queue = main_command_queue
        self.android_command_queue = android_command_queue
        self.main_thread_override_queue = main_thread_override_queue
        self.camera = CameraModule()
        self.wifi_string_conv_dict = {"F": RobotAction.FORWARD,
                                      "B": RobotAction.BACKWARD,
                                      "L": RobotAction.TURN_FORWARD_LEFT,
                                      "R": RobotAction.TURN_FORWARD_RIGHT,
                                      "BR": RobotAction.TURN_BACKWARD_RIGHT,
                                      "BL": RobotAction.TURN_BACKWARD_LEFT
                                      }
        self.wifi_command_dict = {"PHOTO": self.take_photo,
                                  "MOVEMENT": self.get_movement
                                  }
        print("hello")

    # Setup behaviour
    # 1. Listen for wifi connection

    # Behaviour loop:
    # 1. check for stopped
    # 2. check if wifi is still connected
    # 3. check for pending wifi commands
    # 4. send wifi commands
    # 6. repeat loop

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                print("wifi thread listening for commands")
                while not self.stopped:
                    if not self.stopped_queue.empty():
                        self.stopped = self.stopped_queue.get()
                        if command.command_type == OverrideAction.STOP:
                            self.stopped = True
                            break
                    if not self.main_command_queue.empty():
                        command = self.main_command_queue.get()
                        if command.command_type == WifiAction.START_MISSION:
                            self.send_start_mission_command(conn, command.data)
                    # Get data from wifi connection
                    data = conn.recv(2048)
                    if len(data) == 0:
                        pass
                    else:
                        self.parse_wifi_command(data, conn)
                        print("received [%s]" % data)

                print("stopping!")

    def send_start_mission_command(self, conn, data):
        conn.sendall(str.encode(data))

    def receive_photo_result_data(self, conn):
        pass

    def take_photo(self, command, conn):
        photo = self.camera.take_picture()
        # SEND PICTURE
        send_image(photo, conn)

    def todo_receive_mission_instructions(self, data):
        output = True
        encoding = 'utf-8'
        parsed_string = data.decode(encoding)
        command = parsed_string.split("/")
        if command[0] == "ROBOT":
            output = False
            # Parse movement into list of moves
            move_list = list()
            self.main_command_queue.put(Command(RobotAction.RECEIVE_MISSION_INSTRUCTIONS, (move_list, data)))

    def get_movement(self, command, conn):
        obstacle = command[1].split("-")
        self.main_command_queue.put(Command(RobotAction.SET_OBSTACLE_POSITION, obstacle))
        # TODO:Get list of movements and send to main thread

    def parse_wifi_command(self, data, conn):
        raw_string = data.decode("utf-8")
        command = raw_string.split("/")
        self.wifi_command_dict[command[0]](command, conn)
