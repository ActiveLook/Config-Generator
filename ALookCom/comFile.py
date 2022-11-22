

import utils
from com import Com

class ComFile(Com):

    ## constructor
    def __init__(self, verbose = True):
        super().__init__(verbose)
        self.__filename = "com-file.txt"
        self.__dummyTimeout = 1

    ## 
    def findDevice(self):
        return 

    ## open serial
    def open(self, device):
        self.__filename = device
        self.__file = f = open(self.__filename, 'w')

    ##
    def close(self):
        self.__file.close()
        
    ##
    def sendFrame(self, cmdId, data):
        frame = self.formatFrame(cmdId, data)
        str = ''.join('{:02X}'.format(x) for x in frame)
        self.__file.write(str + '\n')

    ## return : {'ret', 'cmdId', 'data'}
    def receiveFrame(self, cmdId):
        return True

    ## receive answer to cmd
    def receiveAck(self):
        return True

    ## receive answer to cmd
    def receive(self):
        return True

    ##
    def receiveUsbMsg(self):
        return True

    ## send data
    def sendRawData(self, bin):
        str = ''.join('{:02X}'.format(x) for x in bin)
        self.__file.write(str + '\n')

    ## get commands data max size
    def getDataSizeMax(self):
        return 512
    
    ## set read timeout
    def setTimeout(self, val):
        self.__dummyTimeout = val

    ## get read timeout
    def getTimeout(self):
        return self.__dummyTimeout
