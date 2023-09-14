from typing import  Any, Tuple
import cv2
import numpy
import torch
from PIL import Image

# declearing constants
RESOLUTION_HEIGHT = 960
RESOLUTION_WIDTH = 1280


def init_model() -> Any:
    """For initializing the model additional settings can be added to this function"""
    try:
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # load functions returns any
        model.classes = [0]
        model.conf = 0.33  # up confidence if detecting other objects as person
        return model
    except Exception as e:
        print(f"Error while initializing the model:{e}")


def process_frame(frame: numpy.ndarray, model) -> Tuple[numpy.ndarray, bool]:
    """
    Processes the frame recieved from cam
    if person found returns proccessed image and True
    if not returns the original frame and False"""
    try:
        clr_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(clr_frame, size=RESOLUTION_WIDTH)
        found_objects = str(results.pandas().xyxy[0].value_counts('name'))
        if "person" in found_objects:
            result_image = results.render()[0]
            result_image = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            return result_image, True
        else:
            return frame, False
    except Exception as e:
        print(f"Error while processing image:{e}")
        return frame, False


def convert_image_to_numpyarray(image: Image) -> numpy.ndarray:
    image_array = numpy.asarray(image)
    return image_array
