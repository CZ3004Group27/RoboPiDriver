import os
import time
import cv2


class DummyCameraModule:
    def __init__(self):
        self.initialised = False

        # allow the camera to warmup
        time.sleep(0.1)
        self.initialised = True

    def take_picture(self):
        # grab an image from the camera
        frame = cv2.imread("dummycatimage.jpg")
        return frame
