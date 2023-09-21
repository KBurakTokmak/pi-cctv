import argparse
import base64
import io
import threading
import time
from typing import Any

import redis
import uvicorn
from face_finder import find_and_write_name_on_image, load_model
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from person_finder import (convert_image_to_numpyarray, init_model,
                           process_frame)
from PIL import Image

app = FastAPI()


app.mount("/static", StaticFiles(directory="FastAPI_backend/static"), name="static")


@app.get("/")
def read_root():
    """"Main page to test website"""
    return {"Hello": "World"}


@app.get("/rasp_cam", response_class=HTMLResponse)
def show_image() -> str:
    """Show the latest detected image with auto-refresh"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Raspberry Pi Camera</title>
    </head>
    <body>
        <h1>Raspberry Pi Camera</h1>
        <img id="raspCamImage" src="/static/detect_image.jpg" alt="Raspberry Pi Camera">
        <script>
            function refreshImage() {
                // Get a reference to the image element
                var img = document.getElementById("raspCamImage");

                // Generate a random parameter to force browser refresh (cache busting)
                var randomParam = Math.random();

                // Update the image source with the random parameter
                img.src = "/static/detect_image.jpg?" + randomParam;
            }

            // Refresh the image every 1 seconds (1000 milliseconds)
            setInterval(refreshImage, 1000);
        </script>
    </body>
    </html>
    """


@app.get("/latest_frame", response_class=HTMLResponse)
def show_latest_image() -> str:
    """Show the latest detected image with auto-refresh"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Raspberry Pi Camera</title>
    </head>
    <body>
        <h1>Raspberry Pi Camera</h1>
        <img id="raspCamImage" src="/static/uploaded_image.jpg" alt="Raspberry Pi Camera">
        <script>
            function refreshImage() {
                // Get a reference to the image element
                var img = document.getElementById("raspCamImage");

                // Generate a random parameter to force browser refresh (cache busting)
                var randomParam = Math.random();

                // Update the image source with the random parameter
                img.src = "/static/uploaded_image.jpg?" + randomParam;
            }

            // Refresh the image every 1 seconds (1000 milliseconds)
            setInterval(refreshImage, 1000);
        </script>
    </body>
    </html>
    """


def parse_args() -> int:
    """Function to parse arguments from cmdline"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type=int, default=80)
    args = parser.parse_args()
    return args.p


def redis_service(model: Any) -> None:
    aws_redis = redis.StrictRedis(host='redis', port=6379, db=0)
    pubsub = aws_redis.pubsub()
    pubsub.subscribe('image_channel')
    face_model = load_model()
    while True:
        print('checking redis channel')
        for message in pubsub.listen():
            encoded_image = message['data']
            if encoded_image != 1:
                image_data = base64.b64decode(encoded_image)
                with open('FastAPI_backend/static/uploaded_image.jpg', 'wb') as file:
                    file.write(image_data)
                image = Image.open(io.BytesIO(image_data))
                image_array = convert_image_to_numpyarray(image)
                processed_image, human_detected = process_frame(image_array, model)
                if human_detected:
                    print('person detected')
                    image = Image.fromarray(processed_image)
                    image.save('FastAPI_backend/static/detect_image.jpg')
                    aws_redis.publish('alarm', 'Sound the alarm!')
                    find_and_write_name_on_image("FastAPI_backend/static/detect_image.jpg", face_model)
                else:
                    print('no person detected')
        time.sleep(0.05)


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
