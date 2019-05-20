from django.shortcuts import render , render_to_response
import cv2 #0이면 노트북 내장 웹캠 숫자를 올리면 추가된 웹캠을 이용할 수 있다. cap = cv2.VideoCapture(0) # 3은 가로 4는 세로 길이 cap.set(3, 720) cap.set(4, 1080) while True: ret, frame = cap.read() cv2.imshow('test', frame) k = cv2.waitKey(1) if k == 27: break cap.release() cv2.destroyAllWindows()
from django.http import StreamingHttpResponse
import os
import numpy as np
from django.views.decorators.csrf import csrf_exempt
import json
import base64
def home(request):
    return render(request, 'home.html')

cap = cv2.VideoCapture(0)
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def gen():
    global cap
    global faceCascade
    print('Starting camera thread')
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                # flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        ret, jpeg = cv2.imencode('.jpg', faces) 
        get_frame = jpeg.tobytes() # jpg 를  Byte 로 변환
        yield (b'--frame\r\n' 
        b'Content-Type: image/jpeg\r\n\r\n' + get_frame + b'\r\n')
                
def video_feed(request):
        return StreamingHttpResponse(gen(), content_type='multipart/x-mixed-replace; boundary=frame')
