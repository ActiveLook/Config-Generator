import struct

from command import Command
import utils
import fontAdd

import numpy as np

class CommandPub(Command):

    def __init__(self, com):
        Command.__init__(self, com) 

    ## set the power of display and initialize display
    def powerDisplayOn(self):
        data = [1]
        self._Command__com.sendFrame(0x00, data)
        return self._Command__com.receiveAck()
    
    ## disable the power of display
    def powerDisplayOff(self):
        data = [0]
        self._Command__com.sendFrame(0x00, data)
        return self._Command__com.receiveAck()

    ## Clear the display memory (black screen)
    def clear(self):
        data = []
        self._Command__com.sendFrame(0x01, data)
        return self._Command__com.receiveAck()

    ## Set the whole display memory to the corresponding grey level
    def grey(self, grey):
        data = [grey]
        self._Command__com.sendFrame(0x02, data)
        return self._Command__com.receiveAck()

    ## Display demonstration pattern
    def demo(self, id):
        data = [id]
        self._Command__com.sendFrame(0x03, data)
        return self._Command__com.receiveAck()

    ## Set timer duration
    def setTimers(self, id, duration):
        data = [id]

        ## Since Fw 4.0.1, duration can be sent on 2 or 4 bytes
        if duration <= 65535:
            data += utils.uShortToList(duration)
        else:
            data += utils.intToList(duration)
        
        self._Command__com.sendFrame(0x04, data)
        return self._Command__com.receiveAck()


    ## Return the battery level on the bas service
    def battery(self):
        cmdId = 0x05
        name = self.battery.__name__
        data = []
        self._Command__com.sendFrame(cmdId, data)

        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return {'ret': False, 'battery': 0}

        data = rcv['data']

        ## decod data
        battLevel = data[0]

        print("{}: {}%".format(name, battLevel))
        return {'ret': True, 'battery': battLevel}

    ## Get the board ID and firmware version.
    def vers(self):
        ret = {'ret': False, 'version': [0, 0, 0, 0], 'serial': [0, 0, 0]}
        cmdId = 0x06
        name = self.vers.__name__
        data = []
        self._Command__com.sendFrame(cmdId, data)

        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return ret

        data = rcv['data']

        ## decod data
        versMajor = data[0]
        versMinor = data[1]
        versPatch = data[2]
        versChar = data[3]
        versYear = data[4]
        versWeek = data[5]
        versNumber= (data[6] << 16) | (data[7] << 8) | data[8]

        ret['ret'] = True
        ret['version'] = [versMajor, versMinor, versPatch, versChar]
        ret['serial'] = [versYear, versWeek, versNumber]

        print("{0}: {1}.{2}.{3}{4} {5:02d}{6:02d}{7:06d} ({5:02d}/{6:02d} {7:06d})".format(name, versMajor, versMinor, versPatch, chr(versChar), versYear, versWeek, versNumber))
        return ret

    ## Activate/deactivate green led: 0 = OFF, 1 = ON, 2 = toggle
    def led(self, mode):
        data = [mode]
        self._Command__com.sendFrame(0x08, data)
        return self._Command__com.receiveAck()

    ## Shift all subsequent displayed object of (x,y) pixels
    def shift(self, x, y):
        name = self.shift.__name__

        x = utils.clamp(x,-128,127)
        y = utils.clamp(y,-128,127)
        data = utils.sShortToList(x)
        data += utils.sShortToList(y)
        self._Command__com.sendFrame(0x09, data)
        return self._Command__com.receiveAck()

    ## Return the user parameters used (shift, luma, sensor)
    def settings(self):
        ret = {'ret': False, 'x': 0, 'y': 0, 'luma': 0, 'als': False, 'gesture': False} 
        cmdId = 0x0A
        name = self.settings.__name__
        data = []
        self._Command__com.sendFrame(cmdId, data)

        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return ret

        data = rcv['data']

        ## decod data
        ret['ret'] = True
        ret['x'] = np.byte(data[0])
        ret['y'] = np.byte(data[1])
        ret['luma'] = data[2]
        if data[3] != 0:
            ret['als'] = True
        else:
            ret['als'] = False
        if data[4] != 0:
            ret['gesture'] = True
        else:
            ret['gesture'] = False

        print("{}: x: {}, y: {}, luma: {}, als: {}, gesture: {}".format(name, ret['x'], ret['y'], ret['luma'], ret['als'], ret['gesture']))
        return ret

    ## set luminance
    def luma(self, luma):
        data = [luma]
        self._Command__com.sendFrame(0x10, data)
        return self._Command__com.receiveAck()

    ##
    def enableSensor(self, enable):
        data = [enable]
        self._Command__com.sendFrame(0x20, data)
        return self._Command__com.receiveAck()

    ##
    def enableGesture(self, enable):
        data = [enable]
        self._Command__com.sendFrame(0x21, data)
        return self._Command__com.receiveAck()

    ##
    def enableAls(self, enable):
        data = [enable]
        self._Command__com.sendFrame(0x22, data)
        return self._Command__com.receiveAck()

    ## set greylevel: 0x00 to 0x0F
    def color(self, greyLevel):
        name = self.color.__name__
        if 0x00 <= greyLevel <= 0x0F:
            data = [greyLevel]
            self._Command__com.sendFrame(0x30, data)
            return self._Command__com.receiveAck()
        else:
            print('{}: greylevel out of range : 0x00 <= greyLevel <= 0x0F'.format(name))
            return False

    ## Set a pixel on at the corresponding coordinates
    def point(self, x0, y0):
        data = utils.sShortToList(x0)
        data += utils.sShortToList(y0)
        self._Command__com.sendFrame(0x31, data)
        return self._Command__com.receiveAck()
    
    ## 	Draw a line at the corresponding coordinates
    def line(self, x0, y0, x1, y1):
        data = utils.sShortToList(x0)
        data += utils.sShortToList(y0)
        data += utils.sShortToList(x1)
        data += utils.sShortToList(y1)
        self._Command__com.sendFrame(0x32, data)
        return self._Command__com.receiveAck()
    
    ## draw rectangle
    def rect(self, x0, y0, x1, y1):
        data = utils.sShortToList(x0)
        data += utils.sShortToList(y0)
        data += utils.sShortToList(x1)
        data += utils.sShortToList(y1)
        self._Command__com.sendFrame(0x33, data)
        return self._Command__com.receiveAck()

    ## draw full rectangle
    def rectFull(self, x0, y0, x1, y1):
        data = utils.sShortToList(x0)
        data += utils.sShortToList(y0)
        data += utils.sShortToList(x1)
        data += utils.sShortToList(y1)
        self._Command__com.sendFrame(0x34, data)
        return self._Command__com.receiveAck()

    ## Draw an empty circle at the corresponding coordinates
    def circ(self, x, y, r):
        data = utils.sShortToList(x)
        data += utils.sShortToList(y)
        data += [r]
        self._Command__com.sendFrame(0x35, data)
        return self._Command__com.receiveAck()

    ## Draw an full circle at the corresponding coordinates
    def circFull(self, x, y, r):
        data = utils.sShortToList(x)
        data += utils.sShortToList(y)
        data += [r]
        self._Command__com.sendFrame(0x36, data)
        return self._Command__com.receiveAck()

    ## display txt
    def txt(self, x0, y0, rot, font, color, str):
        data = utils.sShortToList(x0)
        data += utils.sShortToList(y0)
        data += [rot, font, color]
        data += utils.strToList(str)
        self._Command__com.sendFrame(0x37, data)
        return self._Command__com.receiveAck()

    ## 	Draw multiples lines at the corresponding coordinates
    def polyline(self, coords = [[0, 0], [10, 10]]):
        data = []
        for x, y in coords:
            data += utils.sShortToList(x)
            data += utils.sShortToList(y)

        self._Command__com.sendFrame(0x38, data)
        return self._Command__com.receiveAck()

    ##
    def imgListDeprecated(self):
        cmdId = 0x40
        name = self.imgListDeprecated.__name__
        data = []
        self._Command__com.sendFrame(cmdId, data)

        retError = {'ret': False, 'img': []} 
        
        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return retError

        data = rcv['data']

        imgData = []
        strImgData = ""

        bin = bytearray(data)
        if len(bin):
            fmt = ">%dH" % (len(bin) / 2)
            listUShort = struct.unpack(fmt, bin)
            grp = zip(*[iter(listUShort)]*2)
            for y, x in grp:
                imgData.append([x, y])
                strImgData += " (x: {}, y: {})".format(x, y)
        
        print("{}: nbBmp {}{}".format(name, len(imgData), strImgData))
        return {'ret': True, 'img': imgData}

    ##
    def imgDisplay(self, id, x, y):
        data = [id]
        data += utils.sShortToList(x)
        data += utils.sShortToList(y)
        self._Command__com.sendFrame(0x42, data)
        return self._Command__com.receiveAck()

    ## Erase all bitmaps with numbers >= bmpId
    def imgDeleteDeprecated(self, id = 0):
        data = [id]
        self._Command__com.sendFrame(0x43, data)
        return self._Command__com.receiveAck()

    ## Erase a bitmap,  0xFF will delete all bitmaps
    def imgDelete(self, id):
        data = [id]
        self._Command__com.sendFrame(0x46, data)
        return self._Command__com.receiveAck()

    ##
    def imgList(self):
        cmdId = 0x47
        name = self.imgList.__name__
        data = []
        self._Command__com.sendFrame(cmdId, data)

        retError = {'ret': False, 'img': []} 
        
        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return retError

        data = rcv['data']

        imgData = []
        strImgData = ""

        i = 0
        while i < len(data):
            id = data[i]
            y = utils.listToShort(data[i + 1:i + 3])
            x = utils.listToShort(data[i + 3:i + 5])

            imgData.append([id, x, y])
            strImgData += " (Id: {}, x: {}, y: {})".format(id, x, y)

            i += 5

        print("{}: nbImg {}{}".format(name, len(imgData), strImgData))
        return {'ret': True, 'img': imgData}

    ## Font functions 

    def fontList(self):
        cmdId = 0x50
        name = self.fontList.__name__
        data = []
        self._Command__com.sendFrame(cmdId, data)
        rcv = self._Command__rcvAnswer(name, cmdId)
 
        retError = {'ret': False, 'font': []} 
        
        if not rcv['ret']:
            return retError

        data = rcv['data']
        
        fontData = []
        i = 0
        while i < len(data):
            id = data[i]
            height = data[i+1]
            fontData.append([id, height])
            i +=2

        return {'ret': True, 'font': fontData}


    def fontSave(self, idfont, height, path, first, last, newFormat=True):
        cmdId = 0x51

        data, size = fontAdd.getFontData(height, path, first, last, newFormat=True)

        ##premier chunk init idfont et size
        name = self.fontList.__name__
        lsize = utils.uShortToList(size)
        dataFirstHeader =  [idfont] + lsize
        self._Command__com.sendFrame(cmdId, dataFirstHeader)
        if not self._Command__com.receiveAck():
            return False
        sendsize = self._Command__com.getDataSizeMax() - 5
        quot = len(data) // sendsize
        i = 0
        ## sending final data
        for k in range(quot):
            arrfin = data[i:i+sendsize]
            self._Command__com.sendFrame(cmdId ,arrfin)
            if not self._Command__com.receiveAck():
                return False
            i = i+sendsize
        ## missing data after packeting them
        arrfin = data[i:]
        self._Command__com.sendFrame(cmdId ,arrfin)
        return(self._Command__com.receiveAck())


    def fontSelect(self, font):
        cmdId = 0x52
        name = self.fontList.__name__
        data = [font]
        self._Command__com.sendFrame(cmdId, data)
        return self._Command__com.receiveAck()       


    def fontDelete(self, font):
        cmdId = 0x53
        name = self.fontList.__name__
        data = [font]
        self._Command__com.sendFrame(cmdId, data)
        return self._Command__com.receiveAck()       


    ## predefined layout ID
    LAYOUT_BOOT_ID =               0
    LAYOUT_CONNECT_DEVICE_ID =     2
    LAYOUT_CONNECTED_ID =          3
    LAYOUT_CONNECTION_LOST_ID =    4
    LAYOUT_BYE_BYE_ID =            5
    LAYOUT_BATTERY_ID =            7
    LAYOUT_SUOTA_ID =              9

    ## format layout bitmap additional command
    def layoutCmdImg(self, id, x, y):
        data = [0x00, id]
        data += utils.sShortToList(x)
        data += utils.sShortToList(y)
        return data

    ## format layout circle additional command
    def layoutCmdCircle(self, x, y, r):
        data = [0x01]
        data += utils.sShortToList(x)
        data += utils.sShortToList(y)
        data += utils.uShortToList(r)
        return data
    
    ## format layout full circle additional command
    def layoutCmdCircleFull(self, x, y, r):
        data = [0x02]
        data += utils.sShortToList(x)
        data += utils.sShortToList(y)
        data += utils.uShortToList(r)
        return data

    ## format layout grey level additional command
    def layoutCmdGreyLvl(self, level):
        data = [0x03, level]
        return data

    ## format layout font additional command
    def layoutCmdFont(self, font):
        data = [0x04, font]
        return data

    ## format layout line additional command
    def layoutCmdLine(self, x0, y0, x1, y1):
        data = [0x05]
        data += utils.sShortToList(x0)
        data += utils.sShortToList(y0)
        data += utils.sShortToList(x1)
        data += utils.sShortToList(y1)
        return data

    ## format layout point additional command
    def layoutCmdPoint(self, x, y):
        data = [0x06]
        data += utils.sShortToList(x)
        data += utils.sShortToList(y)
        return data

    ## format layout rectangle additional command
    def layoutCmdRect(self, x0, y0, x1, y1):
        data = [0x07]
        data += utils.sShortToList(x0)
        data += utils.sShortToList(y0)
        data += utils.sShortToList(x1)
        data += utils.sShortToList(y1)
        return data
    
    ## format layout full rectangle additional command
    def layoutCmdRectFull(self, x0, y0, x1, y1):
        data = [0x08]
        data += utils.sShortToList(x0)
        data += utils.sShortToList(y0)
        data += utils.sShortToList(x1)
        data += utils.sShortToList(y1)
        return data

    ## format layout text additional command
    def layoutCmdText(self, x, y, txt):
        data = [0x09]
        data += utils.sShortToList(x)
        data += utils.sShortToList(y)
        data += [len(txt)]
        data += [ord(char) for char in txt] ## convert string to list
        return data

    ## format layout gauge additional command
    def layoutCmdGauge(self, gaugeId):
        data = [0x0A, gaugeId]
        return data

    ## format layout animation display additional command
    def layoutCmdAnimDisplay(self, handlerId, id, delay, repeat, x, y):
        data = [0x0B, handlerId, id]
        data += utils.uShortToList(delay)
        data += [repeat]
        data += utils.sShortToList(x)
        data += utils.sShortToList(y)
        return data
    
    
    ## save layout with text only
    ## foreColor: 0 to 0xF
    def layoutSave(self, id, x0, y0, width, height, foreColor, backColor, font, txtX0, txtY0, txtRot, txtOpacity, usetxt = True, cmd = []):
        name = self.layoutSave.__name__

        if not 0x00 <= foreColor <= 0x0F:
                print("{}: foreColor out of range, need to be 0 <= {} <= 15".format(name, foreColor))
        if not 0x00 <= backColor <= 0x0F:
                print("{}: backColor out of range, need to be 0 <= {} <= 15".format(name, backColor))

        textValid = 0
        if (usetxt):
            textValid = 1

        data = [id, len(cmd)]
        data += utils.uShortToList(x0)
        data += [y0]
        data += utils.uShortToList(width)
        data += [height, foreColor, backColor, font, textValid]
        data += utils.uShortToList(txtX0)
        data += [txtY0, txtRot, txtOpacity]
        data += cmd

        self._Command__com.sendFrame(0x60, data)
        return self._Command__com.receiveAck()

    ## erase layout
    def layoutDelete(self, id):
        data = [id]
        self._Command__com.sendFrame(0x61, data)
        return self._Command__com.receiveAck()

    ## display layout
    def layoutDisplay(self, id, str):
        data = [id]
        data += utils.strToList(str)
        self._Command__com.sendFrame(0x62, data)
        return self._Command__com.receiveAck()

    ## clear layout
    def layoutClear(self, id):
        data = [id]
        self._Command__com.sendFrame(0x63, data)
        return self._Command__com.receiveAck()

    ## list layout
    ## return : {'ret', 'layoutIdx'}
    def layoutList(self):
        cmdId = 0x64
        name = self.layoutList.__name__
        self._Command__com.sendFrame(cmdId, [])

        retError = {'ret': False, 'layoutIdx': []} 
        
        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return retError

        layoutIdx = rcv['data']

        print("{}: nb {}: {}".format(name, len(layoutIdx), layoutIdx))
        return {'ret': True, 'layoutIdx': layoutIdx}

    ## change layout position
    def layoutPos(self, id, x, y):
        data = [id]
        data += utils.uShortToList(x)
        data += [y]
        self._Command__com.sendFrame(0x65, data)
        return self._Command__com.receiveAck()

    ## display layout
    def layoutEx(self, id, x, y, str):
        data = [id]
        data += utils.uShortToList(x)
        data += [y]
        data += utils.strToList(str)
        self._Command__com.sendFrame(0x66, data)
        return self._Command__com.receiveAck()
    
    ## list layout
    ## return : {'ret', 'layoutIdx'}
    def layoutGet(self, layoutId):
        cmdId = 0x67
        name = self.layoutGet.__name__
        data = [layoutId]
        self._Command__com.sendFrame(cmdId, data)
        ret = {'ret': False, 'size': 0, 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'foreColor': 0, 'backColor': 0, 'font': 0, 'textValid': 0, 'txtX0': 0, 'txtY0': 0, 'txtRot': 0, 'txtOpacity': 0, 'cmd': []} 
        
        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return ret

        data = rcv['data']
        ret['ret'] = True
        ret['size'] = data[0]
        ret['x'] = utils.listToUShort(data[1:3])
        ret['y'] =  data[3]
        ret['width'] = utils.listToUShort(data[4:6])
        ret['height'] = data[6]
        ret['foreColor'] = data[7]
        ret['backColor'] = data[8]
        ret['font'] = data[9]
        ret['textValid'] = data[10]
        ret['txtX0'] = utils.listToUShort(data[11:13])
        ret['txtY0'] = data[13]
        ret['txtRot'] = data[14]
        ret['txtOpacity'] = data[15]
        ret['cmd'] = data[16:]

        print("layout #{} x: {}, y: {}, width: {}, height: {}, foreColor: {}, backColor: {}, font: {}, textValid: {}, txtX0: {}, txtY0: {}, txtRot: {}, txtOpacity: {}".format(
            layoutId, ret['x'], ret['y'], ret['width'], ret['height'], ret['foreColor'], ret['backColor'], ret['font'], ret['textValid'], ret['txtX0'], ret['txtY0'], ret['txtRot'], ret['txtOpacity']
        ))
        
        return ret

    ## clear a layout at a spicific position
    def layoutClearEx(self, id, x, y):
        data = [id]
        data += utils.uShortToList(x)
        data += [y]
        self._Command__com.sendFrame(0x68, data)
        return self._Command__com.receiveAck()

    ## Display value (in percentage) of the gauge
    def gaugeDisplay(self, id, value):
        data = [id, value]
        self._Command__com.sendFrame(0x70, data)
        return self._Command__com.receiveAck()

    ## Save the parameters for the gauge nb
    def gaugeSave(self, id, x, y, rExt, rIn, startCoord, endCoord, clockWise):
        clockWiseNum = 1 if clockWise else 0
        data = [id]
        data += utils.sShortToList(x)
        data += utils.sShortToList(y)
        data += utils.uShortToList(rExt)
        data += utils.uShortToList(rIn)
        data += [startCoord, endCoord, clockWiseNum]
        self._Command__com.sendFrame(0x71, data)
        return self._Command__com.receiveAck()

    ## delete a gauge, 0xFF delete all gauges
    def gaugeDelete(self, id):
        data = [id]
        self._Command__com.sendFrame(0x72, data)
        return self._Command__com.receiveAck()

    ##
    def gaugeList(self):
        ret = {'ret': False, 'ids': []} 
        cmdId = 0x73
        name = self.gaugeList.__name__
        self._Command__com.sendFrame(cmdId, [])

        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return ret

        ids = rcv['data']

        ret['ret'] = True
        ret['ids'] = ids

        print("{}: {}".format(name, ids))
        return ret

    ##
    def gaugeGet(self, id):
        ret = {'ret': False, 'x': 0, 'y': 0, 'r': 0, 'rIn': 0, 'start': 0, 'end': 0, 'clockWise': False} 
        cmdId = 0x74
        name = self.gaugeGet.__name__
        self._Command__com.sendFrame(cmdId, [id])

        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return ret

        data = rcv['data']

        ret['ret'] = True
        ret['x'] = utils.listToShort(data[0:2])
        ret['y'] = utils.listToShort(data[2:4])
        ret['r'] = utils.listToUShort(data[4:6])
        ret['rIn'] = utils.listToUShort(data[6:8])
        ret['start'] = data[8]
        ret['end'] = data[9]
        ret['clockWise'] = bool(data[10])

        print("{}: #{} x: {}, y: {}, r: {}, rIn: {}, start: {}, end: {}, clockWise: {}".format(name, id, ret['x'], ret['y'], ret['r'], ret['rIn'], ret['start'], ret['end'], ret['clockWise']))
        return ret

    ##
    def pageSave(self, id, layouts = [[0x01, 0, 0]]):
        data = [id]
        for layoutId, x, y in layouts:
            data += [layoutId]
            data += utils.uShortToList(x)
            data += [y]
        
        self._Command__com.sendFrame(0x80, data)
        return self._Command__com.receiveAck()
    
    ##
    def pageGet(self, id):
        ret = {'ret': False, 'id': -1, 'data': []} 
        cmdId = 0x81
        name = self.pageGet.__name__
        self._Command__com.sendFrame(cmdId, [id])

        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return ret

        data = rcv['data']

        layouts = []
        msg = ""

        id = data[0]
        for i in range(1, len(data), 4):
            layoutId = data[i]
            i += 1
            x = utils.listToUShort(data[i:i+2])
            i += 2
            y = data[i]
            layouts.append([layoutId, x, y])
            msg += " (id: {}, x: {}, y: {})".format(layoutId, x, y)

        ret['ret'] = True
        ret['id'] = id
        ret['data'] = layouts

        print("{}: #{}{}".format(name, id, msg))
        return ret

    ##
    def pageDelete(self, id):
        data = [id]
        self._Command__com.sendFrame(0x82, data)
        return self._Command__com.receiveAck()
    
    ##
    def pageDisplay(self, id, strings = ["1", "2"]):
        data = [id]
        for s in strings:
            data += utils.strToList(s)
        self._Command__com.sendFrame(0x83, data)
        return self._Command__com.receiveAck()

    ##
    def pageClear(self, id):
        data = [id]
        self._Command__com.sendFrame(0x84, data)
        return self._Command__com.receiveAck()

    ##
    def pageList(self):
        ret = {'ret': False, 'ids': []} 
        cmdId = 0x85
        name = self.pageList.__name__
        self._Command__com.sendFrame(cmdId, [])

        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return ret

        ids = rcv['data']

        ret['ret'] = True
        ret['ids'] = ids

        print("{}: {}".format(name, ids))
        return ret

    ## Delete an animation
    def animDelete(self, id):
        data = [id]
        self._Command__com.sendFrame(0x96, data)
        return self._Command__com.receiveAck()

    ## Display animation
    def animDisplay(self, handlerId, id, delay, repeat, x, y):
        data = [handlerId, id]
        data += utils.uShortToList(delay)
        data += [repeat]
        data += utils.sShortToList(x)
        data += utils.sShortToList(y)
        self._Command__com.sendFrame(0x97, data)
        return self._Command__com.receiveAck()

    ## Stop and clear the screen of the corresponding animation
    def animClear(self, handlerId):
        data = [handlerId]
        self._Command__com.sendFrame(0x98, data)
        return self._Command__com.receiveAck()

    ##
    def animList(self):
        ret = {'ret': False, 'ids': []} 
        cmdId = 0x99
        name = self.animList.__name__
        self._Command__com.sendFrame(cmdId, [])

        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return ret

        ids = rcv['data']

        ret['ret'] = True
        ret['ids'] = ids

        print("{}: {}".format(name, ids))
        return ret
    
    ## write config ID
    def cfgWriteDeprecated(self, cfgIdx, cfgId, nbBmp, nblayout, nbFont):
        data = [cfgIdx]
        data += utils.intToList(cfgId)
        data += [nbBmp, nblayout, nbFont]
        self._Command__com.sendFrame(0xA1, data)
        return self._Command__com.receiveAck()

    ## read config ID
    ## return : {'ret', 'cfgIdx', 'cfgId', 'nbBmp', 'nblayout', 'nbFont'}
    def cfgReadDeprecated(self, cfgIdx):
        ret = {'ret': False, 'cfgId': 0, 'nbBmp': 0, 'nblayout': 0, 'nbFont': 0}
        cmdId = 0xA2
        name = self.cfgReadDeprecated.__name__
        data = [cfgIdx]
        self._Command__com.sendFrame(cmdId, data)
        
        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return ret

        data = rcv['data']

        ## decod data
        cfgId = utils.listToUInt(data[1:5])
        nbBmp = data[5]
        nblayout = data[6]
        nbFont = data[7]

        print("{}: idx: {} id: {:x} nbBmp: {} nblayout: {} nbFont {}".format(name, cfgIdx, cfgId, nbBmp, nblayout, nbFont))
        return {'ret': True, 'cfgIdx': cfgIdx, 'cfgId': cfgId, 'nbBmp': nbBmp, 'nblayout': nblayout, 'nbFont': nbFont}

    ## set config
    def cfgSetDeprecated(self, cfgidx):
        data = [cfgidx]
        self._Command__com.sendFrame(0xA3, data)
        return self._Command__com.receiveAck()

    ## Get number of pixel activated on display
    def pixelCount(self, verb=True):
        ret = {'ret': False, 'count': 0}
        cmdId = 0xA5
        name = self.pixelCount.__name__
        data = []
        self._Command__com.sendFrame(cmdId, data)
        
        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return ret

        data = rcv['data']

        ## decod data
        ret['ret'] = True
        ret['count'] = utils.listToUInt(data)
        if verb:
            print("{}: {}".format(name, ret['count']))
        return ret

    ## get battery charging counter
    def getChargingCounter(self):
        ret = {'ret': False, 'counter': 0}
        cmdId = 0xA7
        name = self.getChargingCounter.__name__
        data = []
        self._Command__com.sendFrame(cmdId, data)
        
        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return ret

        data = rcv['data']

        ## decod data
        ret['ret'] = True
        ret['counter'] = utils.listToUInt(data)

        print("{}: {}".format(name, ret['counter']))
        return ret

    ## Get total number of charging minute
    def getChargingTime(self):
        ret = {'ret': False, 'time': 0}
        cmdId = 0xA8
        name = self.getChargingTime.__name__
        data = []
        self._Command__com.sendFrame(cmdId, data)
        
        rcv = self._Command__rcvAnswer(name, cmdId)
        if not rcv['ret']:
            return ret

        data = rcv['data']

        ## decod data
        ret['ret'] = True
        ret['time'] = utils.listToUInt(data)

        print("{}: {}".format(name, ret['time']))
        return ret

    ## Reset charging counter and charging time value in Param
    def resetChargingParam(self):
        self._Command__com.sendFrame(0xAA, [])
        return self._Command__com.receiveAck()

    ## Write configuration
    def cfgWrite(self, name, version, password):
        data = utils.strToList(name, self.CFG_NAME_LEN)
        data += utils.intToList(version)
        data += utils.intToList(password)
        self._Command__com.sendFrame(0xD0, data)
        return self._Command__com.receiveAck()

    ## Read configuration
    def cfgRead(self, name):
        bak = self._Command__com.getTimeout()
        self._Command__com.setTimeout(15.0)

        cmdId = 0xD1
        funcName = self.cfgRead.__name__
        ret = {'ret': False, 'version': 0, 'nbImg': 0, 'nbLayout': 0, 'nbFont': 0, 'nbPage': 0, 'nbGauge': 0}
        data = utils.strToList(name, self.CFG_NAME_LEN)
        self._Command__com.sendFrame(cmdId, data)

        rcv = self._Command__rcvAnswer(funcName, cmdId)
        if not rcv['ret']:
            return ret

        self._Command__com.setTimeout(bak)

        ret['ret'] = True
        ret['version'] = utils.listToUInt(rcv['data'][0:4])
        ret['nbImg'] = rcv['data'][4]
        ret['nbLayout'] = rcv['data'][5]
        ret['nbFont'] = rcv['data'][6]
        ret['nbPage'] = rcv['data'][7]
        ret['nbGauge'] = rcv['data'][8]

        print("{}: version: {}, nbImg: {}, nbLayout: {}, nbFont: {}, nbPage: {}, nbGauge: {}".format(funcName, ret['version'], ret['nbImg'], ret['nbLayout'], ret['nbFont'], ret['nbPage'], ret['nbGauge']))
        
        return ret

    ## Select the current configuration used to display layouts, images, etc
    def cfgSet(self, name):
        data = utils.strToList(name, self.CFG_NAME_LEN)
        self._Command__com.sendFrame(0xD2, data)
        return self._Command__com.receiveAck()

    ## List configurations in memory
    def cfgList(self):
        bak = self._Command__com.getTimeout()
        self._Command__com.setTimeout(15.0)

        cmdId = 0xD3
        data = []
        self._Command__com.sendFrame(cmdId, data)
        ret = {'ret': False, 'cfg': []}

        rcv = self._Command__rcvAnswer(self.cfgList.__name__, cmdId)
        if not rcv['ret']:
            return ret

        self._Command__com.setTimeout(bak)
        
        i = 0
        data = rcv['data']
        while i < len(data):
            cfg = {'name': "", 'size': 0, 'version': 0, 'usgCnt': 0, 'installCnt': 0, 'isSystem': 0}

            cfg['name'] = utils.listToStr(data[i:], self.CFG_NAME_LEN)
            nameLen = len(cfg['name'])
            if nameLen < self.CFG_NAME_LEN:
                i += nameLen + 1 ## ignore '\0'
            else:
                i += self.CFG_NAME_LEN
            
            cfg['size'] = utils.listToUInt(data[i:i+4])
            i += 4

            cfg['version'] = utils.listToUInt(data[i:i+4])
            i += 4

            cfg['usgCnt'] = data[i]
            i += 1

            cfg['installCnt'] = data[i]
            i += 1

            cfg['isSystem'] = data[i]
            i += 1

            ret['cfg'].append(cfg)
            print("cfg: {: <12} size: {: >3} kb, version: {: >5}, usgCnt: {}, installCnt: {}, isSystem: {}".format(cfg['name'], cfg['size'] // 1024, cfg['version'], cfg['usgCnt'], cfg['installCnt'], cfg['isSystem']))

        ret['ret'] = True

        return ret

    ## rename a configuration
    def cfgRename(self, oldName, newName, password):
        data = utils.strToList(oldName, self.CFG_NAME_LEN)
        data += utils.strToList(newName, self.CFG_NAME_LEN)
        data += utils.intToList(password)
        self._Command__com.sendFrame(0xD4, data)
        return self._Command__com.receiveAck()

    ## delete a configuration
    def cfgDelete(self, name, usePassword = False, password = 0):
        bak = self._Command__com.getTimeout()
        self._Command__com.setTimeout(20.0)

        data = utils.strToList(name, self.CFG_NAME_LEN)
        if usePassword:
            data += utils.intToList(password)
        self._Command__com.sendFrame(0xD5, data)
        ret = self._Command__com.receiveAck()

        self._Command__com.setTimeout(bak)

        return ret

    ## 	Delete the configuration that has not been used for the longest time
    def cfgDeleteLessUsed(self):
        bak = self._Command__com.getTimeout()
        self._Command__com.setTimeout(20.0)

        data = []
        self._Command__com.sendFrame(0xD6, data)
        ret = self._Command__com.receiveAck()

        self._Command__com.setTimeout(bak)

        return ret

    ## get free space available
    def cfgFreeSpace(self):
        bak = self._Command__com.getTimeout()
        self._Command__com.setTimeout(20.0)

        cmdId = 0xD7
        data = []
        self._Command__com.sendFrame(cmdId, data)
        ret = {'ret': False, 'totalSize': 0, 'freeSpace': 0}
        
        rcv = self._Command__rcvAnswer(self.cfgFreeSpace.__name__, cmdId)
        if not rcv['ret']:
            return ret

        self._Command__com.setTimeout(bak)

        totalSize = utils.listToUInt(rcv['data'][0:4])
        freeSpace = utils.listToUInt(rcv['data'][4:8])

        print("Cfg: totalSize: {} kB, freeSpace: {} kB, usedSpace: {} kB".format(totalSize // 1024, freeSpace // 1024, (totalSize - freeSpace) // 1024))
        ret['ret'] = True
        ret['totalSize'] = totalSize
        ret['freeSpace'] = freeSpace

        return ret

    ## get number of config
    def cfgGetNb(self):
        cmdId = 0xD8
        data = []
        self._Command__com.sendFrame(cmdId, data)
        ret = {'ret': False, 'nb': 0}

        rcv = self._Command__rcvAnswer(self.cfgGetNb.__name__, cmdId)
        if not rcv['ret']:
            return ret

        nb = rcv['data'][0]

        print("Cfg: nb:{}".format(nb))
        ret['ret'] = True
        ret['nb'] = nb

        return ret

    ## Shutdown the device
    def shutdown(self):
        data = [0x6F, 0x7F, 0xC4, 0xEE]
        self._Command__com.sendFrame(0xE0, data)
        return self._Command__com.receiveAck()

    ## Reset the device
    def reset(self):
        data = [0x5C, 0x1E, 0x2D, 0xE9]
        self._Command__com.sendFrame(0xE1, data)
        return self._Command__com.receiveAck()
    
    ## Read deivce info parameter
    PROD_PARAM_ID_HW_PLATFORM = 0
    PROD_PARAM_ID_MANUFACTURER = 1
    PROD_PARAM_ID_MFR_ID = 2
    PROD_PARAM_ID_MODEL = 3
    PROD_PARAM_ID_SUB_MODEL = 4
    PROD_PARAM_ID_FW_VERSION = 5
    PROD_PARAM_ID_SERIAL_NUMBER = 6
    PROD_PARAM_ID_BATT_MODEL = 7
    PROD_PARAM_ID_LENS_MODEL = 8
    PROD_PARAM_ID_DISPLAY_MODEL = 9
    PROD_PARAM_ID_DISPLAY_ORIENTATION = 10
    PROD_PARAM_ID_CERTIF_1 = 11
    PROD_PARAM_ID_CERTIF_2 = 12
    PROD_PARAM_ID_CERTIF_3 = 13
    PROD_PARAM_ID_CERTIF_4 = 14
    PROD_PARAM_ID_CERTIF_5 = 15
    PROD_PARAM_ID_CERTIF_6 = 16
    def rdDevInfo(self, paramId):
        cmdId = 0xE3
        data = [paramId]
        self._Command__com.sendFrame(cmdId, data)
        ret = {'ret': False, 'data': []}

        rcv = self._Command__rcvAnswer(self.rdDevInfo.__name__, cmdId)
        if not rcv['ret']:
            return ret

        ret['ret'] = True
        ret['data'] =  rcv['data']

        intFmt = ', '.join(str(i) for i in rcv['data'])
        hexFmt = ', '.join('0x{:02X}'.format(x) for x in rcv['data'])
        strFmt = ''.join(chr(c) for c in rcv['data'])

        idName = ["HW_PLATFORM", "MANUFACTURER", "MFR_ID", "PRODUCT_TYPE", "SUB_MODEL", "FW_VERSION", "SERIAL_NUMBER", "BATT_MODEL", "LENS_MODEL", "DISPLAY_MODEL", "DISPLAY_ORIENTATION", "CERTIF_1", "CERTIF_2", "CERTIF_3", "CERTIF_4", "CERTIF_5", "CERTIF_6"]
        print("{}:\n\tint: [{}]\n\thex: [{}]\n\tstr: [{}]".format(idName[paramId], intFmt, hexFmt, strFmt))

        return ret
