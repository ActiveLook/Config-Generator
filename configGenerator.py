import json
import os
import sys

from ALookCom.anim import Anim
from ALookCom.img import Img
from ALookCom.layout import Layout
from ALookCom.commandPub import CommandPub
from ALookCom.comBin import ComBin
from ALookCom.comFile import ComFile

import sensorParam

class ConfigGenerator:
    def __init__(self, com):
        self.cmd = CommandPub(com)
        self.anim = Anim(com)
        self.img = Img(com)
        self.layout = Layout(com)
        self.com = com

    
    def parseJson(self, path):
        # read file
        f = open(path, 'r')
        cfg = json.load(f)
        f.close()

        ## write config, without version (in case of failure)
        if 'config' in cfg:
            for config in cfg['config']:
                if config['deprecated']:
                    if not self.cmd.cfgWriteDeprecated(config['cfg'], 0, 0, 0, 0):
                        print("cmd cfgWriteDeprecated failed")
                        return False
                else:
                    if not self.cmd.cfgWrite(config['cfg'], 0, config['cfgKey']):
                        print("cmd cfgWrite failed")
                        return False

        ## save fonts
        if 'fonts' in cfg:
            for font in cfg['fonts']:
                if not self.cmd.fontSave(font['id'], font['height'], font['path'], font['first'], font['last']):
                    print("failed to save font: {}".format(font['path']))
                    return False

        ## layoutDelete
        if 'layoutDelete' in cfg:
            for layoutDelete in cfg['layoutDelete']:
                if not self.cmd.layoutDelete(layoutDelete['id']):
                    print("cmd layoutDelete failed")
                    return False 

        ## save layouts
        if 'layouts' in cfg:
            for lay in cfg['layouts']:
                cmds = []
                for c in lay['cmds']:
                    if c['type'] == 'img':
                        cmds += self.cmd.layoutCmdImg(c['id'], c['x'], c['y'])
                    elif c['type'] == 'circle':
                        cmds += self.cmd.layoutCmdCircle(c['x'], c['y'], c['r'])
                    elif c['type'] == 'circleFull':
                        cmds += self.cmd.layoutCmdCircleFull(c['x'], c['y'], c['r'])
                    elif c['type'] == 'rect':
                        cmds += self.cmd.layoutCmdRect(c['x0'], c['y0'], c['x1'], c['y1'])
                    elif c['type'] == 'rectFull':
                        cmds += self.cmd.layoutCmdRectFull(c['x0'], c['y0'], c['x1'], c['y1'])
                    elif c['type'] == 'line':
                        cmds += self.cmd.layoutCmdLine(c['x0'], c['y0'], c['x1'], c['y1'])
                    elif c['type'] == 'point':
                        cmds += self.cmd.layoutCmdPoint(c['x'], c['y'])
                    elif c['type'] == 'color':
                        cmds += self.cmd.layoutCmdGreyLvl(c['val'])
                    elif c['type'] == 'font':
                        cmds += self.cmd.layoutCmdFont(c['id'])
                    elif c['type'] == 'text':
                        cmds += self.cmd.layoutCmdText(c['x'], c['y'], c['txt'])
                    elif c['type'] == 'anim':
                        cmds += self.cmd.layoutCmdAnimDisplay(c['handlerId'], c['id'], c['delay'], c['repeat'], c['x'], c['y'])
                    else:
                        print("Layout #{}: unknown type: {}".format(lay['id'], c['type']))
                        return False

                ret = self.cmd.layoutSave(
                    id = lay['id'],
                    x0 = lay['x0'],
                    y0 = lay['y0'],
                    width = lay['width'],
                    height = lay['height'],
                    foreColor = lay['foreColor'],
                    backColor = lay['backColor'],
                    font = lay['font'],
                    txtX0 = lay['txtX0'],
                    txtY0 = lay['txtY0'],
                    txtRot = lay['txtRot'],
                    txtOpacity = lay['txtOpacity'],
                    usetxt = lay['usetxt'],
                    cmd = cmds)
                if not ret:
                    print("failed to save layout {}#".format(lay['id']))
                    return False

        ## imgDelete
        if 'imgDelete' in cfg:
            for imgDelete in cfg['imgDelete']:
                if imgDelete['deprecated']:
                    if not self.cmd.imgDeleteDeprecated(imgDelete['id']):
                        print("cmd imgDeleteDeprecated failed")
                        return False
                else:
                    if not self.cmd.imgDelete(imgDelete['id']):
                        print("cmd imgDelete failed")
                        return False 

        ## save images
        if 'imgs' in cfg:
            for img in cfg['imgs']:
                if not self.img.saveImage(img['id'], img['path']):
                    print("failed to save image: {}".format(img['path']))
                    return False


        ## save pages
        if 'pages' in cfg:
            for p in cfg['pages']:
                layouts = []
                for lay in p['layouts']:
                    layouts += [[lay['id'], lay['x'], lay['y']]]
                if not self.cmd.pageSave(p['id'], layouts):
                    print("failed to save page {}#".format(p['id']))
                    return False

        ## save animation
        if 'anim' in cfg:
            for a in cfg['anim']:
                if 'gif' in a:
                    if not self.anim.saveAnimationGif(a['id'], a['gif'], False):
                        print("failed to save animation: {}".format(a['gif']))
                        return False
                else:
                    if not self.anim.saveAnimation(a['id'], a['folder']):
                        print("failed to save animation: {}".format(a['folder']))
                        return False

        ## Sensor
        if not sensorParam.setSensorParam(self.com, cfg):
            return False

        if 'sensor' in cfg:
            for sensor in cfg['sensor']:
                if not self.cmd.enableSensor(sensor['all']):
                    print("cmd setSensorAlsArray failed")
                    return False   

        if 'luma' in cfg:
            for lum in cfg['luma']:
                if not self.cmd.luma(lum['val']):
                    print("cmd luma failed")
                    return False

        if 'timers' in cfg:
            for timer in cfg['timers']:
                if not self.cmd.setTimers(timer['id'], timer['duration']):
                    print("cmd setTimers failed")
                    return False

        ## update config version
        if 'config' in cfg:
            for config in cfg['config']:
                if config['deprecated']:
                    if not self.cmd.cfgWriteDeprecated(config['cfg'], config['cfgVersion'], config['nbBmp'], config['nbLayout'], config['nbFont']):
                        print("cmd cfgWriteDeprecated failed")
                        return False
                    if not self.cmd.cfgSetDeprecated(config['cfg']):
                        print("cmd cfgSetDeprecated failed")
                        return False
                else:
                    if not self.cmd.cfgWrite(config['cfg'], config['cfgVersion'], config['cfgKey']):
                        print("cmd cfgWrite failed")
                        return False
                    if not self.cmd.cfgSet(config['cfg']):
                        print("cmd cfgSet failed")
                        return False
        return True

    
    def cyclePages(self):
        lst = self.cmd.pageList()
        if not lst['ret']:
            print('failed to list pagess')
            return False
        
        lst = lst['ids']
        if len(lst) == 0:
            print('no page to display')
            return True

        i = 0
        while 1:
            print("Display page {}".format(lst[i]))
            strs = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
            self.cmd.clear()
            self.cmd.pageDisplay(lst[i], strs)
            i += 1
            if i >= len(lst):
                i = 0

            input('Press Enter to continue')


    def cycleLayouts(self):
        lst = self.cmd.layoutList()
        if not lst['ret']:
            print('failed to list layouts')
            return False
        
        lst = lst['layoutIdx']
        if len(lst) == 0:
            print('no layout to display')
            return True

        i = 0
        while 1:
            print("Display layout {}".format(lst[i]))
            self.cmd.clear()
            self.cmd.layoutDisplay(lst[i], str(lst[i]))
            i += 1
            if i >= len(lst):
                i = 0

            input('Press Enter to continue')


    def cycleImages(self):
        lst = self.cmd.imgList()
        if not lst['ret']:
            print('failed to list images')
            return False
        
        lst = lst['img']
        if len(lst) == 0:
            print('no image to display')
            return True

        i = 0
        while 1:
            print("Display image {}".format(lst[i][0]))
            self.cmd.clear()
            self.cmd.imgDisplay(lst[i][0], 0, 0)
            i += 1
            if i >= len(lst):
                i = 0

            input('Press Enter to continue')


