import time
from multiprocessing import Process, Queue
from Action import *
import os

# receives map from android tablet and sends image result to tablet and robot position

if os.name == 'nt':
    class AndroidLinkModule(Process):
        TIMEOUT_PERIOD = 0.5

        def __init__(self, stopped_queue, main_command_queue,robot_action_list, main_thread_override_queue):
            Process.__init__(self)
            self.stopped = False
            self.robot_ready_status = False
            self.bluetooth_connected_status = False
            self.wifi_connected_status = False
            self.stopped_queue = stopped_queue
            self.main_command_queue = main_command_queue
            self.robot_action_list = robot_action_list
            self.main_thread_override_queue = main_thread_override_queue
            self.timeout_start = None
            self.timeout = None
            print("hello")

        # Setup behaviour
        # 1. Listen for bluetooth connection

        # Behaviour loop:
        # 1. check for stopped
        # 2. check for pending android commands
        # 3. send android commands to main thread
        # 4. run all possible commands from command thread (or timeout and send back info after 0.5? seconds)
        # 5. repeat loop
        def run(self):
            print("thread running")
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
            print("stopping!")

        def send_android_message(self, message):
            pass
else:
    from bluetooth import *


    class AndroidLinkModule(Process):
        TIMEOUT_PERIOD = 0.5

        def __init__(self, stopped_queue, main_command_queue,robot_action_queue, main_thread_override_queue):
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
            self.pathing_dict{
                "EXPLORE" : self.start_explore,
                "PATH" : self.start_path
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
            server_sock = BluetoothSocket(RFCOMM)
            server_sock.bind(("", PORT_ANY))
            server_sock.listen(1)

            port = server_sock.getsockname()[1]

            uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

            advertise_service(server_sock, "SampleServer",
                              service_id=uuid,
                              service_classes=[uuid, SERIAL_PORT_CLASS],
                              profiles=[SERIAL_PORT_PROFILE],
                              #                   protocols = [ OBEX_UUID ]
                              )

            print("Waiting for connection on RFCOMM channel %d" % port)

            client_sock, client_info = server_sock.accept()
            print("Accepted connection from ", client_info)

            print("loop running")
            with client_sock:
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
                    data = client_sock.recv(2048)
                    if len(data) == 0:
                        continue
                    else:
                        self.parse_android_message(data)
                        # Send command to main thread
                    print("received [%s]" % data)

            print("stopping!")


        def parse_android_message(self, data):
            command = data.split("/")
            self.parse_command_type(command)

        # TODO
        def send_android_message(self, message):
            pass

        # TODO
        def start_robot(self,command):
            pass
        #TODO
        def move_robot(self,command):
            pass
        def stop_robot(self,command):
            self.main_thread_override_queue.put(Command(OverrideAction.STOP,""))
        def parse_command_type(self,command):
            self.command_dict[command[0]](command)

        # TODO
        def set_robot_position(self,command):
            pass

        # TODO
        def start_explore(self,command):
            robot_position_info = map(str, command[2].replace('(','').replace(')','').split(','))

            # list goes as: [x value, y value, robot direction]
            robot_position_list = [int(robot_position_info[1]),int(robot_position_info[2]),int(robot_position_info[3])]

            #Set robot location in main thread
            self.robot_action_queue.put(Command(RobotAction.SET_ROBOT_POSITION_DIRECTION,robot_position_list))

            # Set obstacle location in main thread
            self.robot_action_queue.put(Command(RobotAction.SET_OBSTACLE_POSITION,))
        # TODO
        def start_path(self,command):
            pass

