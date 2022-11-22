from serial.tools import list_ports_windows

def getUsbInfo():
    """get usb info /!\ only serial_number usefull for the moment"""
    comp = list_ports_windows.comports()
    for info in comp:
        if info.manufacturer == 'Microsoft':
            return({'name': info.name, 'manufacturer': info.manufacturer, 'serial': info.serial_number})
