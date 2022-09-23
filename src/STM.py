from Action import *
from STMModule import STMModule

stm = STMModule()
stm.process_move(RobotAction.FORWARD,0,0,0)

stm.process_move(RobotAction.FORWARDLEFT,0,0,0)

stm.process_move(RobotAction.FORWARDRIGHT,0,0,0)

stm.process_move(RobotAction.BACKWARDLEFT,0,0,0)

stm.process_move(RobotAction.BACKWARDRIGHT,0,0,0)
