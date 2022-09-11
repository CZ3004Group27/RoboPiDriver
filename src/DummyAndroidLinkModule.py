import time
from multiprocessing import Process, Queue
from Action import *
import os
import socket
import signal


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
            "MOVE": self.move_robot
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

        print("Waiting for connection on fake wifi RFCOMM channel %d" % port)

        client_sock, client_info = server_sock.accept()

        client_sock.settimeout(2)
        print("Accepted connection from ", client_info)
        self.bluetooth_connected_status = True

        print("bluetooth loop running")
        while not self.stopped:
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
            #
            try:
                data = client_sock.recv(2048)
                if len(data) == 0:
                    pass
                else:
                    # self.parse_android_message(data)
                    # Send command to main thread
                    print("received [%s]" % data)
            except socket.timeout:
                pass
            except:
                pass

            try:
                string_to_send = "STATUS/" + str(self.robot_ready_status) + "/" + str(self.wifi_connected_status)
                print(string_to_send)
                client_sock.settimeout(2)
                client_sock.send(str.encode(string_to_send))
            except socket.timeout:
                pass
            except:
                pass

        print("stopping!")
        client_sock.close()
        server_sock.close()
        self.bluetooth_connected_status = False

    def parse_android_message(self, data):
        encoding = 'utf-8'
        parsed_string = data.decode(encoding)
        print(parsed_string)
        command = parsed_string.split("/")
        self.parse_command_type(command, data)

    # TODO
    def send_android_message(self, message):
        pass

    def start_robot(self, command):
        # Run command based on explore or fastest path
        self.pathing_dict[command[1]](command)

    def move_robot(self, command):
        movement_value = self.robot_move_dict[command[1]]
        self.main_command_queue.put(Command(movement_value, ""))

    def stop_robot(self, command):
        self.main_thread_override_queue.put(Command(OverrideAction.STOP, ""))

    def parse_command_type(self, command, data):
        # Run command based on start/stop/move
        self.command_dict[command[0]](command, data)

    def set_robot_position(self, command, data):
        robot_position_info = map(str, command[2].replace('(', '').replace(')', '').split(','))

        # list goes as: [x value, y value, robot direction]
        robot_position_list = [int(robot_position_info[1]), int(robot_position_info[2]),
                               int(robot_position_info[3])]
        print("setting robot position")
        # Set robot location in main thread
        self.robot_action_queue.put(Command(RobotAction.SET_ROBOT_POSITION_DIRECTION, robot_position_list))

    def start_explore(self, command, data):
        self.set_robot_position(command)
        self.start_mission(command, data)

    def start_path(self, command, data):
        self.start_mission(command, data)

    def start_mission(self, command, data):
        print("starting mission")
        self.robot_action_queue.put(Command(RobotAction.START_MISSION, data))