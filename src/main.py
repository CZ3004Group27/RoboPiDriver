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
    image = None
    robot_position_x = 0
    robot_position_y = 0

    # Initialise Wifi thread
    wifi_thread = WifiModule(wifi_stopped_queue, wifi_command_queue, android_command_queue, override_queue)
    wifi_thread.start()

    # Initialise android bluetooth thread
    android_thread = AndroidLinkModule(android_stopped_queue, android_command_queue,action_list, override_queue)
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
                move = action_list.get()
                if move == Action.TAKE_PICTURE:
                    # Take a picture with picamera
                    image = CameraModule.take_picture()
                    # Send image by bluetooth/wifi ???
                    wifi_command_queue.put(Action(WifiAction.SEND_PICTURE, image))
                else:
                    STMModule.process_move(move)
    except KeyboardInterrupt:
        wifi_stopped_queue.put(True)
        android_stopped_queue.put(True)

    wifi_thread.join()
    print("wifi thread stopped")
    android_thread.join()
    print("android thread stopped")
    print("program shutting down")
