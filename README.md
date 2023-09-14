# Pi-cctv-XI
## Table of Contents
- [pi-cctv-XI](#pi-cctv-xi)
  - [Table of Contents](#table-of-contents)
  - [Pre Setup](#pre-setup)
    - [Raspberry](#raspberry)
    - [AWS Server](#aws-server)
  - [Setup](#setup)
    

## Pre Setup

  Readying the raspberry and AWS server(or any server) for to use in project.

### Raspberry

* Flash the sd card preloaded with RaspberryPi OS 64 bit lite. Setup the SSH, WLAN and login details in the preload.
* For preload [this guide](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up/2) can be used.
* Install the camera to Raspberry and enable it from "raspi-config" in terminal. [Guide for Raspberry PI Cam](https://raspberrytips.com/install-camera-raspberry-pi/)

## Setup
  
  Connect to your AWS instance and raspberry pi with your preferred SSH method.
  
  First you need to clone the repo in your home(~) folder. Do this for both AWS instance and Raspberry.

 `sudo apt-get install git`
  
  `git clone https://github.com/KBurakTokmak/pi-cctv.git`

  First find what your public IP adresss of the AWS instance(or your server) and note it down. For setup start with AWS server. 
* Use [this repo](https://github.com/arsfutura/face-recognition) to generate your own model and put in in model/ folder. Should be like `pi-cctv/model/face_recognizer.pk`
* Install docker on both devices. `curl -sSL https://get.docker.com | sh` is the command I`ve used.
* On AWS cd into cloned repo and use `sudo docker compose up` to build the image and run the required containers.
* On Raspberry pi cd into cloned pi-cctv. Run the command while changing `${YOUR_AWS_IP}` to your aws ip address `sudo docker build -f Dockerfile.rasp --build-arg AWS_IP=${YOUR_AWS_IP} -t imagesender .`
* Than run the built container as `sudo docker container run --privileged -it -d imagesender` . It will take some time(5mins) for container to build yolov5 model.

Now your raspberry pi will send images to your aws server automatically and aws will do the face recognition. Whenever aws server recieves an image with person detected it will send signal to pi to sound alarm.

Image can be viewed at http://<aws_public_ip>:port/rasp_cam
