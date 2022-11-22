## BLE abstraction Layer

import asyncio
from bleak import BleakScanner

class Ble:
    ## get device rssi
    def __getRssi(self, dev):
        return dev.rssi
    
    ## runner to scan devices
    async def __runScanDevices(self):
        devices = await BleakScanner.discover(timeout = 2.5)
        for d in devices:
            self.__scannedDev.append(d)

    ## scan for devices
    def scanDevices(self):
        self.__scannedDev = []

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__runScanDevices())

        ## sort by RSSI
        self.__scannedDev.sort(key=self.__getRssi, reverse=True)

        return self.__scannedDev
    
    def getAdvtManufacturerData(self, dev):
        return dev.metadata['manufacturer_data']
