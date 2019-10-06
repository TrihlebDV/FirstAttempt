#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import imutils
from pyzbar import pyzbar

class Function(): #вспомогательный класс содержащий функции
    def __init__(self, shape):
        self.per = None
        self.kernel = None
        self.sensivity = 70
        self.h  = None
        self.frame_shape = shape
        self.white = cv2.imread("white.jpg")
        self.black = cv2.bitwise_not(self.white[0:self.frame_shape[0], 0:self.frame_shape[1]])
        self.makeKernel(30)
        self.debug = False
        self.imgInit()

    def imgInit(self):
        self.white = self.white[0:self.frame_shape[0], 0:self.frame_shape[1]]
        self.black = cv2.bitwise_not(self.white)

    def makeKernel(self, par):
        self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (par, par))

    def setSensivity(self, par):
        self.sensivity = par
        #print(self.sensivity)

    def setDebug(self):
        self.debug = not self.debug

    def getPyzbarCode(self, img):
        img = imutils.resize(img, width=400)
        # find the barcodes in the frame and decode each of the barcodes
        barcodes = pyzbar.decode(img)
        # loop over the detected barcodes
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # the barcode data is a bytes object so if we want to draw it
            # on our output image we need to convert it to a string first
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(img, text, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        return img
        
    def detectLine(self, frame):
        direction = 0
        check = 0
        lineFound = False
        #frame1 = cv2.warpPerspective(frame, self.h, (520, 320), cv2.INTER_LINEAR) # переводим изображение в вертикальный вид
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # переход в  оттенки серого
        _ , fthresh = cv2.threshold(gray, self.sensivity, 255, cv2.THRESH_BINARY_INV) # градация черного-белого по уровню self.sensitivity
        direction = 0.0 #курс нашей посудины
        lineFound = False
        for i in range(5): #для каждой 5-ой по вертикале части изображения определяем центр наибольшего черного пятна 
            thresh = fthresh[i*round(self.frame_shape[0]/5):(i+1)*round(self.frame_shape[0]/5), 0:self.frame_shape[1]]
            _, contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cx = thresh.shape[0] #на случай если не удастся вычислить cx
            cy = thresh.shape[1]
            if contours:   # если есть хоть один контур
                lineFound = True
                mainContour = max(contours, key = cv2.contourArea)    # берем максимальный
                M = cv2.moments(mainContour)  # берем его
                if M['m00'] != 0:   # если нет деления на ноль
                    cx = int(M['m10']/M['m00'])     # смотрим координаты центра наибольшего черного пятна
                    cy = int(M['m01']/M['m00'])     # они получаются в пикселях кадра
                    if (cx - round(self.frame_shape[1]/3)) < 0:
                        check -= 1
                    elif (cx - 2*round(self.frame_shape[1]/3) > 0):
                          check += 1
                    if self.debug:
                        cv2.line(frame, (cx, cy-30+i*round(self.frame_shape[0]/5)), (cx, cy+30+i*round(self.frame_shape[0]/5)), (255, 0, 0), 1)    # рисуем перекрестье центре контура
                        cv2.line(frame, (cx-30, cy+i*round(self.frame_shape[0]/5)), (cx+30, cy+i*round(self.frame_shape[0]/5)), (255, 0, 0), 1)
                if self.debug:
                    cv2.circle(frame, (cx, cy+i*round(self.frame_shape[0]/5)), 3, (0, 0, 255), -1) #отрисовываем центральную точку контура 
                    #cv2.drawContours(frame, mainContour, -1, (0, 255, 0), 2, cv2.FILLED) #отображаем контуры на изображении
                direction =direction + (cx / (thresh.shape[1]/2) - 1)*(5 - i)  # преобразуем координаты от 0 до ширина кадра -> от -1 до 1
        return lineFound, direction/5, check, frame

    def getMaskedImage(self,  image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _ , fthresh = cv2.threshold(gray, 104, 255, cv2.THRESH_BINARY) # градация черного-белого по уровню self.sensitivity
        # создайте и примените закрытие
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 30))
        closed = cv2.morphologyEx(fthresh, cv2.MORPH_CLOSE, kernel)
        #поиск контуров
        h, w = closed.shape[:2]
        cv2.rectangle(closed,(0, round(h*4/5)),(w, h),(255, 255, 255), -1)
        cnts = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[1]
        if cnts:
            c = max(cnts, key = cv2.contourArea)
            hull = cv2.convexHull(c)
            mask = np.zeros(self.frame_shape, np.uint8)
            cv2.fillPoly(mask, pts = [hull], color=(255, 255, 255))
            mask = cv2.bitwise_not(mask)
            image1 = cv2.bitwise_or(self.white, self.black, mask = mask)
            image = cv2.add(image, image1)
        else:
            mask = np.zeros((h, w),np.uint8)
            image = cv2.bitwise_and(image, image, mask = mask)
        return image
        #return closed
        














        
