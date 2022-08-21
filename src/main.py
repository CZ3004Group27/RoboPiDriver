from multiprocessing import Process, Lock, Queue
from WifiModule import WifiModule

if __name__ == '__main__':
    stopped = False
    current_action = None
    main_queue = Queue()
    wifi_stopped_queue = Queue()
    move_list = Queue()

    wifi_thread = WifiModule(wifi_stopped_queue, main_queue)
    wifi_thread.start()
    while not stopped:
        if not main_queue.empty():
            current_action = main_queue.get()
        wifi_stopped_queue.put(True)
        stopped = True
        if not move_list.empty():
            move = move_list.get()
            # TODO: run move
    wifi_thread.join()
    print("wifi thread stopped")
