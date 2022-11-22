## BLE abstraction Layer

import asyncio
import sys

import nest_asyncio
from bleak import BleakClient
from bleak import BleakScanner

class BleClient:
    __DEVICE_NAME_UUID   = "00002a00-0000-1000-8000-00805f9b34fb"
    __SPS_WRITE_UUID     = "0783b03e-8535-b5a0-7140-a304d2495cba"
    __SPS_READ_UUID      = "0783b03e-8535-b5a0-7140-a304d2495cb8"
    __SPS_FLOW_CTRL_UUID = "0783b03e-8535-b5a0-7140-a304d2495cb9"
    __SPS_GESTURE_UUID   = "0783b03e-8535-b5a0-7140-a304d2495cbb"
    __SPS_TOUCH_UUID     = "0783b03e-8535-b5a0-7140-a304d2495cbc"

    __RETRY              = 20

    ## constructor
    def __init__(self):
        self.__rxBuff = bytearray()

        self.__flowCtrl = 0

        nest_asyncio.apply()

    ## destructor
    def __del__(self):
        self.disconnect()
        self.__client = None

    ## read notify callback
    def __spsReadNotif(self, sender, data):
        self.__rxBuff += data

    ## flow control notify callback
    def __spsFlowCtrlNotif(self, sender, data):
        self.__flowCtrl = data[0]
    
    ## gesture event notify callback
    def __spsGestureNotif(self, sender, data):
        print("BLE: SWIPE")

    ## touch event notify callback
    def __spsTouchNotif(self, sender, data):
        print("BLE: Touch")

    ## unexpected disconnect callback
    def __unexpectedDisconnectCb(self, client):
        print("BLE: unexpected disconnect")
        self.__client = None

    ## connection runner
    async def __runConnect(self, addr):
        self.__client = BleakClient(addr)
        if sys.platform == 'win32':
            retry = self.__RETRY
            connected = False
            while (retry > 0) and not connected:
                try:
                    connected = await self.__client.connect(timeout = 30.0, use_cached  = False)
                except:
                    devices = await BleakScanner.discover()
                    addr = next((x for x in devices if x.name == addr.name), addr)

                    retry -= 1
        else:
            connected = await self.__client.connect()

        if not connected:
            print("failed to connect {}".format(addr))
            raise 
        
        retry = self.__RETRY
        done = False
        while (retry > 0) and not done:
            try:
                self.__client.set_disconnected_callback(self.__unexpectedDisconnectCb)

                ## read notification
                await self.__client.start_notify(self.__SPS_READ_UUID, self.__spsReadNotif)

                ## flow control notification
                await self.__client.start_notify(self.__SPS_FLOW_CTRL_UUID, self.__spsFlowCtrlNotif)

                ## gesture event notification
                await self.__client.start_notify(self.__SPS_GESTURE_UUID, self.__spsGestureNotif)
            
                ## touch event notification
                await self.__client.start_notify(self.__SPS_TOUCH_UUID, self.__spsTouchNotif)

                done = True
            except:
                retry -= 1

        print("Connected " + addr.name)

    ## diconnection runner
    async def __runDiconnect(self):
        if self.__client:
            await self.__client.disconnect()
        print("Disconnected")
    
    ## write gatt
    async def __runWrite(self, data):
        while self.__flowCtrl == 2:
            await asyncio.sleep(0.1)

        retry = self.__RETRY
        done = False
        while (retry > 0) and not done:
            try:
                await self.__client.write_gatt_char(self.__SPS_WRITE_UUID, data, response = True)
                done = True
            except:
                retry -= 1

    ## read runner
    async def __runRead(self, size, timeout):
        out = []

        while 1:
            if len(self.__rxBuff) >= size:
                out = self.__rxBuff[0:size]
                self.__rxBuff = self.__rxBuff[size:]
                
            if len(out) or not timeout:
                return out

            await asyncio.sleep(0.1)

            if timeout > 0.1:
                timeout -= 0.1
            else:
                timeout = 0

    ## get device name runner
    async def __runGetDeviceName(self):
        retry = self.__RETRY
        done = False
        while (retry > 0) and not done:
            try:
                rawName = await self.__client.read_gatt_char(self.__DEVICE_NAME_UUID)
                done = True
            except:
                retry -= 1
        
        return rawName.decode("ascii") 

    async def __runGetInfo(self):
        """get all info that can given when connecting in BLE"""
        linfo = {}
        for service in self.__client.services:
            for charac in service.characteristics:
                if charac.description != "Unknown":
                    if "read" in charac.properties:
                        retry = self.__RETRY
                        done = False
                        while (retry > 0) and not done:
                            try:
                                res = await self.__client.read_gatt_char(charac)
                                done = True
                            except:
                                retry -= 1
                        name = 'Name' in charac.description or 'String' in charac.description
                        if name:
                            lres = ""
                        else:
                            lres = []
                        for val in res:
                            if name:
                                lres += chr(int(val))
                            else:
                                lres.append(int(val))
                        linfo[charac.description] = lres
        return linfo

    ## connect to a device
    def connect(self, addr):
        print("Connecting " + addr.name + "...")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__runConnect(addr))

    ## diconnect from a device
    def disconnect(self):
        print("Disconnecting...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__runDiconnect())

    ## reset SPS rx buffer
    def resetRxbuffer(self):
        self.__rxBuff = bytearray()

    ## SPS write
    def write(self, data):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__runWrite(data))

    ## SPS read
    def read(self, size = 1, timeout = 1.75):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.__runRead(size, timeout))

    ## get Device name
    def getDeviceName(self):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.__runGetDeviceName())

    ## get connection MTU
    def getMtu(self):
        ## remove size of Op-Code (1 Byte) and Attribute Handle (2 Bytes)
        return self.__client.mtu_size - 3

    def getValueInfo(self):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.__runGetInfo())
