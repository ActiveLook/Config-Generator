
import utils
import display
import fontSize
from img import Img
from commandPub import CommandPub
from comMixed import ComMixed
from comBin import ComBin
from comBle import ComBle

class Layout:
    def __init__(self, com):
        self.cmd = CommandPub(com)
        self.com = com
    

    def saveBasic(self, id, x, y, width, height, cmd = []):
        ret  = True
        ret &= self.cmd.layoutSave(
            id = id,
            x0 = x,
            y0 = y,
            width = width,
            height = height,
            foreColor = 15,
            backColor = 0,
            font = 2,
            txtX0 = width - 3,
            txtY0 = height - 3,
            txtRot = 4,
            txtOpacity = 15,
            usetxt = True,
            cmd = cmd)

        return ret


    def saveImg(self, id, x, y, width, height):
        ret = True

        imgId = 10

        img = Img(self.com)
        ret &= img.saveImageRandom(imgId, width, height)
        
        cmd = self.cmd.layoutCmdImg(imgId, 0, 0)
        ret &= self.saveBasic(id, x, y, width, height, cmd)

        return ret


    def saveRect(self, id, x, y, width, height):
        cmd = self.cmd.layoutCmdRect(0, 0, width - 1, height - 1)
        return self.saveBasic(id, x, y, width, height, cmd)


    def saveRectF(self, id, x, y, width, height):
        cmd = self.cmd.layoutCmdRectFull(0, 0, width - 1, height - 1)
        return self.saveBasic(id, x, y, width, height, cmd)


    def saveCircle(self, id, x, y, width, height):
        circleX = width // 2
        circleY = height // 2
        circleR = min([width, height]) // 2
        cmd = self.cmd.layoutCmdCircle(circleX, circleY, circleR)
        return self.saveBasic(id, x, y, width, height, cmd)


    def saveCircleF(self, id, x, y, width, height):
        circleX = width // 2
        circleY = height // 2
        circleR = min([width, height]) // 2
        cmd = self.cmd.layoutCmdCircleFull(circleX, circleY, circleR)
        return self.saveBasic(id, x, y, width, height, cmd)


    def saveLine(self, id, x, y, width, height):
        cmd = self.cmd.layoutCmdLine(0, 0, width - 1, 0)
        cmd += self.cmd.layoutCmdLine(0, height - 1, width - 1, height - 1)
        return self.saveBasic(id, x, y, width, height, cmd)


    def savePoint(self, id, x, y, width, height):
        cmd = self.cmd.layoutCmdPoint(0, 0)
        cmd += self.cmd.layoutCmdPoint(width - 1, 0)
        cmd += self.cmd.layoutCmdPoint(width - 1, height - 1)
        cmd += self.cmd.layoutCmdPoint(0, height - 1)
        return self.saveBasic(id, x, y, width, height, cmd)


    def saveTxt(self, id, x, y, width, height):
        txt1 = {'font': 1, 'txt': 'A'}
        txt2 = {'font': 2, 'txt': 'b'}
        txt3 = {'font': 3, 'txt': 'C'}
        txts = [txt1, txt2, txt3]

        cmd = []
        txtPos = 0
        for t in txts:
            txtPos = txtPos + fontSize.getStringWidth(t['font'], t['txt'])
            cmd += self.cmd.layoutCmdFont(t['font'])
            cmd += self.cmd.layoutCmdText(txtPos, fontSize.getFontHeight(t['font']), t['txt'])

        return self.saveBasic(id, x, y, width, height, cmd)


    def saveGauge(self, id, x, y, width, height):
        ret  = True

        ret &= self.cmd.cfgWriteDeprecated(1, 0, 0, 0, 0)
        ret &= self.cmd.gaugeSave(1, 0, 0, 30, 10, 5, 12, True)

        cmd = self.cmd.layoutCmdGauge(1)
        return self.saveBasic(id, x, y, width, height, cmd)

##### main #####
if __name__ == '__main__':
    com = ComBin(False)
    #comName = com.findDeviceByName("A.LooK 000295")
    comName = com.findDevice()
    if not comName:
        print("Activelook not connected")
        exit()
    
    com.open(comName)
    lay = Layout(com)

    saveFuncs = [lay.saveImg, lay.saveRect, lay.saveRectF, lay.saveCircle, lay.saveCircleF, lay.saveLine, lay.savePoint, lay.saveTxt, lay.saveGauge]
    width = 80
    height = fontSize.getFontHeight(3) + 5
    x = 0
    y = 0
    id = 0

    lay.cmd.clear()

    for f in saveFuncs:
        f(id, x, y, width, height)
        lay.cmd.layoutDisplay(id, str(id))

        id += 1
        x += width + 10
        if x + width > display.WIDTH:
            x = 0
            y += height + 10
