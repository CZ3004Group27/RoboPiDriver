from enum import Enum


class Action(Enum):
    pass


class RobotAction(Action):
    FORWARD = 1
    BACKWARD = 2
    TURN_FORWARD_LEFT = 3
    TURN_FORWARD_RIGHT = 4
    TURN_BACKWARD_LEFT = 5
    TURN_BACKWARD_RIGHT = 6
    SET_ROBOT_POSITION_DIRECTION = 7
    SET_OBSTACLE_POSITION = 8
    TAKE_PICTURE = 9
    START_PATH = 10
    START_EXPLORE = 11


class OverrideAction(Action):
    STOP = 1


class AndroidBluetoothAction(Action):
    ROBOT_NOT_READY = 1
    ROBOT_READY = 2
    WIFI_DISCONNECTED = 3
    WIFI_CONNECTED = 4
    UPDATE_CURRENT_ACTION = 5
    UPDATE_CURRENT_LOCATION = 6
    SEND_IMAGE_WITH_RESULT = 7


class WifiAction(Action):
    SEND_IMAGE = 1


class Command:
    def __init__(self, command_type: Action, data):
        self.command_type = command_type
        self.data = data
