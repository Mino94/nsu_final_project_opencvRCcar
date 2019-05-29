# nsu_final_project_opencvRCcar
OpenCV 사용 영상처리 RC카

Hw : 아두이노, 라즈베리파이, 
Sw : Django, OpenCV, Android

1. Android와 아두이노 Bluetooth 통신
2. Raspberry Pi Camera => Mjpeg-streamer Server에 올리기
3. Server에 올리 Camera영상을 가져와 Django에서 영상처리
 - Canny 알고리즘을 이용하여 Edge Detetctor 

 [Canny 에지 검출 알고리즘]
단계 1.  가우시안 필터링을 하여 노이즈를 없앴다. #가우시안 필터를 사용하여 노이즈 제거 3*3
        이미지에 상세한것들이 단순하게 된다. 이미지상에 노이즈들이 제거된다.
        
단계 2.  Sobel 연산자를 사용하여 기울기(gradient) 값이 높은 부분을 찾는다.

단계 3.  최대값이 아닌 픽셀의 값을 0으로 만들었다.

단계 4.  히스테리시스 임계값(hysteresis thresholding) 방식을 사용 에지인지 아닌지를 판별한다.

- OpenCV에서 제공하는 Background Subtraction 알고리즘 중 하나인 BackgroundSubtractorMOG2를 사용
  connectedComponentsWithStats 함수를 사용하여 라벨링
