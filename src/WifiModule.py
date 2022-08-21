from multiprocessing import Process, Queue
import os

class WifiModule(Process):
    def __init__(self, stopped_queue, main_queue):
        Process.__init__(self)
        self.stopped = False
        self.stopped_queue = stopped_queue
        print("hello")

    def run(self):
        print("thread running")
        os.system(f'webserver/manage.py runserver')
        while not self.stopped:
            if not self.stopped_queue.empty():
                self.stopped = self.stopped_queue.get()
            pass
        print("stopping!")

