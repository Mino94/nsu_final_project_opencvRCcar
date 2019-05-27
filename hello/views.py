from django.shortcuts import render , render_to_response
import cv2 
from django.http import StreamingHttpResponse
import os
import numpy as np
from django.views.decorators.csrf import csrf_exempt
import json
import base64


def home(request):
    return render(request, 'home.html')

def second(request):
    return render(request, 'second.html')

# cap = cv2.VideoCapture("http://192.168.0.5:8080/?action=stream")
cap = cv2.VideoCapture(0)

def ROI_img(img, vertices):
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, vertices, [255, 255, 255])
        roi = cv2.bitwise_and(img, mask)
        return roi

def hough_line(img, rho, theta, threshold, min_line_len, max_line_gap):
        hough_lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), min_line_len, max_line_gap)

        background_img = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)

        if(np.all(hough_lines) ==True):
                draw_hough_lines(background_img, hough_lines)
 
        return background_img

def draw_hough_lines(img, lines, color=[0, 0, 255], thickness = 2):
        for line in lines:
                for x1, y1, x2, y2 in line:
                        cv2.line(img, (x1, y1), (x2, y2), color, thickness)

def weighted_img(init_img, added_img):
        return cv2.addWeighted(init_img, 1.0, added_img, 1.0, 0.0)

def gen():
    global cap
    print('Starting camera thread')
    while True:
        ret, frame = cap.read()
        if(ret):
            height, width = frame.shape[:2]
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            img = cv2.GaussianBlur(img, (3, 3), 0)
            img = cv2.Canny(img, 70, 210)
            vertices = np.array([[(0, height/2 - 50), (width, height/2 - 50), (width, height/2 + 50), (0, height/2 + 50)]], np.int32)
            img = ROI_img(img, vertices)
            hough_lines = hough_line(img, 1, np.pi/180, 50, 50, 30)
            
            merged_img = weighted_img(frame, hough_lines)

            ret, jpeg = cv2.imencode('.jpg', merged_img) 
            get_frame = jpeg.tobytes() 

        yield (b'--frame\r\n' 
        b'Content-Type: image/jpeg\r\n\r\n' + get_frame + b'\r\n')

def video_feed(request):
        return StreamingHttpResponse(gen(), content_type='multipart/x-mixed-replace; boundary=frame')

fgbg = cv2.createBackgroundSubtractorMOG2(varThreshold=100)

def gen2():
    global cap
    global fgbg
    print('Detect Starting camera thread')
    while True:
        ret, frame = cap.read()
        fgmask = fgbg.apply(frame)

        nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(fgmask)

        for index, centroid in enumerate(centroids):
                if stats[index][0] == 0 and stats[index][1] == 0:
                        continue
                if np.any(np.isnan(centroid)):
                        continue

                x, y, width, height, area = stats[index]
                centerX, centerY = int(centroid[0]), int(centroid[1])
                if area > 100:
                        cv2.circle(frame, (centerX, centerY), 1, (0, 255, 0), 2)
                        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 255))

        ret, jpeg2 = cv2.imencode('.jpg', fgmask) 
        get_frame2 = jpeg2.tobytes() 

        yield (b'--frame\r\n' 
        b'Content-Type: image/jpeg\r\n\r\n' + get_frame2 + b'\r\n')

def second_video_feed(request):
        return StreamingHttpResponse(gen2(), content_type='multipart/x-mixed-replace; boundary=frame')
