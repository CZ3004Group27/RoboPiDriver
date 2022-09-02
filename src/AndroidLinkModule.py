import time
from multiprocessing import Process, Queue
from Action import *
import os

if os.name == 'nt':
    class AndroidLinkModule(Process):
        TIMEOUT_PERIOD = 0.5

        def __init__(self, stopped_queue, main_command_queue, main_thread_override_queue):
            Process.__init__(self)
            self.stopped = False
            self.robot_ready_status = False
            self.bluetooth_connected_status = False
            self.wifi_connected_status = False
            self.stopped_queue = stopped_queue
            self.main_command_queue = main_command_queue
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

        def __init__(self, stopped_queue, main_command_queue, main_thread_override_queue):
            Process.__init__(self)
            self.stopped = False
            self.robot_ready_status = False
            self.bluetooth_connected_status = False
            self.wifi_connected_status = False
            self.stopped_queue = stopped_queue
            self.main_command_queue = main_command_queue
            self.main_thread_override_queue = main_thread_override_queue
            self.timeout_start = None
            self.timeout = None

        # Setup behaviour
        # 1. Listen for bluetooth connection

        # Behaviour loop:
        # 1. check for stopped
        # 2. check if bluetooth is still connected
        # 3. run all possible commands from command thread (or timeout and send back info after 0.5? seconds)
        # 4. check for pending android commands
        # 5. send android commands to main thread
        # 6. repeat loop
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
            pass
        def send_android_message(self, message):
            pass
