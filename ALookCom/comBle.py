import struct
from time import sleep, time

from ble import Ble
from bleClient import BleClient
from com import Com
import utils

class ComBle(Com):
    __FRAME_FMT_QUERY_LEN_MSK = 0x0F

    __FRAME_HEADER_SIZE  = 1
    __FRAME_CMD_ID_SIZE  = 1
    __FRAME_FMT_SIZE     = 1
    __FRAME_FOOTER_SIZE  = 1

    __RCV_STATE_START    = 0
    __RCV_STATE_CMD_ID   = 1
    __RCV_STATE_FMT      = 2
    __RCV_STATE_LEN_MSB  = 3
    __RCV_STATE_LEN_LSB  = 4
    __RCV_STATE_QUERY    = 5
    __RCV_STATE_DATA     = 6
    __RCV_STATE_FOOTER   = 7

    ## constructor
    def __init__(self, verbose = True):
        super().__init__(verbose)
        
        self.__rcvState = self.__RCV_STATE_START
        self.__rcvCmdId = 0
        self.__rcvSizeLen = 0
        self.__rcvSize = 0
        self.__rcvQueryLen = 0
        self.__rcvQuery = []
        self.__rcvData = []
        self.__rcvDataLen = 0
        self.__rcvRawFrame = []
        self.__ble = Ble()
        self.__timeout = 1.75

    ## get frame datat size
    def __rcvGetHeaderSize(self):
        return self.__FRAME_HEADER_SIZE + self.__FRAME_CMD_ID_SIZE + self.__rcvSizeLen + self.__FRAME_FMT_SIZE + self.__rcvQueryLen

    ## get frame datat size
    def __rcvGetDataSize(self):
        return self.__rcvSize - self.__rcvGetHeaderSize() - self.__FRAME_FOOTER_SIZE

    ## decode received byte
    def __rcvByte(self, b):
        ret = False

        self.__rcvRawFrame += [b]

        if self.__rcvState == self.__RCV_STATE_START:
            if b == self.FRAME_HEADER:
                self.__rcvRawFrame = [b]
                self.__rcvSize = 0
                self.__rcvData = []
                self.__rcvQuery = []
                self.__rcvState = self.__RCV_STATE_CMD_ID
            else:
                self.printFrameError("Missing header", [b])

        elif self.__rcvState == self.__RCV_STATE_CMD_ID:
            self.__rcvCmdId = b
            self.__rcvState = self.__RCV_STATE_FMT

        elif self.__rcvState == self.__RCV_STATE_FMT:
            self.__rcvQueryLen = (b & self.__FRAME_FMT_QUERY_LEN_MSK)
            self.__rcvSize = 0
            if (b & self.FRAME_FMT_LEN_2BYTES) == self.FRAME_FMT_LEN_2BYTES:
                self.__rcvSizeLen = 2
                self.__rcvState = self.__RCV_STATE_LEN_MSB
            else:
                self.__rcvSizeLen = 1
                self.__rcvState = self.__RCV_STATE_LEN_LSB
            
        elif self.__rcvState == self.__RCV_STATE_LEN_MSB:
            self.__rcvSize = b << 8
            self.__rcvState = self.__RCV_STATE_LEN_LSB

        elif self.__rcvState == self.__RCV_STATE_LEN_LSB:
            self.__rcvSize |= b
            self.__rcvDataLen = self.__rcvGetDataSize()
            if self.__rcvQueryLen > 0:
                self.__rcvState = self.__RCV_STATE_QUERY
            elif self.__rcvDataLen > 0:
                self.__rcvState = self.__RCV_STATE_DATA
            else:
                self.__rcvState = self.__RCV_STATE_FOOTER

        elif self.__rcvState == self.__RCV_STATE_QUERY:
            self.__rcvQuery.append(b)
            if self.__rcvQueryLen == len(self.__rcvQuery):
                if self.__rcvDataLen > 0:
                    self.__rcvState = self.__RCV_STATE_DATA
                else:
                    self.__rcvState = self.__RCV_STATE_FOOTER
        
        elif self.__rcvState == self.__RCV_STATE_DATA:
            self.__rcvData.append(b)
            if self.__rcvDataLen == len(self.__rcvData):
                self.__rcvState = self.__RCV_STATE_FOOTER
        
        elif self.__rcvState == self.__RCV_STATE_FOOTER:
            if b == self.FRAME_FOOTER:
                ret = True
            else:
                self.printFrameError("Missing footer", self.__rcvRawFrame)
            self.__rcvState = self.__RCV_STATE_START

        else:
            ## failsafe
            self.__rcvState = self.__RCV_STATE_START

        return ret

    ##
    def __asyncData(self):
        ret = False
        if self.__rcvCmdId == 0xB4:
             ## USB text
             print("msg: {}".format(bytearray(self.__rcvData).decode('ascii')))
             ret = True
        elif self.__rcvCmdId == 0x07:
            ## Command echo
            self.logRawAppend(bytearray(self.__rcvData))
            ret = True
        elif self.__rcvCmdId == 0xE2:
            ## error
            print("error: cmdId = {}, err = {}, sub = {}".format(self.__rcvData[0], self.__rcvData[1], self.__rcvData[2]))
            ret = True

        return ret
    
    ## send data over serial
    def __sendData(self, data):
        ## Write size is limited by MTU
        ## work around, split data
        size = len(data)
        i = 0
        while i < size:
            subLen = size
            if subLen > self.__dev.getMtu():
                subLen = self.__dev.getMtu()
            self.__dev.write(data[i : i + subLen])
            i += subLen
        self.printFrame("Send Frame", data)
    
    ## Look for Ble device with "A.LooK " in name
    def findDevice(self):
        print("Scanning devices...")
        return self.findDeviceByName("A.LooK ")

    ## Look for Ble device who match name
    def findDeviceByName(self, name, timeout=15):
        print("Scanning for {}...".format(name))
        t1 = time()
        while abs(time()-t1) < timeout:
            devices = self.__ble.scanDevices()
            for d in devices:
                if name in d.name:
                    return d
                    

        return 

    ## Look for Ble device who match address
    def findDeviceByAddr(self, addr, timeout=15):
        print("Scanning for {}...".format(addr))
        t1 = time()
        while abs(time()-t1) < timeout:
            devices = self.__ble.scanDevices()
            for d in devices:
                if addr == d.address:
                    return d

        return 

    ## get RSSI of the device
    def getRssi(self, dev):
        return dev.rssi
    
    ## open serial
    def open(self, device):
        self.device = device
        self.__dev = BleClient()
        self.__dev.connect(device)

    ## 
    def close(self):
        self.__dev.disconnect()

    ##
    def sendFrame(self, cmdId, data):
        frame = self.formatFrame(cmdId, data)
        self.__sendData(frame)

    ## return : {'ret', 'cmdId', 'data'}
    def receiveFrame(self, cmdId):
        while 1:
            b = self.__dev.read(1, self.__timeout)
            if len(b) != 1:
                ## Timeout
                return  {'ret': False, 'cmdId': self.__rcvCmdId, 'data': self.__rcvData}

            if self.__rcvByte(b[0]):
                if self.__rcvCmdId == cmdId:
                    return  {'ret': True, 'cmdId': self.__rcvCmdId, 'data': self.__rcvData}
                else:
                    if not self.__asyncData():
                        self.printFrameError("wrong cmd Id received", self.__rcvRawFrame)
                        return  {'ret': False, 'cmdId': self.__rcvCmdId, 'data': self.__rcvData}


    ## receive answer to cmd
    def receiveAck(self):
        ## flow control is acynchronous on BLE
        while 1:
            b = self.__dev.read(1, 0)
            if len(b) != 1:
                return True
            if self.__rcvByte(b[0]):
                self.__asyncData()


    ## receive answer to cmd
    def receive(self):
        while 1:
            data = self.__dev.read(1, self.__timeout)
            if len(data) != 1:
                ## timeout
                return False
            else:
                if self.__rcvByte(data[0]):
                    if not self.__asyncData():
                        self.printFrameError("Wrong ack", self.__rcvRawFrame)

    ## send data
    def sendRawData(self, bin):
        self.__sendData(bin)

    ## get commands data max size
    def getDataSizeMax(self):
        return 512

    ## get BLE name
    def getBleName(self):
        return  self.__dev.getDeviceName()

    ## set read timeout
    def setTimeout(self, val):
        self.__timeout = val

    ## get read timeout
    def getTimeout(self):
        return self.__timeout

    def getBleInfo(self):
        return self.__dev.getValueInfo()

    def getAdvtManufacturerData(self, comName):
        return self.__ble.getAdvtManufacturerData(comName)
