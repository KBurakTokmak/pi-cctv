"""Script to get images from RaspberryPi cam periodically"""
import argparse
import base64
import threading
from time import sleep
from typing import Tuple, no_type_check

import cv2
import numpy
import pygame
import redis
import torch
from RaspCam import RaspCam

# declearing constants
RESOLUTION_HEIGHT = 480
RESOLUTION_WIDTH = 640


@no_type_check
def send_image_to_redis_channel(image: numpy.ndarray, redis: redis.StrictRedis) -> None:
    '''Send image bytes(base64) to image_channel channel on specified redis connection'''
    try:
        ret, buffer = cv2.imencode('.jpg', image)
        buffer = buffer.tobytes()
        buffer = base64.b64encode(buffer)
        pi_redis.publish('image_channel', buffer)
    except Exception as e:
        print(f"Error while sending image through redis channel:{e}")


def parse_args() -> (str):
    """Function to parse arguments from cmdline"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip")
    args = parser.parse_args()
    return args.ip


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


def init_model():
    """For initializing the model additional settings can be added to this function"""
    try:
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # load functions returns any
        model.classes = [0]
        model.conf = 0.25  # up confidence if detecting other objects as person
        return model
    except Exception as e:
        print(f"Error while initializing the model:{e}")


def play_alarm_on_redis_signal(pi_redis: redis.StrictRedis) -> None:
    pygame.mixer.pre_init(buffer=2048)
    pygame.mixer.init()
    alarm_sound = pygame.mixer.Sound('pi_cam/alarm.wav')
    pubsub = pi_redis.pubsub()
    pubsub.subscribe('alarm')
    try:
        while True:
            for message in pubsub.listen():
                print(message['data'])
                if message['data'] == "Sound the alarm!":
                    alarm_sound.play()
            sleep(0.25)
    except Exception as e:
        print(f'Error while reciving messages in redis:{e}')


def periodic_image_sender(pi_redis: redis.StrictRedis) -> None:
    try:
        cam = RaspCam(RESOLUTION_HEIGHT, RESOLUTION_WIDTH)
        model = init_model()
        while True:
            frame, is_successful = cam.capture_frame()
            if not is_successful:
                break
            processed_image, human_detected = process_frame(frame, model)
            if human_detected:
                print('sending image to redis channel')
                send_image_to_redis_channel(processed_image, pi_redis)
            cam.wait_next_frame(0.5)
            cam.camera = cam.initialize_cam()  # re init cam for new capture
        cam.end_cv_capture()
    except Exception as e:
        print(f"Error in image sender loop:{e}")


if __name__ == "__main__":
    aws_ip = parse_args()
    pi_redis = redis.StrictRedis(host=aws_ip, port=6688, db=0, charset="utf-8", decode_responses=True)
    imagesender_thread = threading.Thread(target=periodic_image_sender, args=(pi_redis,))
    soundplayer_thread = threading.Thread(target=play_alarm_on_redis_signal, args=(pi_redis,))
    imagesender_thread.start()
    soundplayer_thread.start()
    imagesender_thread.join()
    soundplayer_thread.join()
