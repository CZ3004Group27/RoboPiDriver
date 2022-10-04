from multiprocessing import Process, Lock, Queue
from Action import *
import socket

# from WifiModule import *
# from STMModule import STMModule
# from AndroidLinkModule import *
# from CameraModule import *

from DummyAndroidLinkModule import *
from DummyWifiModule import *
from DummySTMModule import *
from DummyCameraModule import DummyCameraModule as CameraModule


# TODO anh help pls
def run_pathing(stm):
    camera = CameraModule()
    path_robot_position_x = 0
    path_robot_position_y = 0
    path_robot_direction = 0
    # STEP 1: move robot forward until detect obstacle
    x, y, r, moved = stm.process_move(RobotAction.FORWARD_UNTIL_OBS, robot_position_x, robot_position_y,
                                      robot_direction)
    path_robot_position_x = x
    path_robot_position_y = y
    path_robot_direction = r
    # STEP 2: Detect picture
    # STEP 3: Turn left or right around obstacle depending on picture
    # STEP 4: move robot forward until detect obstacle
    # STEP 5: Detect picture
    # STEP 6: turn left or right around obstacle depending on picture
    pass


if __name__ == '__main__':
    # Initialise Variables
    stopped = False
    override_action = None
    map_array = None
    stm = STMModule()
    override_queue = Queue()
    wifi_stopped_queue = Queue()
    android_stopped_queue = Queue()
    wifi_command_queue = Queue()
    android_command_queue = Queue()
    action_list = Queue()
    obstacle_with_direction_list = list()
    movement_string_conv_dict = {"F": RobotAction.FORWARD,
                                 "B": RobotAction.BACKWARD,
                                 "FL": RobotAction.TURN_FORWARD_LEFT,
                                 "FR": RobotAction.TURN_FORWARD_RIGHT,
                                 "BR": RobotAction.TURN_BACKWARD_RIGHT,
                                 "BL": RobotAction.TURN_BACKWARD_LEFT
                                 }

    image = None
    robot_position_x = 0
    robot_position_y = 0
    robot_direction = 0
    obstacle_position_x = -1
    obstacle_position_y = -1
    movement_counter = 0

    # Initialise Wifi thread
    print("starting wifi module")
    wifi_thread = WifiModule(wifi_stopped_queue, wifi_command_queue, action_list, override_queue)
    wifi_thread.start()

    # Initialise android bluetooth thread
    print("starting bluetooth module")
    android_thread = AndroidLinkModule(android_stopped_queue, android_command_queue, action_list, override_queue)
    android_thread.start()
    android_command_queue.put(Command(AndroidBluetoothAction.ROBOT_READY, ""))
    # Main thread loop (try catch block is to intercept ctrl-c stop command so that it closes gracefully)
    try:
        while not stopped:
            # Check if there are any override commands for the threads
            if not override_queue.empty():
                override_action = override_queue.get()
                if override_action.command_type == OverrideAction.STOP:
                    print("stop command received")
                    while not action_list.empty():
                        action_list.get()
                elif override_action.command_type == OverrideAction.QUIT:
                    wifi_stopped_queue.put(True)
                    android_stopped_queue.put(True)
                    stopped = True
                    break
            # Check and run one move per loop
            if not action_list.empty():
                command = action_list.get()
                print("action received")
                print(command.command_type)
                print(command.data)
                # if action is a movement action
                if command.command_type.value <= RobotAction.TURN_BACKWARD_RIGHT.value:
                    x, y, r, moved = stm.process_move(command.command_type, robot_position_x, robot_position_y,
                                                      robot_direction)
                    robot_position_x = x
                    robot_position_y = y
                    robot_direction = r
                    if moved:
                        movement_counter += 1

                    temp_list = [robot_position_x, robot_position_y, robot_direction]
                    android_command_queue.put(Command(AndroidBluetoothAction.UPDATE_DONE,
                                                      [movement_counter, obstacle_position_x, obstacle_position_y]))
                    wifi_command_queue.put(Command(WifiAction.UPDATE_DONE,
                                                      [movement_counter, obstacle_position_x, obstacle_position_y]))

                elif command.command_type == RobotAction.SET_ROBOT_POSITION_DIRECTION:
                    temp_tuple = command.data
                    robot_position_x = temp_tuple[0]
                    robot_position_y = temp_tuple[1]
                    robot_direction = temp_tuple[2]
                elif command.command_type == RobotAction.SET_OBSTACLE_POSITION:
                    obstacle_position_x = command.data[0]
                    obstacle_position_y = command.data[1]
                elif command.command_type == RobotAction.SET_MOVEMENTS:
                    for move in command.data:
                        print(movement_string_conv_dict[move])
                        action_list.put(Command(movement_string_conv_dict[move], ""))
                elif command.command_type == RobotAction.SEND_TARGET_ID:
                    android_command_queue.put(Command(AndroidBluetoothAction.SEND_IMAGE_WITH_RESULT, command.data))
                elif command.command_type == RobotAction.START_EXPLORE:
                    movement_counter = 0
                    wifi_command_queue.put(Command(WifiAction.START_MISSION, command.data))
                elif command.command_type == RobotAction.START_PATH:
                    movement_counter = 0
                    run_pathing(stm)
                elif command.command_type == RobotAction.SEND_MISSION_PLAN:
                    android_command_queue.put(Command(AndroidBluetoothAction.SEND_MISSION_PLAN, command.data))
                elif command.command_type == RobotAction.WIFI_CONNECTED:
                    android_command_queue.put(Command(AndroidBluetoothAction.WIFI_CONNECTED, ""))
                else:
                    pass
    except KeyboardInterrupt:
        wifi_stopped_queue.put(Command(OverrideAction.STOP, 0))
        android_stopped_queue.put(Command(OverrideAction.STOP, 0))
        wifi_close_module()
        android_close_module()
    except Exception as e:
        print(e)

    print("waiting for android to stop")
    android_thread.join()
    print("android thread stopped")
    wifi_thread.join()
    print("wifi thread stopped")
    print("program shutting down")
