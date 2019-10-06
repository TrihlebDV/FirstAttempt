#!/usr/bin/env python3
# -*- coding: utf-8 -*-

 
''' 
#создаем массив cvFrame в формате opencv
cvFrame = np.ndarray((heightFrame, widthFrame, 3), buffer = data, dtype = np.uint8)
        
self._onFrameCallback(cvFrame) #вызываем обработчик в качестве параметра передаем cv2 кадр
'''

import time
import receiver

IP_ROBOT = '10.42.0.236'
RTP_PORT = 5000

def onFrameCallback(frame, w, h):
    print(w)

recv = receiver.StreamReceiver(receiver.VIDEO_MJPEG, onFrameCallback)
#recv = receiver.StreamReceiver(receiver.VIDEO_MJPEG)
recv.setPort(RTP_PORT)
recv.setHost(IP_ROBOT)
recv.play_pipeline()

#recvCV = receiver.StreamReceiver(receiver.VIDEO_MJPEG, (IP_ROBOT, RTP_PORT+50))
#recvCV.play_pipeline()

#главный цикл программы    
try:
    while True:
        time.sleep(0.1)
except (KeyboardInterrupt, SystemExit):
    print('Ctrl+C pressed')

recv.stop_pipeline()
recv.null_pipeline()
