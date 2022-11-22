import os

import cv2

import utils
from img import Img
from commandPub import CommandPub


class Anim:
    def __init__(self, com):
        self.cmd = CommandPub(com)
        self.img = img = Img(com)
        self.com = com
    
    ## return the number of elements before the fist difference
    def _sameValueLen(self, la, lb):
        assert(len(la) == len(lb)), "different length is not handled"

        cnt = 0
        for a, b in zip(la, lb):
            if a == b:
                cnt += 1
            else:
                break
        
        return cnt

    ## return the number of elements before the fist difference, start counting from the end
    def _sameValueLenReverse(self, la, lb):
        assert(len(la) == len(lb)), "different length is not handled"

        cnt = 0
        i = len(la)
        while i > 0:
            i -= 1
            if la[i] == lb[i]:
                cnt += 1
            else:
                break
        
        return cnt

    ## encode full image for animation
    def _encodFullImgCmd(self, img):
        height = img.shape[0]
        width = img.shape[1]

        ## compress img 4 bit per pixel
        encodedImg = []
        for i in range(height):
            byte = 0
            shift = 0
            for j in range(width):
                ## convert gray8bit to gray4bit
                pxl = round(img[i, j] / 17)

                ## compress 4 bit per pixel
                byte += pxl << shift
                shift += 4
                if shift == 8:
                    encodedImg.append(byte)
                    byte = 0
                    shift = 0
            if shift != 0:
                encodedImg.append(byte)

        return encodedImg

    ### reduce pixel range to 16 level of grey but keep it on 1 byte
    def _reducePxlRange(self, img):
        for i, line in enumerate(img):
            for j, plx in enumerate(line):
                pxl = round(plx / 17)
                img[i][j] = pxl
        
        return img

    ## prepare command for animation saving
    def formatCmd(self, id, imgs):
        ## first image encoded as complete image
        rawAnim = self._encodFullImgCmd(imgs[0])
        imgSize = len(rawAnim)

        prev = self._reducePxlRange(imgs[0])

        width = imgs[0].shape[1]

        for img in imgs[1:]:
            img = self._reducePxlRange(img)

            ## crop width
            lines = []
            for i, line in enumerate(img):
                ## crop the line
                crop = []
                xOffset = self._sameValueLen(line, prev[i])
                if xOffset != len(line):
                    end = self._sameValueLenReverse(line, prev[i])
                    crop = line[xOffset : len(line) - end]
                
                ## transform to 4bpp compression
                byte = 0
                shift = 0
                encCrop = []
                for pxl in crop:
                    ## compress 4 bit per pixel
                    byte += pxl << shift
                    shift += 4
                    if shift == 8:
                        encCrop.append(byte)
                        byte = 0
                        shift = 0
                if shift != 0:
                    encCrop.append(byte)

                lines.append({'offset': xOffset, 'widthPxl': len(crop), 'encodedData': encCrop})
            
            ## crop height
            class BreakIt(Exception): pass
            yOffset = 0
            try:
                for line in lines:
                    if line['widthPxl'] == 0:
                        yOffset += 1
                    else:
                        ## break only the for loop
                        raise BreakIt
            except BreakIt:
                pass
                
            height = len(lines) - yOffset
            i = yOffset + height
            try:
                while (i > 0) and (height > 0):
                    i -= 1
                    if lines[i]['widthPxl'] == 0:
                        height -= 1
                    else:
                        ## break only the while loop
                            raise BreakIt
            except BreakIt:
                pass

            ## restitue data
            frame = []
            lHeight = utils.uShortToList(height)
            lYOffset = utils.sShortToList(yOffset)
            frame += lHeight + lYOffset
            for line in lines[yOffset : yOffset + height]:
                widthPxl = line['widthPxl']
                lwidthPxl = utils.uShortToList(widthPxl)
                lXOffset = utils.sShortToList(line['offset'])
                frame += lwidthPxl + lXOffset + line['encodedData']

            rawAnim += frame
            prev = img

        ## start save animation command
        data = [id]
        data += utils.intToList(len(rawAnim))
        data += utils.intToList(imgSize)
        data += utils.uShortToList(width)
        cmds = [self.com.formatFrame(0x95, data)]

        ## pack data in commands
        nbDataMax = self.com.getDataSizeMax()
        i = 0
        while i < len(rawAnim):
            if nbDataMax > (len(rawAnim) - i):
                nbDataMax = (len(rawAnim) - i)

            cmds += [self.com.formatFrame(0x95, rawAnim[i:(nbDataMax + i)])]
            i += nbDataMax

        return cmds
    
    ## prepare command for animation saving
    def formatCmdFolder(self, id, folder):
        ## list file in folder
        imgs = []
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            if os.path.isfile(path):
                img = cv2.imread(path)
                img = cv2.rotate(img, cv2.ROTATE_180)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                imgs.append(img)

        return self.formatCmd(id, imgs)

    ## prepare command for animation saving
    def formatCmdGif(self, id, gif, invertColor):

        cap = cv2.VideoCapture(gif)

        imgs = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.rotate(frame, cv2.ROTATE_180)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if invertColor:
                ## invert color
                frame = 255 - frame
            
            imgs.append(frame)
            

        cap.release()

        return self.formatCmd(id, imgs)
    
    ## save an animation, takes all images of a folder
    def saveAnimation(self, id, folder = "anim/cube-302x256"):
        ## convert image
        cmds = self.formatCmdFolder(id, folder)

        ## send commands
        for c in cmds:
            self.com.sendRawData(c)
            if not self.com.receiveAck():
                return False
        
        return True
    
    ## save an animation from a gif
    def saveAnimationGif(self, id, gif = "anim/monkey-228x228.gif", invertColor = True):
        ## convert image
        cmds = self.formatCmdGif(id, gif, invertColor)

        ## send commands
        for c in cmds:
            self.com.sendRawData(c)
            if not self.com.receiveAck():
                return False
        
        return True
