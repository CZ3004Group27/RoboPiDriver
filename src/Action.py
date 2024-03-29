from enum import IntEnum


class Action(IntEnum):
    pass


class RobotAction(IntEnum):
    FORWARD = 1
    BACKWARD = 2
    TURN_FORWARD_LEFT = 3
    TURN_FORWARD_RIGHT = 4
    TURN_BACKWARD_LEFT = 5
    TURN_BACKWARD_RIGHT = 6
    SET_ROBOT_POSITION_DIRECTION = 7
    SET_OBSTACLE_POSITION = 8
    SET_MOVEMENTS = 9
    SEND_TARGET_ID = 10
    FORWARD_UNTIL_OBS = 11
    START_EXPLORE = 12
    START_PATH = 13
    SEND_MISSION_PLAN = 14 # (list of moves, original string command)
    WIFI_DISCONNECTED = 15
    WIFI_CONNECTED = 16
    SEND_FINISH = 17


class OverrideAction(IntEnum):
    STOP = 1
    QUIT = 2


class AndroidBluetoothAction(IntEnum):
    ROBOT_NOT_READY = 1
    ROBOT_READY = 2
    WIFI_DISCONNECTED = 3
    WIFI_CONNECTED = 4
    UPDATE_CURRENT_ACTION = 5
    UPDATE_DONE = 6
    SEND_IMAGE_WITH_RESULT = 7
    SEND_MISSION_PLAN = 8
    SEND_FINISH = 9


class WifiAction(IntEnum):
    START_MISSION = 1
    UPDATE_DONE = 2
    SEND_PICTURE = 3


class Command:
    def __init__(self, command_type: Action, data):
        self.command_type = command_type
        self.data = data
