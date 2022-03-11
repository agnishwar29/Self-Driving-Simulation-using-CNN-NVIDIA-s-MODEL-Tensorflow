print("setting up")
import base64
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] ='3'
import cv2
from PIL import Image
import numpy as np
import socketio
import eventlet
from flask import Flask
from keras.models import load_model
from io import BytesIO

sio = socketio.Server()
app = Flask(__name__)
maxSpeed = 30


def preProcess(img):
    img = img[60:135,:,:]
    img =cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img,(3,3),0)
    img = cv2.resize(img,(200,66))
    img = img/255
    return img

@sio.on('telemetry')
def telemetry(sid,data):
    speed = float(data['speed'])
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = preProcess(image)
    image = np.array([image])
    steering = float(model.predict(image))
    throttle =1.0 - speed /maxSpeed
    print('{} {} {}'.format(steering,throttle,speed))
    sendControl(steering, throttle)


@sio.on('connect')
def connect(sid, environ):
    print("connected")
    sendControl(0,0)

def sendControl(steering, throttle):
    sio.emit('steer', data={
        'steering_angle': steering.__str__(),
        'throttle': throttle.__str__()
    })

if __name__ == '__main__':
    model = load_model('D:\pythonProject\Self-Driving-Car\model.h5')
    app = socketio.Middleware(sio,app)
    eventlet.wsgi.server(eventlet.listen(('',4567)),app)