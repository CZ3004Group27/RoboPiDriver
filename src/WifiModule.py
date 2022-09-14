from multiprocessing import Process, Queue
import os
import socket
from Action import *
from CameraModule import CameraModule
import signal
import base64


# receives movement instructions and image result from PC, sends to it map information


def send_image(image, conn):
    # Send image
    string_to_send = "PHOTODATA/" + base64.b64encode(image.tobytes()).decode("utf-8")
    conn.sendall(string_to_send.encode("utf-8"))


def wifi_close_module():
    try:
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(("127.0.0.1", WifiModule.PORT))
        sock.close()
    except socket.timeout:
        pass


class WifiModule(Process):
    HOST = ''  # Standard loopback interface address (localhost)
    PORT = 25565  # Port to listen on (non-privileged ports are > 1023)

    def __init__(self, stopped_queue, main_command_queue, robot_action_list, main_thread_override_queue):
        Process.__init__(self)
        self.stopped = False
        self.stopped_queue = stopped_queue
        self.main_command_queue = main_command_queue
        self.robot_action_list = robot_action_list
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
                                  "MOVEMENTS": self.get_movement,
                                  "TARGET": self.get_target_id,
                                  "ROBOT": self.get_movement_plan
                                  }
        print("starting wifi module")

    # Setup behaviour
    # 1. Listen for wifi connection

    # Behaviour loop:
    # 1. check for stopped
    # 2. check if wifi is still connected
    # 3. check for pending wifi commands
    # 4. send wifi commands
    # 6. repeat loop

    def run(self):
        """Ignore CTRL+C in the worker process."""
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            conn, addr = s.accept()
            conn.settimeout(2)
            self.robot_action_list.put(Command(RobotAction.WIFI_CONNECTED, ""))
            with conn:
                print(f"Connected by {addr}")
                print("wifi thread listening for commands")
                while not self.stopped:
                    if not self.stopped_queue.empty():
                        command = self.stopped_queue.get()
                        if command.command_type == OverrideAction.STOP:
                            self.stopped = True
                            break
                    if not self.main_command_queue.empty():
                        command = self.main_command_queue.get()
                        if command.command_type == WifiAction.START_MISSION:
                            self.send_start_mission_command(conn, command.data)
                    # Get data from wifi connection
                    try:
                        data = conn.recv(2048)
                        if len(data) == 0:
                            pass
                        else:
                            self.parse_wifi_command(data, conn)
                            print("received [%s]" % data)
                    except socket.timeout:
                        pass

                print("stopping!")

    def send_start_mission_command(self, conn, data):
        print("trying to send start mission to wifi")
        try:
            conn.settimeout(2)
            conn.sendall(data)
        except:
            pass

    def receive_photo_result_data(self, conn):
        pass

    def take_photo(self, data, command, conn):
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
            self.robot_action_list.put(Command(RobotAction.RECEIVE_MISSION_INSTRUCTIONS, (move_list, data)))

    def get_movement_plan(self, data, command, conn):
        self.robot_action_list.put(Command(RobotAction.SEND_MISSION_PLAN, data))

    def get_movement(self, data, command, conn):
        obstacle = command[1].split("-")
        self.robot_action_list.put(Command(RobotAction.SET_OBSTACLE_POSITION, obstacle))
        # TODO:Get list of movements and send to main thread

    def parse_wifi_command(self, data, conn):
        raw_string = data.decode("utf-8")
        command = raw_string.split("/")
        self.wifi_command_dict[command[0]](data, command, conn)

    def get_target_id(self, data, command, conn):
        self.robot_action_list.put(Command(RobotAction.SEND_TARGET_ID, data))
