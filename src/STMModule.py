from multiprocessing import Process, Queue
from Action import *
import os
from RobotMovementError import *


import serial


class STMModule:
    def __init__(self):
        # global ser
        self.port = '/dev/ttyS0'
        self.baud = 115200
        # ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=3)  # Check that arduino has same baudrate of 115200
        # ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=3)  # Check that arduino has same baudrate of 115200
        self.isEstablished = False
        ser.flush()
        pass

    def isConnected(self):
        return self.isEstablished

    def connect(self):
        while True:
            retry = False
            try:
                # Let's wait for connection
                print('[STM_INFO] Waiting for serial connection from STM')

                self.serialConn = serial.Serial(self.commPort, self.baud, timeout=0.1)
                print('[STM_ACCEPTED] Connected to STM.')
                self.isEstablished = True
                retry = False

            except Exception as e:
                print('[STM_ERROR] Arduino Connection Error: %s' % str(e))
                retry = True

            # When established, break the while(true)
            if not retry:
                break

            # When not yet established, keep retrying
            print('[STM_INFO] Retrying STM Establishment')
            time.sleep(1)



    def forward(self):
        ser.write(str.encode("FW"))


    def forwardLeft(self):
        ser.write(str.encode("FL"))


    def forwardRight(self):
        ser.write(str.encode("FR"))


    def backwardleft(self):
        ser.write(str.encode("BL"))


    def backwardright(self):
        ser.write(str.encode("BR"))


    # returns new robot position x and y and direction r
    def process_move(self, move: RobotAction, robot_position_x, robot_position_y, robot_direction):
        moved = False
        new_x = robot_position_x
        new_y = robot_position_y
        new_direction = robot_direction
        try:
            if move == RobotAction.FORWARD:
                if self.check_for_obstacle():
                    raise RobotMovementError
                moved = True
                self.forward()
                print("moving forward!")
                new_y = new_y + (1 - robot_direction) * (int(not (robot_direction % 2)))
                new_x = new_x + (2 - robot_direction) * (int((robot_direction % 2)))
            elif move == RobotAction.BACKWARD:
                if self.check_for_obstacle():
                    raise RobotMovementError
                moved = True
                print("moving backward!")
                new_y = new_y - (1 - robot_direction) * (int(not (robot_direction % 2)))
                new_x = new_x - (2 - robot_direction) * (int((robot_direction % 2)))
            elif move == RobotAction.TURN_FORWARD_LEFT:
                if self.check_for_obstacle():
                    raise RobotMovementError
                moved = True
                self.forwardleft()
                print("moving forward left!!")
                if robot_direction == 0 or robot_direction == 1:
                    new_y = new_y + 3
                else:
                    new_y = new_y - 3

                if robot_direction == 1 or robot_direction == 2:
                    new_x = new_x + 3
                else:
                    new_x = new_x - 3
                new_direction = (new_direction - 1) % 4
            elif move == RobotAction.TURN_FORWARD_RIGHT:
                if self.check_for_obstacle():
                    raise RobotMovementError
                moved = True
                self.forwardright()
                print("moving forward right!")
                if robot_direction == 0 or robot_direction == 3:
                    new_y = new_y + 3
                else:
                    new_y = new_y - 3

                if robot_direction == 0 or robot_direction == 1:
                    new_x = new_x + 3
                else:
                    new_x = new_x - 3
                new_direction = (new_direction + 1) % 4
            elif move == RobotAction.TURN_BACKWARD_LEFT:
                if self.check_for_obstacle():
                    raise RobotMovementError
                moved = True
                self.backwardleft()
                print("moving backward left!")
                if robot_direction == 1 or robot_direction == 2:
                    new_y = new_y + 3
                else:
                    new_y = new_y - 3

                if robot_direction == 2 or robot_direction == 3:
                    new_x = new_x + 3
                else:
                    new_x = new_x - 3
                new_direction = (new_direction + 1) % 4
            elif move == RobotAction.TURN_BACKWARD_RIGHT:
                if self.check_for_obstacle():
                    raise RobotMovementError
                moved = True
                self.backwardright()
                print("moving backward right!")
                if robot_direction == 1 or robot_direction == 2:
                    new_y = new_y + 3
                else:
                    new_y = new_y - 3

                if robot_direction == 0 or robot_direction == 3:
                    new_x = new_x + 3
                else:
                    new_x = new_x - 3
                new_direction = (new_direction - 1) % 4
        except RobotMovementError:
            print("obstacle detected!")
        finally:
            return new_x, new_y, new_direction, moved

    def check_for_obstacle(self):
        return False

    def disconnect(self):
        if not (self.serialConn is None):  # if (self.serialConn):
            print('[STM_CLOSE] Shutting down STM Connection')
            self.serialConn.close()
            self.isEstablished = False

    def read(self):
        try:
            readData = self.serialConn.readline()
            self.serialConn.flush()  # Clean the pipe
            readData = readData.decode('utf-8')
            if readData == '':
                return None
            print('[STM_INFO] Received: ' + readData)
            return readData

        except Exception as e:
            print('[STM_ERROR] Receiving Error: %s' % str(e))
            if ('Input/output error' in str(e)):
                self.disconnect()
                print('[STM_INFO] Re-establishing Arduino Connection.')
                self.connect()

    # The fundamental trying to send
    def write(self, message):
        try:
            # Make sure there is a connection first before sending
            if self.isEstablished:
                print("STM", message)
                message = message.encode('utf-8')
                self.serialConn.write(message)
                return

            # There is no connections. Send what?
            else:
                print('[STM_INVALID] No STM Connections')

        except Exception as e:
            print('[STM_ERROR] Cannot send message: %s' % str(e))
