import argparse
import base64
import threading
import time
from PIL import Image

import redis
import uvicorn
from face_finder import find_and_write_name_on_image
from fastapi import FastAPI
from fastapi.responses import FileResponse
from person_finder import init_model, process_frame, convert_image_to_numpyarray

app = FastAPI()


@app.get("/")
def read_root():
    """"Main page to test website"""
    return {"Hello": "World"}


@app.get("/rasp_cam")
def show_image() -> FileResponse:
    """Show the latest uploaded image"""
    return FileResponse("uploaded_image.jpg")


def parse_args() -> int:
    """Function to parse arguments from cmdline"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type=int, default=80)
    args = parser.parse_args()
    return args.p


def redis_service(model: any) -> None:
    aws_redis = redis.StrictRedis(host='redis', port=6379, db=0)
    pubsub = aws_redis.pubsub()
    pubsub.subscribe('image_channel')

    while True:
        print('checking redis channel')
        for message in pubsub.listen():
            encoded_image = message['data']
            if encoded_image != 1:
                image_data = base64.b64decode(encoded_image)
                image = Image.open(image_data)
                image_array = convert_image_to_numpyarray(image)
                processed_image, human_detected = process_frame(image_array, model)
                if human_detected:
                    image = Image.fromarray(image_array)
                    image.save('uploaded_image.jpg')
                    aws_redis.publish('alarm', 'Sound the alarm!')
                    find_and_write_name_on_image("uploaded_image.jpg")
        time.sleep(0.1)


if __name__ == '__main__':
    p = parse_args()
    model = init_model()
    web_server_thread = threading.Thread(target=uvicorn.run,
                                         args=(app,),
                                         kwargs={'port': p, 'host': "0.0.0.0"})
    redis_service_thread = threading.Thread(target=redis_service, args=(model,))
    redis_service_thread.start()
    web_server_thread.start()
    web_server_thread.join()
    redis_service_thread.join()
