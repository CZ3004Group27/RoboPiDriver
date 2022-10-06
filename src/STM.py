from Action import *
from STMModule import STMModule
import time

stm = STMModule()

stm.connect()

stm.send_movement_to_stm('a')

# stm.process_move(RobotAction.FORWARD,0,0,0)
stm.send_movement_to_stm('w')
# stm.process_move(RobotAction.TURN_FORWARD_LEFT,0,0,0)
stm.send_movement_to_stm('d')
# stm.process_move(RobotAction.TURN_FORWARD_RIGHT,0,0,0)


# stm.process_move(RobotAction.TURN_BACKWARD_LEFT,0,0,0)




# stm.process_move(RobotAction.TURN_BACKWARD_RIGHT, 0, 0, 0)


stm.disconnect()