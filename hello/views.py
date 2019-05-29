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

# cap = cv2.VideoCapture("http://192.168.0.4:8080/?action=stream")
cap = cv2.VideoCapture("http://192.168.0.62:8080/?action=stream")

#ROI 는 관심구역을 의미
def ROI_img(img, vertices):
        mask = np.zeros_like(img) # 0으로 이루어진 img와 같은 크기의 행렬을 만든다.
        cv2.fillPoly(mask, vertices, [255, 255, 255]) #mask에 vertices에 지정된 좌표 4개의 안쪽을 흰색으로 채워준다.
        roi = cv2.bitwise_and(img, mask) #둘다 0이 아닌경우에 return
        return roi

def hough_line(img, rho, theta, threshold, min_line_len, max_line_gap):
        # 화면의 직선을 검출한다. 시작과 끝점 2개를 검출
        # threshold 에 따라 정밀도와 직선검출을 조절한다.
        hough_lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), min_line_len, max_line_gap)
        
        #직선을 그릴 검은색 이미지를 생성한다.
        background_img = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)

        # None 값이면 그리지않겠다.
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
            img = cv2.GaussianBlur(img, (3, 3), 0) #가우시안 필터를 사용하여 노이즈 제거 3*3
            img = cv2.Canny(img, 70, 210) #low = 70, high = 210
            vertices = np.array([[(0, height/2 - 50), (width, height/2 - 50), (width, height/2 + 50), (0, height/2 + 50)]], np.int32)
            img = ROI_img(img, vertices) # 수평선 
            hough_lines = hough_line(img, 1, np.pi/180, 50, 50, 30)
            
            merged_img = weighted_img(frame, hough_lines)

            ret, jpeg = cv2.imencode('.jpg', merged_img) 
            get_frame = jpeg.tobytes() 

        yield (b'--frame\r\n' 
        b'Content-Type: image/jpeg\r\n\r\n' + get_frame + b'\r\n')

def video_feed(request):
        return StreamingHttpResponse(gen(), content_type='multipart/x-mixed-replace; boundary=frame')
# 배경제거 라이브러리 함수
fgbg = cv2.createBackgroundSubtractorMOG2(varThreshold=100)

def gen2():
    global cap
    global fgbg
    print('Detect Starting camera thread')
    while True:
        ret, frame = cap.read()
        fgmask = fgbg.apply(frame)
        # connectedComponentsWithStats를 사용하여 레이블링
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

        ret, jpeg2 = cv2.imencode('.jpg', frame) 
        get_frame2 = jpeg2.tobytes() 

        yield (b'--frame\r\n' 
        b'Content-Type: image/jpeg\r\n\r\n' + get_frame2 + b'\r\n')

def second_video_feed(request):
        return StreamingHttpResponse(gen2(), content_type='multipart/x-mixed-replace; boundary=frame')
