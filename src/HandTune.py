from multiprocessing import Process, Lock, Queue
from Action import *

from STMModule import STMModule
from CameraModule import *


class Main:
    def __init__(self):
        # Initialise Variables
        self.stopped = False
        self.stm = STMModule()
        self.stm.connect()

        try:
            while not self.stopped:
                command = input("Write function call on stm, in format <function>,<param1>,<param2>,ect")
                self.stm.send_function_and_args_to_stm(command)
        except Exception as e:
            print(e)

        if self.stm.isConnected():
            self.stm.disconnect()
        print("program shutting down")

if __name__ == '__main__':
    main = Main()
