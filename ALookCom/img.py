import math
import random

import cv2

import utils
from commandPub import CommandPub

class Img:
    def __init__(self, com):
        self.cmd = CommandPub(com)
        self.com = com

    ## prepare command for random img saving
    def formatCmdRandom(self, width, height, id = -1):
        ## compress img 4 bit per pixel
        encodedImg = []
        for i in range(height):
            byte = 0
            shift = 0
            for _ in range(width):
                pxl = random.randint(0, 15)

                ## compress 4 bit per pixel
                byte += pxl << shift
                shift += 4
                if shift == 8:
                    encodedImg.append(byte)
                    byte = 0
                    shift = 0
            if shift != 0:
                encodedImg.append(byte)

        ## start save image command
        data = []
        if id != -1:
            data += [id]
        data += utils.intToList(len(encodedImg)) ## compressed size in byte
        data += utils.uShortToList(width)
        cmds = [self.com.formatFrame(0x41, data)]

        ## pack pixels in commands
        nbDataMax = self.com.getDataSizeMax()
        i = 0
        while i < len(encodedImg):
            if nbDataMax > (len(encodedImg) - i):
                nbDataMax = (len(encodedImg) - i)

            cmds += [self.com.formatFrame(0x41, encodedImg[i:(nbDataMax + i)])]
            i += nbDataMax

        return cmds

    ## prepare command for image saving, 1 bit per pixel
    def formatCmdRandom1Bpp(self, width, height, id = -1):
        ## compress img 1 bit per pixel
        encodedImg = []
        for _ in range(height):
            byte = 0
            shift = 0
            encodedLine = []
            for _ in range(width):
                pxl = random.randint(0, 1)

                ## compress 1 bit per pixel
                byte += pxl << shift
                shift += 1
                if shift == 8:
                    encodedLine.append(byte)
                    byte = 0
                    shift = 0
            if shift != 0:
                encodedLine.append(byte)
            encodedImg.append(encodedLine)

        ## start save image command
        data = []
        if id != -1:
            data += [id]
        data += utils.intToList(len(encodedImg) * len(encodedImg[0])) ## compressed size in byte
        data += utils.uShortToList(width)
        cmds = [self.com.formatFrame(0x45, data)]

        ## pack lines in commands
        ## a command must have only full line and not overflow command buffer
        cmdDataMax = self.com.getDataSizeMax()
        lineSize = len(encodedImg[0])
        nbLineMax = cmdDataMax // lineSize
        nbLine = len(encodedImg)
        lineIdx = 0
        while lineIdx < nbLine:
            if nbLineMax > (nbLine - lineIdx):
                nbLineMax = (nbLine - lineIdx)

            data = []
            for _ in range(nbLineMax):
                data += encodedImg[lineIdx]
                lineIdx += 1
            cmds += [self.com.formatFrame(0x45, data)]

        return cmds
    
    ## prepare commands for image streaming
    def formatStreamCmdRandom(self, width, height, x, y, id = -1):
        ## compress img 1 bit per pixel
        encodedImg = []
        for _ in range(height):
            byte = 0
            shift = 0
            encodedLine = []
            for _ in range(width):
                pxl = random.randint(0, 1)

                ## compress 1 bit per pixel
                byte += pxl << shift
                shift += 1
                if shift == 8:
                    encodedLine.append(byte)
                    byte = 0
                    shift = 0
            if shift != 0:
                encodedLine.append(byte)
            encodedImg.append(encodedLine)
        
        ## start stream command
        data = []
        if id != -1:
            data += [id]
        data += utils.intToList(len(encodedImg) * len(encodedImg[0])) ## compressed size in byte
        data += utils.uShortToList(width)
        data += utils.sShortToList(x)
        data += utils.sShortToList(y)
        cmds = [self.com.formatFrame(0x44, data)]

        ## pack lines in commands
        ## a command must have only full line and not overflow command buffer
        cmdDataMax = self.com.getDataSizeMax()
        lineSize = len(encodedImg[0])
        nbLineMax = cmdDataMax // lineSize
        nbLine = len(encodedImg)
        lineIdx = 0
        while lineIdx < nbLine:
            if nbLineMax > (nbLine - lineIdx):
                nbLineMax = (nbLine - lineIdx)

            data = []
            for _ in range(nbLineMax):
                data += encodedImg[lineIdx]
                lineIdx += 1
            cmds += [self.com.formatFrame(0x44, data)]

        return cmds

    ## prepare command for image saving
    def formatCmd(self, filePath, id = -1):
        img = cv2.imread(filePath)
        img2 = cv2.rotate(img, cv2.ROTATE_180)
        
        gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        height = img.shape[0]
        width = img.shape[1]

        ## compress img 4 bit per pixel
        encodedImg = []
        for i in range(height):
            byte = 0
            shift = 0
            for j in range(width):
                ## convert gray8bit to gray4bit
                pxl = round(gray[i,j] / 17)

                ## compress 4 bit per pixel
                byte += pxl << shift
                shift += 4
                if shift == 8:
                    encodedImg.append(byte)
                    byte = 0
                    shift = 0
            if shift != 0:
                encodedImg.append(byte)

        ## start save image command
        data = []
        if id != -1:
            data += [id]
        data += utils.intToList(len(encodedImg)) ## compressed size in byte
        data += utils.uShortToList(width)
        cmds = [self.com.formatFrame(0x41, data)]

        ## pack pixels in commands
        nbDataMax = self.com.getDataSizeMax()
        i = 0
        while i < len(encodedImg):
            if nbDataMax > (len(encodedImg) - i):
                nbDataMax = (len(encodedImg) - i)

            cmds += [self.com.formatFrame(0x41, encodedImg[i:(nbDataMax + i)])]
            i += nbDataMax

        return cmds

    ## prepare command for image saving, 1 bit per pixel
    def formatCmd1Bpp(self, filePath, id = -1):
        img = cv2.imread(filePath)
        img2 = cv2.rotate(img, cv2.ROTATE_180)
        
        gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        height = img.shape[0]
        width = img.shape[1]

        ## compress img 1 bit per pixel
        encodedImg = []
        for i in range(height):
            byte = 0
            shift = 0
            encodedLine = []
            for j in range(width):
                ## convert gray8bit in gray1bit
                if (gray[i,j] > 0):
                    pxl = 1
                else:
                    pxl = 0

                ## compress 1 bit per pixel
                byte += pxl << shift
                shift += 1
                if shift == 8:
                    encodedLine.append(byte)
                    byte = 0
                    shift = 0
            if shift != 0:
                encodedLine.append(byte)
            encodedImg.append(encodedLine)

        ## start save image command
        data = []
        if id != -1:
            data += [id]
        data += utils.intToList(len(encodedImg) * len(encodedImg[0])) ## compressed size in byte
        data += utils.uShortToList(width)
        cmds = [self.com.formatFrame(0x45, data)]

        ## pack lines in commands
        ## a command must have only full line and not overflow command buffer
        cmdDataMax = self.com.getDataSizeMax()
        lineSize = len(encodedImg[0])
        nbLineMax = cmdDataMax // lineSize
        nbLine = len(encodedImg)
        lineIdx = 0
        while lineIdx < nbLine:
            if nbLineMax > (nbLine - lineIdx):
                nbLineMax = (nbLine - lineIdx)

            data = []
            for i in range(nbLineMax):
                data += encodedImg[lineIdx]
                lineIdx += 1
            cmds += [self.com.formatFrame(0x45, data)]

        return cmds

    ## prepare commands for image streaming
    def formatStreamCmd(self, filePath, x, y):
        img = cv2.imread(filePath)
        img2 = cv2.rotate(img, cv2.ROTATE_180)
        
        gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        height = img.shape[0]
        width = img.shape[1]

        ## compress img 1 bit per pixel
        encodedImg = []
        for i in range(height):
            byte = 0
            shift = 0
            encodedLine = []
            for j in range(width):
                ## convert gray8bit in gray1bit
                if (gray[i,j] > 0):
                    pxl = 1
                else:
                    pxl = 0

                ## compress 1 bit per pixel
                byte += pxl << shift
                shift += 1
                if shift == 8:
                    encodedLine.append(byte)
                    byte = 0
                    shift = 0
            if shift != 0:
                encodedLine.append(byte)
            encodedImg.append(encodedLine)
        
        ## start stream command
        data = utils.intToList(len(encodedImg) * len(encodedImg[0])) ## compressed size in byte
        data += utils.uShortToList(width)
        data += utils.sShortToList(x)
        data += utils.sShortToList(y)
        cmds = [self.com.formatFrame(0x44, data)]

        ## pack lines in commands
        ## a command must have only full line and not overflow command buffer
        cmdDataMax = self.com.getDataSizeMax()
        lineSize = len(encodedImg[0])
        nbLineMax = cmdDataMax // lineSize
        nbLine = len(encodedImg)
        lineIdx = 0
        while lineIdx < nbLine:
            if nbLineMax > (nbLine - lineIdx):
                nbLineMax = (nbLine - lineIdx)

            data = []
            for i in range(nbLineMax):
                data += encodedImg[lineIdx]
                lineIdx += 1
            cmds += [self.com.formatFrame(0x44, data)]

        return cmds

    ##
    def appendImageRandom(self, width, height):       
        ## convert image
        cmds = self.formatCmdRandom(width, height)

        ## send commands
        for c in cmds:
            self.com.sendRawData(c)
            if not self.com.receiveAck():
                return False
        
        return True

    ##
    def appendImage(self, filename = "img/smiley.png"):
        ## convert image
        cmds = self.formatCmd(filename)

        ## send commands
        for c in cmds:
            self.com.sendRawData(c)
            if not self.com.receiveAck():
                return False
        
        return True

    ##
    def saveImageRandom(self, id, width, height):
        ## convert image
        cmds = self.formatCmdRandom(width, height, id)

        ## send commands
        for c in cmds:
            self.com.sendRawData(c)
            if not self.com.receiveAck():
                return False
        
        return True

    ##
    def saveImage(self, id, filename = "img/smiley.png"):
        ## convert image
        cmds = self.formatCmd(filename, id)

        ## send commands
        for c in cmds:
            self.com.sendRawData(c)
            if not self.com.receiveAck():
                return False
        
        return True

    def saveImage1bpp(self, id, filename = "img/smiley.png"):
        ## convert image
        cmds = self.formatCmd1Bpp(filename, id)

        ## send commands
        for c in cmds:
            self.com.sendRawData(c)
            if not self.com.receiveAck():
                return False
        
        return True

    ##
    def appendImage1Bpp(self, filename = "img/smiley.png"):
        ## convert image
        cmds = self.formatCmd1Bpp(filename)

        ## send commands
        for c in cmds:
            self.com.sendRawData(c)
            if not self.com.receiveAck():
                return False

        return True

    ##
    def appendImageRandom1Bpp(self, width, height):
        ## convert image
        cmds = self.formatCmdRandom1Bpp(width, height)

        ## send commands
        for c in cmds:
            self.com.sendRawData(c)
            if not self.com.receiveAck():
                return False

        return True

    ##
    def saveImageRandom1Bpp(self, id, width, height):
        ## convert image
        cmds = self.formatCmdRandom1Bpp(width, height, id)

        ## send commands
        for c in cmds:
            self.com.sendRawData(c)
            if not self.com.receiveAck():
                return False

        return True

    ## display an image with streaming
    def stream(self, x = 0, y = 0, filename='img/smiley.png'):
        ## convert image
        cmds = self.formatStreamCmd(filename, x, y)

        ## send commands
        for c in cmds:
            self.com.sendRawData(c)
            if not self.com.receiveAck():
                return False
        
        return True

    ## display an image with streaming
    def streamRandom(self, width, height,  x = 0, y = 0):
        ## convert image
        cmds = self.formatStreamCmdRandom(width, height, x, y)

        ## send commands
        for c in cmds:
            self.com.sendRawData(c)
            if not self.com.receiveAck():
                return False
        
        return True
