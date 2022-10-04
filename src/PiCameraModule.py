import os
import time
from picamera2 import Picamera2

class CameraModule:
        def __init__(self):
            self.camera_index = 0
            self.initialised = False
            self.camera = Picamera2()

            config = Picamera2.still_configuration(main={"size": (640, 480), "format": "BGR888"})

            self.camera.configure(config)
            self.camera.video_configuration.controls.framerate = 30

            # Make the image taken brighter
            self.camera.set_controls({"Brightness": 0.5})
            self.camera.start()

            # allow the camera to warmup
            time.sleep(1)
            self.initialised = True

        def take_picture(self):
            # grab an image from the camera
            image = self.camera.capture_array("main")
            return image
