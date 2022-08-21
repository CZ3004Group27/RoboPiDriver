from enum import Enum


class Action(Enum):
    FORWARD = 1
    BACKWARD = 2
    TURN_LEFT = 3
    TURN_RIGHT = 4
    TURN_LEFT_INP = 5
    TURN_RIGHT_INP = 6
    TAKE_PICTURE = 7


class OverrideAction(Enum):
    STOP = 1


class CommandType(Enum):
    SEND_PICTURE = 1


class CommandAction:
    def __init__(self, command_type: CommandType, data):
        self.command_type = command_type
        self.data = data
