from multiprocessing import Process, Queue
from Action import *
import os

if os.name == 'nt':

    class STMModule:
        def __init__(self):
            pass

        def process_move(self, move: RobotAction):
            pass
else:
    import serial
    class STMModule:
        def __init__(self):
            global ser
            try:
                ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=3)  # Check that arduino has same baudrate of 115200
            except:
                ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=3)  # Check that arduino has same baudrate of 115200

            ser.flush()

        def process_move(self, move: RobotAction):
            pass
