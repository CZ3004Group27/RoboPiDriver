from multiprocessing import Process, Queue
from Action import *
import os
import time
from RobotMovementError import *


class STMModule:
    def __init__(self):
        pass

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
            time.sleep(1)
            return new_x, new_y, new_direction, moved

    def connect(self):
        pass

    def isConnected(self):
        return True

    def disconnect(self):
        pass

    def check_for_obstacle(self):
        return False
