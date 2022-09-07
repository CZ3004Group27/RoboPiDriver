from multiprocessing import Process, Lock, Queue
from WifiModule import WifiModule
from STMModule import STMModule
from AndroidLinkModule import AndroidLinkModule
from CameraModule import CameraModule
from Action import *
import cv2

if __name__ == '__main__':
    # Initialise Variables
    stopped = False
    override_action = None
    map_array = None
    camera = CameraModule()
    stm = STMModule()
    override_queue = Queue()
    wifi_stopped_queue = Queue()
    android_stopped_queue = Queue()
    wifi_command_queue = Queue()
    android_command_queue = Queue()
    action_list = Queue()
    obstacle_with_direction_list = list()

    image = None
    robot_position_x = 0
    robot_position_y = 0
    robot_direction = 0

    # Initialise Wifi thread
    wifi_thread = WifiModule(wifi_stopped_queue, wifi_command_queue, android_command_queue, override_queue)
    wifi_thread.start()

    # Initialise android bluetooth thread
    android_thread = AndroidLinkModule(android_stopped_queue, android_command_queue, action_list, override_queue)
    android_thread.start()

    # Main thread loop (try catch block is to intercept ctrl-c stop command so that it closes gracefully)
    try:
        while not stopped:
            # Check if there are any override commands for the threads
            if not override_queue.empty():
                override_action = override_queue.get()
                if override_action == OverrideAction.STOP:
                    wifi_stopped_queue.put(True)
                    android_stopped_queue.put(True)
                    stopped = True
                    break
            # Check and run one move per loop
            if not action_list.empty():
                command = action_list.get()
                # if action is a movement action
                if int(command.command_type) <= int(RobotAction.TURN_BACKWARD_RIGHT):
                    x, y, r = STMModule.process_move(command.command_type, robot_position_x, robot_position_y, robot_direction)
                    robot_position_x = x
                    robot_position_y = y
                    robot_direction = r

                    temp_list = [robot_position_x, robot_position_y, robot_direction]

                    wifi_command_queue.put(Command(WifiAction.UPDATE_CURRENT_LOCATION, temp_list))
                    android_command_queue.put(Command(AndroidBluetoothAction.UPDATE_CURRENT_LOCATION, temp_list))

                elif command.command_type == RobotAction.SET_ROBOT_POSITION_DIRECTION:
                    temp_tuple = command.data
                    robot_position_x = temp_tuple[0]
                    robot_position_y = temp_tuple[1]
                    robot_direction = temp_tuple[2]
                elif command.command_type == RobotAction.SET_OBSTACLE_POSITION:
                    # TODO:
                    pass
                # if action is a picture action
                elif command.command_type == RobotAction.TAKE_PICTURE:
                    # Take a picture with picamera
                    image = CameraModule.take_picture()
                    # Send image by bluetooth/wifi ???
                    wifi_command_queue.put(Command(WifiAction.SEND_IMAGE, image))
                elif command.command_type == RobotAction.START_MISSION:
                    wifi_command_queue.put(Command(WifiAction.START_MISSION, command.data))
                else:
                    pass
    except KeyboardInterrupt:
        wifi_stopped_queue.put(True)
        android_stopped_queue.put(True)

    wifi_thread.join()
    print("wifi thread stopped")
    android_thread.join()
    print("android thread stopped")
    print("program shutting down")
