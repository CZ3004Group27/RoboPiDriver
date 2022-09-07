from multiprocessing import Process, Queue
from Action import *
import os

if os.name == 'nt':

    class STMModule:
        def __init__(self):
            pass

        def process_move(self, move: RobotAction, robot_position_x, robot_position_y, robot_direction):
            pass
else:
    import serial


    class STMModule:
        def __init__(self):
            # global ser
            # try:
            #    ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=3)  # Check that arduino has same baudrate of 115200
            # except:
            #    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=3)  # Check that arduino has same baudrate of 115200

            # ser.flush()
            pass

        # returns new robot position x and y and direction r
        def process_move(self, move: RobotAction, robot_position_x, robot_position_y, robot_direction):
            moved = False
            new_x = robot_position_x
            new_y = robot_position_y
            new_direction = robot_direction
            if move == RobotAction.FORWARD:
                moved = True
                pass
            elif move == RobotAction.BACKWARD:
                moved = True
                pass
            elif move == RobotAction.TURN_FORWARD_LEFT:
                moved = True
                pass
            elif move == RobotAction.TURN_FORWARD_RIGHT:
                moved = True
                pass
            elif move == RobotAction.TURN_BACKWARD_LEFT:
                moved = True
                pass
            elif move == RobotAction.TURN_FORWARD_RIGHT:
                moved = True
                pass
            if moved:
                return new_x, new_y, new_direction
