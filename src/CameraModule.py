import os
import time
import cv2

# Conditional import of picamera (only works on linux)
# Windows
if os.name == 'nt':

    class CameraModule:
        def __init__(self):
            self.initialised = False

        def take_picture(self):
            pass

# Posix (Linux, OS X)
else:

    class CameraModule:
        def __init__(self):
            self.camera_index = 0
            self.initialised = False
            self.camera = None
            self.rawCapture = None
            # initialize the camera and grab a reference to the raw camera capture
            self.camera = cv2.VideoCapture(self.camera_index)
            # allow the camera to warmup
            time.sleep(0.1)
            self.initialised = True

        def take_picture(self):
            self.camera.open(self.camera_index)
            # grab an image from the camera
            ret, frame = self.camera.read()
            self.camera.release()
            if ret:
                return frame
            else:
                return None
