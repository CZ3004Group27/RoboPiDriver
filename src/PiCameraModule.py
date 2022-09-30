import os
import time
from picamera2 import Picamera2

class CameraModule:
        def __init__(self):
            self.camera_index = 0
            self.initialised = False
            self.camera = Picamera2()
            self.camera.resolution = (640,480)
            self.camera.framerate = 30

            # Make the image taken brighter
            self.camera.set_controls({"Brightness": 0.5})
            self.image = np.empty((640 * 480 * 3,), dtype=np.uint8)

            # allow the camera to warmup
            time.sleep(0.1)
            self.initialised = True

        def take_picture(self):
            # grab an image from the camera
            self.camera.capture(image, 'bgr')
            image = image.reshape((640, 480, 3))
            return image
