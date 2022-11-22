
import struct
import time
import utils

class Com:
    FRAME_HEADER =         0xFF
    FRAME_FOOTER =         0xAA
    FRAME_FMT_LEN_2BYTES = 0x10

    ## constructor
    def __init__(self, verbose = True):
        self.__logRawFilename = None
        self.__verbose = verbose

    ## manage error in decodFrame
    def printFrameError(self, error, frame):
        if self.__verbose:
            frameLen = len(frame)
            shift = (frameLen - 1) * 8

            ## put the frame on a single integer
            val = 0
            for value in frame:
                val += (value << shift)
                shift -= 8
            
            print("Frame Error: {:x}".format(val))

            if error:
                print("Error: {}".format(error))
    
    ##
    def printFrame(self, strheader, frame):
        if self.__verbose:
            frameLen = len(frame)
            shift = (frameLen - 1) * 8

            ## put the frame on a single integer
            val = 0
            for value in frame:
                val += (value << shift)
                shift -= 8

            str = strheader + " [ {:x} ]".format(val)
            print(str)

    ## format frame before sending
    def formatFrame(self, cmdId, data):
        dataSize = len(data)
        
        frameLen = 5 + dataSize ## 5 = header + cmdId + fmt + len + footer
        lenNbByte = 1
        if frameLen > 0xFF:
            frameLen += 1
            lenNbByte = 2

        frame = []
        frame.append(self.FRAME_HEADER)               ## header
        frame.append(cmdId)                           ## cmdId
        if lenNbByte == 1:
            frame.append(0x00)                        ## fmt
            frame.append(frameLen)                    ## len
        else:
            frame.append(self.FRAME_FMT_LEN_2BYTES)   ## fmt
            frame += utils.uShortToList(frameLen)     ## len MSB + LSB

        frame += data

        frame.append(self.FRAME_FOOTER)               ## footer
        
        return bytes(frame)

    ## append to log raw file
    def logRawAppend(self, data):
        if self.__logRawFilename:
            f = open(self.__logRawFilename, "a")
            f.write("{0};{1}\n".format(time.time(), data.hex()))
            f.close()

    ## log raw data
    def logRaw(self, filename):
        self.__logRawFilename = filename

        # erase file
        f = open(filename, "w")
        f.close()

        while 1:
            self.receive()

    ## Look for a connectable device, return the device
    def findDevice(self):
        raise NotImplementedError

    ## connect to device
    def open(self, device):
        raise NotImplementedError

    ## device disconnect
    def close(self):
        raise NotImplementedError

    ##
    def sendFrame(self, cmdId, data):
        raise NotImplementedError

    ## return : {'ret', 'cmdId', 'data'}
    def receiveFrame(self, cmdId):
        raise NotImplementedError
    
    ## receive answer to cmd
    ## return True/False
    def receiveAck(self):
        raise NotImplementedError

    ## receive answer to cmd
    def receive(self):
        raise NotImplementedError

    ##
    def receiveUsbMsg(self):
        raise NotImplementedError

    ## send data
    def sendRawData(self, bin):
        raise NotImplementedError

    ## get commands data max size
    def getDataSizeMax(self):
        raise NotImplementedError

    ## set read timeout
    def setTimeout(self, val):
        raise NotImplementedError

    ## get read timeout
    def getTimeout(self):
        raise NotImplementedError