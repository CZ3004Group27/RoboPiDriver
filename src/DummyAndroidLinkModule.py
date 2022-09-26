import time
from multiprocessing import Process, Queue
from Action import *
import os
import socket
import signal
import struct


def send_message_with_size(conn, data):
    number_of_bytes = len(data)
    packet_length = struct.pack("!I", number_of_bytes)
    packet_length += data
    conn.sendall(packet_length)


def android_close_module():
    try:
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(("127.0.0.1", AndroidLinkModule.PORT))

        sock.close()
    except socket.timeout:
        pass


class AndroidLinkModule(Process):
    TIMEOUT_PERIOD = 0.5
    PORT = 50000

    def __init__(self, stopped_queue, main_command_queue, robot_action_queue, main_thread_override_queue):
        Process.__init__(self)
        self.stopped = False
        self.robot_ready_status = False
        self.bluetooth_connected_status = False
        self.wifi_connected_status = False
        self.stopped_queue = stopped_queue
        self.main_command_queue = main_command_queue
        self.robot_action_queue = robot_action_queue
        self.main_thread_override_queue = main_thread_override_queue
        self.timeout_start = None
        self.timeout = None
        self.command_dict = {
            "START": self.start_robot,
            "STOP": self.stop_robot,
            "MOVE": self.move_robot,
            "ROBOT_STATUS": self.update_robot_position
        }
        self.robot_move_dict = {"F": RobotAction.FORWARD,
                                "B": RobotAction.BACKWARD,
                                "L": RobotAction.TURN_FORWARD_LEFT,
                                "R": RobotAction.TURN_FORWARD_RIGHT,
                                "BR": RobotAction.TURN_BACKWARD_RIGHT,
                                "BL": RobotAction.TURN_BACKWARD_LEFT
                                }
        self.pathing_dict = {
            "EXPLORE": self.start_explore,
            "PATH": self.start_path
        }
        self.direction_conv_dict = {
            "0": 0,
            "180": 2,
            "-90": 1,
            "90": 3
        }
        self.connection_closed = False

    # Setup behaviour
    # 1. Listen for bluetooth connection

    # Behaviour loop:
    # 1. check for stopped
    # 2. check if bluetooth is still connected
    # 3. run all possible commands from command thread (or timeout and send back info after 0.5? seconds)
    # 4. check for pending android commands
    # 5. send android commands to main thread
    # 6. send android robot status
    # 7. repeat loop
    def run(self):
        """Ignore CTRL+C in the worker process."""
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(("", self.PORT))
        server_sock.listen(1)

        port = server_sock.getsockname()[1]

        while not self.stopped:
            print("Waiting for connection on fake wifi RFCOMM channel %d" % port)
            server_sock.settimeout(2)
            try:
                client_sock, client_info = server_sock.accept()

                print("Accepted connection from ", client_info)
                self.bluetooth_connected_status = True
                self.connection_closed = False

                print("bluetooth loop running")
                while not self.connection_closed:
                    # 1. check for stopped
                    if not self.stopped_queue.empty():
                        command = self.stopped_queue.get()
                        if command.command_type == OverrideAction.STOP:
                            self.stopped = True
                            break

                    # 4. run all possible commands from command thread or until timeout
                    self.timeout_start = time.time()
                    if not self.main_command_queue.empty():
                        self.timeout = time.time() - self.timeout_start

                        # Get out of loop if time has surpassed TIMEOUT_PERIOD
                        if self.timeout > self.TIMEOUT_PERIOD:
                            break

                        command = self.main_command_queue.get()

                        # COMMAND SWITCH BLOCK
                        if command.command_type == AndroidBluetoothAction.ROBOT_NOT_READY:
                            self.robot_ready_status = False
                        elif command.command_type == AndroidBluetoothAction.ROBOT_READY:
                            self.robot_ready_status = True
                        elif command.command_type == AndroidBluetoothAction.WIFI_DISCONNECTED:
                            self.wifi_connected_status = False
                        elif command.command_type == AndroidBluetoothAction.WIFI_CONNECTED:
                            self.wifi_connected_status = True
                        elif command.command_type == AndroidBluetoothAction.UPDATE_DONE:
                            self.send_done(command.data, client_sock)
                        elif command.command_type == AndroidBluetoothAction.SEND_IMAGE_WITH_RESULT:
                            self.send_android_message(command.data, client_sock)
                        elif command.command_type == AndroidBluetoothAction.SEND_MISSION_PLAN:
                            self.send_android_message(command.data, client_sock)

                    client_sock.settimeout(self.TIMEOUT_PERIOD)
                    data = self.receive_message_with_size(client_sock)
                    if data is not None:
                        self.parse_android_message(data)
                        # Send command to main thread
                        print("received [%s]" % data)

                    try:
                        string_to_send = "STATUS/" + str(self.robot_ready_status) + "/" + str(self.wifi_connected_status)
                        client_sock.settimeout(2)
                        send_message_with_size(client_sock, str.encode(string_to_send))
                        print(string_to_send)
                    except socket.timeout:
                        pass
                    except:
                        pass

                print("finishing connection!")
                client_sock.close()
                self.bluetooth_connected_status = False
            except socket.timeout:
                if not self.stopped_queue.empty():
                    command = self.stopped_queue.get()
                    if command.command_type == OverrideAction.STOP:
                        self.stopped = True
                        break

        print("stopping!")
        server_sock.close()

    def parse_android_message(self, data):
        encoding = 'utf-8'
        parsed_string = data.decode(encoding)
        print(parsed_string)
        command = parsed_string.split("/")
        self.parse_command_type(command, data)

    def send_android_message(self, message, conn):
        try:
            conn.settimeout(self.TIMEOUT_PERIOD)
            send_message_with_size(conn, message)
        except socket.timeout:
            pass
        except:
            pass

    def start_robot(self, command, data):
        # Run command based on explore or fastest path
        print("starting mission")
        self.pathing_dict[command[1]](command, data)

    def move_robot(self, command, data):
        movement_value = self.robot_move_dict[command[1]]
        self.robot_action_queue.put(Command(movement_value, ""))

    def stop_robot(self, command, data):
        print("stopping robot")
        self.main_thread_override_queue.put(Command(OverrideAction.STOP, ""))

    def parse_command_type(self, command, data):
        # Run command based on start/stop/move
        self.command_dict[command[0]](command, data)

    def set_robot_position(self, command, data):
        robot_position_info = map(str, command[2].replace('(', '').replace(')', '').split(','))
        robot_position_info_list = list(robot_position_info)

        # list goes as: [x value, y value, robot direction]
        robot_position_list = [int(robot_position_info_list[1]), int(robot_position_info_list[2]),
                               self.direction_conv_dict[robot_position_info_list[3]]]
        print("setting robot position")
        # Set robot location in main thread
        self.robot_action_queue.put(Command(RobotAction.SET_ROBOT_POSITION_DIRECTION, robot_position_list))

    def start_explore(self, command, data):
        print("starting explore")
        self.set_robot_position(command, data)
        self.start_mission(command, data)

    def start_path(self, command, data):
        print("starting path")
        self.start_mission(command, data)

    def start_mission(self, command, data):
        print("starting mission")
        self.robot_action_queue.put(Command(RobotAction.START_MISSION, data))

    def update_robot_position(self, command, data):
        robot_position_info = map(str, command[1].replace('(', '').replace(')', '').split(','))
        robot_position_info_list = list(robot_position_info)

        # list goes as: [x value, y value, robot direction]
        robot_position_list = [int(robot_position_info_list[1]), int(robot_position_info_list[2]),
                               int(robot_position_info_list[3])]
        print("setting robot position")
        # Set robot location in main thread
        self.robot_action_queue.put(Command(RobotAction.SET_ROBOT_POSITION_DIRECTION, robot_position_list))

    def send_done(self, command, conn):
        try:
            number_of_movements = command[0]
            obstacle_x = command[1]
            obstacle_y = command[2]
            string = "DONE/" + str(number_of_movements) + "/" + str(obstacle_x)+ "-"+str(obstacle_y)
            message = string.encode("utf-8")
            conn.settimeout(2)
            send_message_with_size(conn, message)
        except socket.timeout:
            pass
        except:
            pass

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
