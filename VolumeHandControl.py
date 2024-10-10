import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#################
wCam, hCam = 640, 480
#################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
curr_vol = volume.GetMasterVolumeLevel()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 0
volPer = 0

while True:
    success, img = cap.read()

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:

        x1, y1 = lmList[4][1], lmList[4][2]  # for thumb
        x2, y2 = lmList[8][1], lmList[8][2]  # for index

        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)  # line
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)  # middle point

        length = math.hypot(x2 - x1, y2 - y1)
        #print(length)

        # Hand range 20 - 120
        # Volume range -96 - 0
        vol = np.interp(length, [20, 110], [minVol, maxVol])
        volBar = np.interp(length, [20, 110], [300, 150])
        volPer = np.interp(length, [20, 110], [0, 100])
        #print(vol)

        volume.SetMasterVolumeLevel(vol, None)

        if length < 30:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
        if length > 100:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

        cv2.rectangle(img, (50, 150), (85, 300), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 300), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)}%', (40, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f"FPS: {fps:.2f}", (20, 30), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)

    cv2.imshow('Image', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

volume.SetMasterVolumeLevel(curr_vol, None)
cap.release()
cv2.destroyAllWindows()