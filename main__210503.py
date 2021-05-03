import cv2
import numpy as np
import threading
import time
import vlc
import simpleaudio as sa



# p = vlc.MediaPlayer('sample.mp3')
# soundlength = p.get_length()

def play():
    print("PLAYYYYYYYYYYYYYYYYY")
    wave_obj = sa.WaveObject.from_wave_file('sample.wav')
    play_obj = wave_obj.play()
    play_obj.wait_done()
    # #p.play()
    # if ((soundlength <= p.get_time()) or (p.is_playing == False)) :
    #     print("NOT PLAYING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #     p.set_media('sample.mp3')
    #     p.play()
        
        
    # else:
    #     #p.play()
    #     print("PLAYYYYYYYYYYYYYYYYYYYYY")





def zero():
    print(f"0단계 진입")

def one():
    print(f"1단계 진입")

def two():
    print(f"2단계 진입")


def three():
    print(f"3단계 진입")

def four():
    print(f"4단계 진입")

def five():
    print(f"5단계 진입")

def not_zero():
    print("")

def alert_level(x):
    sound=threading.Thread(name="sound_Thread", target=play, daemon=True)
    sound.start()

    dispatch= [zero,
               not_zero,
               one,
               not_zero,
               two,
               not_zero,
               three,
               not_zero,
               four,
               not_zero,
               five]
    dispatch[x]()

def gstreamer_pipeline(
    capture_width=640,
    capture_height=480,
    display_width=640,
    display_height=480,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        f"width=(int){capture_width}, height=(int){capture_height}, "
        f"format=(string)NV12, framerate=(fraction){framerate}/1 ! "
        f"nvvidconv flip-method={flip_method} ! "
        f"video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)GRAY8 ! "
        f"videoconvert ! "
        f"video/x-raw, format=(string)BGR ! appsink"
    )

model = 'load_file/res10_300x300_ssd_iter_140000.caffemodel'
config = 'load_file/deploy.prototxt'

eye_cascPath = 'load_file/haarcascade_eye_tree_eyeglasses.xml'  #eye detect model
eyeCascade = cv2.CascadeClassifier(eye_cascPath)

isEyes = "None"
alert_level_count = 0

x1 = 0
x2 = 0
y1 = 0
y2 = 0

def check_eye(frame):
    eyes = eyeCascade.detectMultiScale(
    frame,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(30, 30),
    )
    global isEyes
    #"NONE"
    global alert_level_count
    if len(eyes) == 0:
        print("눈 감겨있음")
        isEyes = "CLOSE"
       
        if alert_level_count < 10:
            alert_level_count += 1 
        alert_level(alert_level_count)
    else:
        print("눈 떠져있음")
        isEyes = "OPEN"
        if alert_level_count > 0:
            alert_level_count -= 1
    return eyes

cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print('카메라가 정상적으로 연결이 되어있지 않습니다.')
    exit()

net = cv2.dnn.readNet(model, config)

if net.empty():
    exit()

#global confidence
#confidence = 0.0

_, frame = cap.read()
if frame is None:
    exit()

def startTimer():
    timer = threading.Timer(0.01, startTimer)
    timer.daemon = True
    blob = cv2.dnn.blobFromImage(frame, 1, (300, 300), (104, 177, 123))
    net.setInput(blob)
    detect = net.forward()

    detect = detect[0, 0, :, :]
    (h, w) = frame.shape[:2]

    for i in range(detect.shape[0]):
        confidence = detect[i, 2]

        if confidence < 0.5:
            break
        else:
            global x1
            x1 = int(detect[i, 3] * w)
            global y1
            y1 = int(detect[i, 4] * h)
            global x2
            x2 = int(detect[i, 5] * w)
            global y2
            y2 = int(detect[i, 6] * h)

            #print(f"{x1}, {y1}")
        
            check_eye(frame)
    timer.start()

startTimer()

prevTime = 0

while True:
    
    _, frame = cap.read()
    if frame is None:
        break

    curTime = time.time()
    sec = curTime - prevTime
    prevTime = curTime
    fps = 1/(sec)

    labFPS = "FPS: %0.1f" % fps
    #labFace = f"Face Accuracy: {confidence}"
    labEye = f"isEyesOn: {isEyes}"
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0))
    cv2.putText(frame, labFPS, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
    #cv2.putText(frame, labFace, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
    cv2.putText(frame, labEye, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)

    #print ("Time: ", sec)
    #print ("Estimated fps", fps)
    #start_t = timeit.default_timer()
    # blob = cv2.dnn.blobFromImage(frame, 1, (300, 300), (104, 177, 123))
    # net.setInput(blob)
    # detect = net.forward()

    # detect = detect[0, 0, :, :]
    # (h, w) = frame.shape[:2]

    # for i in range(detect.shape[0]):
    #     confidence = detect[i, 2]
    #     if confidence < 0.5:
    #         break

        # x1 = int(detect[i, 3] * w)
        # y1 = int(detect[i, 4] * h)
        # x2 = int(detect[i, 5] * w)
        # y2 = int(detect[i, 6] * h)
        
        # #사각형그리기
        # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0))
        # # 사각형을 그릴 이미지, 사각형의 좌측상단좌표, 우측하단좌표, 테두리 색, 테두리 두께
        # #라벨과 라벨붙이기
        # label = 'Face: %4.3f' % confidence
        # cv2.putText(frame, label, (x1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
        # 텍스트를 넣을 이미지, 텍스트 내용, 텍스트 시작 좌측하단좌표, 글자체, 글자크기, 글자색, 글자두께, cv2.LINE_AA(좀 더 예쁘게 해주기 위해)
        #test = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #t1 = threading.Thread(target=check_eye, args=(frame,))
        #t1.start()
        #check_eye(frame)
    #terminate_t = timeit.default_timer()
    #FPS = int(1./(terminate_t - start_t ))
    #print(FPS)
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()

cv2.destroyAllWindows()
