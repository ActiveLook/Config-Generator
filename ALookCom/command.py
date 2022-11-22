import struct

import numpy as np

class Command:
    CFG_NAME_LEN = 12

    def __init__(self, com):
        self.__com = com

    ## receive answer from a command
    def __rcvAnswer(self, name, cmdId):
        rcv = self.__com.receiveFrame(cmdId)
        if not rcv['ret']:
            print("{} failed to receive answer".format(name))
            return {'ret': False, 'data': []}

        ackOk = self.__com.receiveAck()
        if not ackOk:
            print("{} failed to receive ackr".format(name))
            return {'ret': False, 'data': []}
        
        return rcv