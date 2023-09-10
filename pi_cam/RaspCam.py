import time
from pathlib import Path
from typing import Tuple

import cv2


class RaspCam:

    def __init__(self, width: int, height: int, test=False) -> None:
        self.width = width
        self.height = height
        if not test:
            self.camera = self.initialize_cam()

    def initialize_cam(self) -> cv2.VideoCapture:
        """Initialize the cam with desired resolution"""
        try:
            # Initialize the camera
            camera = cv2.VideoCapture(0)  # Use 0 for the default camera
            # Set the resolution of the camera (optional)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            return camera
        except Exception as e:
            print(f"Error while initializing camera: {e}")
            return camera

    def capture_frame(self) -> Tuple[cv2.UMat, bool]:
        """Capture Frame and return it with a status flag as tuple"""
        try:
            ret, frame = self.camera.read()
            if not ret:
                print("Error capturing frame")
                return frame, False
            return frame, True
        except Exception as e:
            print(f"Error during frame capture: {e}")
            return frame, False

    def save_frame(self, frame: cv2.UMat) -> None:
        """Save captured frame to desired location"""
        try:
            # Define the file name with a timestamp
            timestamp = time.strftime("%Y%m%d%H%M%S")
            filename = f"frame_{timestamp}.jpg"
            save_directory = Path.home() / 'cam_images' / filename
            # Save the frame
            cv2.imwrite(str(save_directory), frame)
            print(f"Frame saved as {filename}")
        except Exception as e:
            print(f"Error while saving frame:{e}")

    def wait_next_frame(self, seconds: int) -> None:
        """Desired waittime between captures and cam release/reset"""
        try:
            self.camera.release()
            time.sleep(seconds)
        except Exception as e:
            print(f"Error while cam release and waiting:{e}")

    def end_cv_capture(self):
        """Destroy windows by cv2"""
        try:
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Error while closing cv2 windows:{e}")
