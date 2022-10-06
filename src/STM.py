from Action import *
from STMModule import STMModule
import time

stm = STMModule()

stm.connect()

stm.process_move(RobotAction.FORWARD,0,0,0)

stm.process_move(RobotAction.TURN_FORWARD_LEFT,0,0,0)

stm.process_move(RobotAction.TURN_FORWARD_RIGHT,0,0,0)


stm.process_move(RobotAction.TURN_BACKWARD_LEFT,0,0,0)


stm.process_move(RobotAction.TURN_BACKWARD_RIGHT, 0, 0, 0)


stm.disconnect()