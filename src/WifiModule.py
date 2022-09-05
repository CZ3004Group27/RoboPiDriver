from multiprocessing import Process, Queue
import os
import socket
from Action import *

# receives movement instructions and image result from PC, sends to it map information
class WifiModule(Process):
    wifi_string_conv_dict = {"MOVE/F": RobotAction.FORWARD,
                             "MOVE/B": RobotAction.BACKWARD,
                             "MOVE/L" : RobotAction.TURN_FORWARD_LEFT,
                             "MOVE/R" : RobotAction.TURN_FORWARD_RIGHT,
                             "MOVE/BR" : RobotAction.TURN_BACKWARD_RIGHT,
                             "Move/BL" : RobotAction.TURN_BACKWARD_LEFT
                             }
    HOST = ''  # Standard loopback interface address (localhost)
    PORT = 25565  # Port to listen on (non-privileged ports are > 1023)

    def __init__(self, stopped_queue, main_command_queue, android_command_queue, main_thread_override_queue):
        Process.__init__(self)
        self.stopped = False
        self.stopped_queue = stopped_queue
        self.main_command_queue = main_command_queue
        self.android_command_queue = android_command_queue
        self.main_thread_override_queue = main_thread_override_queue
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
                        if command.command_type == WifiAction.SEND_IMAGE:
                            self.send_image(command.data)
                    # Get data from wifi connection
                    self.receive_image(conn)
                print("stopping!")

    def send_image(self, image):
        pass

    def receive_image(self, conn):
        pass
