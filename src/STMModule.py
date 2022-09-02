from multiprocessing import Process, Queue
from Action import *
import os

if os.name() == 'nt':

    class STMModule:
        def __init__(self):
            pass

        def process_move(self, move: Action):
            pass
else:
    class STMModule:
        def __init__(self):
            pass

        def process_move(self, move: Action):
            pass
