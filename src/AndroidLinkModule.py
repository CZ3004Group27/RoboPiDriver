from multiprocessing import Process, Queue


class AndroidLinkModule(Process):
    def __init__(self, stopped_queue,command_queue, move_queue, main_thread_override_queue):
        Process.__init__(self)
        self.stopped = False
        self.stopped_queue = stopped_queue
        self.move_queue = move_queue
        self.command_queue = command_queue
        self.main_thread_override_queue = main_thread_override_queue
        print("hello")

    def run(self):
        print("thread running")
        while not self.stopped:
            if not self.stopped_queue.empty():
                self.stopped = self.stopped_queue.get()
            pass
        print("stopping!")