##### main #####
if __name__ == '__main__':
    folder = 'cfgDescriptor'
    sub_folders = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]
    folderChoosen =''
    mode = input("mode:\n1 - Save in file\n2 - USB live test\n")
    if mode == "1":
        com = ComFile(True)
        comName = input("Enter filename\n")
    elif mode == "2":
        com = ComBin(True)
        comName = com.findDevice()
    else:
        sys.exit(1)
    
    if not comName:
        print("Activelook not connected")
        sys.exit()

    com.open(comName)
    generator = ConfigGenerator(com)
    
    temp = "Choose a file"
    for f in range(len(sub_folders)):
        temp+= f"\n{f+1}  - {sub_folders[f]}"
    temp+="\n"
    folderChoosen = sub_folders[int(input(temp))-1]

    folderPath = f"cfgDescriptor/{folderChoosen}/config.json"
    if not generator.parseJson(folderPath):
        print("failed to generate config")
    else:
        if type(generator.com) is ComFile:
            generator.com.close()
            sys.exit(0)

        mode = input("Select test mode:\n1 - Images\n2 - Layouts\n3 - Pages\n")
        if mode == "1":
            generator.cycleImages()
        elif mode == "2":
            generator.cycleLayouts()
        elif mode == "3":
            generator.cyclePages()
        else:
            print("unknown mode")

    generator.com.close()

    #input('Press Enter to exit')
    