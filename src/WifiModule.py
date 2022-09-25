from multiprocessing import Process, Queue
import os
import socket
from Action import *
from CameraModule import CameraModule
import signal
import base64
import struct
import cv2


# receives movement instructions and image result from PC, sends to it map information


def wifi_close_module():
    try:
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(("127.0.0.1", WifiModule.PORT))
        sock.close()
    except socket.timeout:
        pass


def send_message_with_size(conn, data):
    number_of_bytes = len(data)
    packet_length = struct.pack("!I", number_of_bytes)
    packet_length += data
    conn.sendall(packet_length)


def send_image(image, conn):
    # Send image
    string_to_send = "PHOTODATA/" + base64.b64encode(cv2.imencode('.jpg', image)[1].tobytes()).decode("utf-8")
    send_message_with_size(conn, string_to_send.encode("utf-8"))


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
                                      "FL": RobotAction.TURN_FORWARD_LEFT,
                                      "FR": RobotAction.TURN_FORWARD_RIGHT,
                                      "BR": RobotAction.TURN_BACKWARD_RIGHT,
                                      "BL": RobotAction.TURN_BACKWARD_LEFT
                                      }
        self.wifi_command_dict = {"PHOTO": self.take_photo,
                                  "MOVEMENTS": self.get_movement,
                                  "TARGET": self.get_target_id,
                                  "ROBOT": self.get_movement_plan
                                  }
        self.connection_closed = False
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
            port = s.getsockname()[1]
            while not self.stopped:
                print("Waiting for connection on fake wifi channel %d" % port)
                conn, addr = s.accept()
                conn.settimeout(2)
                self.robot_action_list.put(Command(RobotAction.WIFI_CONNECTED, ""))
                self.connection_closed = False
                with conn:
                    print(f"Connected by {addr}")
                    print("wifi thread listening for commands")
                    while not self.connection_closed:
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
                        conn.settimeout(2)
                        data = self.receive_message_with_size(conn)
                        if data is not None:
                            self.parse_wifi_command(data, conn)
                            print("received [%s]" % data)

                    print("finishing connection!")
                    self.robot_action_list.put(Command(RobotAction.WIFI_DISCONNECTED, ""))

            print("stopping!")

    def send_start_mission_command(self, conn, data):
        print("trying to send start mission to wifi")
        try:
            conn.settimeout(self.TIMEOUT_PERIOD)
            send_message_with_size(conn, data)
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
        # Get list of movements and send to main thread
        moves = command[2]
        list_of_moves = moves.split(",")
        self.robot_action_list.put(Command(RobotAction.SET_MOVEMENTS, list_of_moves))

    def parse_wifi_command(self, data, conn):
        raw_string = data.decode("utf-8")
        command = raw_string.split("/")
        self.wifi_command_dict[command[0]](data, command, conn)

    def get_target_id(self, data, command, conn):
        self.robot_action_list.put(Command(RobotAction.SEND_TARGET_ID, data))

    def receive_message_with_size(self, conn):
        try:
            data = conn.recv(4)
            if len(data) == 0:
                self.connection_closed = True
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
            self.connection_closed = True
            return None
        except socket.error:
            self.connection_closed = True
            return None
        except:
            self.connection_closed = True
            return None
