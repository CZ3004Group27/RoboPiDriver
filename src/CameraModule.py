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
    import picamera


    class CameraModule:
        def __init__(self):
            self.initialised = False
            self.camera = None
            self.rawCapture = None
            # initialize the camera and grab a reference to the raw camera capture
            if os.name == 'nt':
                self.camera = PiCamera()
                self.rawCapture = PiRGBArray(camera)
                # allow the camera to warmup
                time.sleep(0.1)
                self.initialised = True
            else:
                pass

        def take_picture(self):
            # grab an image from the camera
            self.camera.capture(self.rawCapture, format="bgr")
            image = self.rawCapture.array
