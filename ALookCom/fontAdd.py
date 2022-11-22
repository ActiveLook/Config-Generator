import string
import numpy as np


from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import utils

def char_to_pixels(text, size, path):
    font = ImageFont.truetype(path, size) 
    w, h = font.getsize(text)  
    ## ascii letters are more spaced than other caracters
    if text in string.ascii_letters:
        w += 1
    ##
    image = Image.new('L', (w, h), 1)  
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font) 
    arr = np.asarray(image)
    arr = np.where(arr, 0, 1)

    ## remove the columns of 0 in the left side
    indUn = len(arr[0])
    for l in arr:
        for i in range(len(l)):
            if l[i] == 1:
                if i < indUn:
                    indUn = i
    cropArr = np.zeros((len(arr), len(arr[0])-indUn))
    for i,l in enumerate(arr):
            cropArr[i] = l[indUn:]

    ## cropping the image to sue with the good height
    if text == " ":
        cropArr = np.array([[0 for _ in range(len(arr[0]))]])
    else:
        while not(1 in cropArr[-1]):
            cropArr = cropArr[:-1]

    ## adjust top cropping 
    n = getcrop("L", size, path)
    for _ in range(n):
        cropArr = cropArr[1:]
 
    h, w = cropArr.shape
    return cropArr


def getcrop(text, size, path):
    ## get top cropping with linear approx with size of font
    font = ImageFont.truetype(path, size) 
    w, h = font.getsize(text)  
    if text in string.ascii_letters:
        w += 1
    image = Image.new('L', (w, h), 1)  
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font) 
    arr = np.asarray(image)
    arr = np.where(arr, 0, 1)
    ind0 = 0
    for i,l in enumerate(arr):
        if (1 in l):
            ind0 = i
            break
    return ind0 - (2 + int(size/40))



def write1byte(nb0, nb1):
    return(nb0*2**4 + nb1)


def write2bytes(car, nb):
    l = []
    if car == 1:
        offset = 128
    else :
        offset = 0
    nbboucle = nb // 1016
    nbrem = nb % 1016
    ## writing 00
    for i in range(nbboucle):
        l.append(0)
        l.append(127 + offset)
    nbDouble = nbrem // 8
    nbDoubleRem = nbrem % 8
    if nbDouble != 0:
        l.append(0)
        l.append(nbDouble + offset)
    return(l, nbDoubleRem)


def pixel_to_rle(arr, height):
    h, w = arr.shape
    arr  = arr.reshape(-1)

    ## adding off lines to sue with size
    for k in range(height-h):
        arr =  list(arr) + [0 for k in range(w)]
    lhex = []
    lg = len(arr)
    i = 0
    car = int(arr[i])

    ## cpt01 [number of on pixels, number of off pixels]
    cpt01 = [0, 0]
    cpt01[car] += 1
    prev = car
    i += 1
    while (i<lg):
        car = int(arr[i])

        ## while pixels are repeated, just increment cpt01[pixel]
        if car == prev:
            cpt01[car] += 1
            prev = car
        else:
            ## switch 0 -> 1
            if car == 1:
                ## not enough pixels for 2 bytes encoding
                if cpt01[0] < 16:
                    pass
                elif cpt01[0] <= 30:
                    nb0 = cpt01[0]
                    lhex.append(write1byte(15, 0))
                    cpt01[0] = nb0 - 15
                ## 2 bytes encoding
                else:
                    nb0 = cpt01[0]
                    l, nbRem = write2bytes(0, nb0)
                    lhex = lhex + l
                    ## pixels not encoded yet
                    cpt01[0] = nbRem
                cpt01[1] += 1
            
            ##switch 1 -> 0
            else:
                ## not enough pixels for 2 bytes encoding
                if cpt01[1] < 16:
                    lhex.append(write1byte(cpt01[0], cpt01[1]))
                ## 2 bytes encoding
                else:
                    nb1 = cpt01[1] - 15
                    lhex.append(write1byte(cpt01[0], 15))
                    l, nbRem = write2bytes(1, nb1)                    
                    lhex = lhex + l
                    ## encoding on pixels missing
                    if nbRem != 0:
                        lhex.append(nbRem)
                cpt01 = [1,0]
        prev = car        
        i+=1

    ## encoding last pixels
    if (cpt01[0] < 15 and cpt01[1] <15):     
        lhex.append(write1byte(cpt01[0], cpt01[1]))
    else:
        if cpt01[1] >15:
            car = 1
            lhex.append(write1byte(cpt01[0], 15))
            nb = cpt01[1] - 15
        else:
            car = 0
            nb = cpt01[0]
        l, nbRem = write2bytes(car,nb)                    
        lhex = lhex + l
        if nbRem != 0:
            if car == 1:
                lhex.append(write1byte(0, nbRem))
            else:
                lhex.append(write1byte(nbRem, 0))
    ## adding char headers
    lhex = [0, w] + lhex
    lhex[0] = len(lhex)
    return(lhex)


## encoding without 2bytes encoding
def pixel_to_rle_no_00(arr, height):
    h, w = arr.shape
    arr  = arr.reshape(-1)
    for k in range(height-h):
        arr = [0 for k in range(w)] + list(arr)
    listhex = []
    lg = len(arr)
    ltot = []
    cpt = 1
    cptbytes = [0, 0]
    car = arr[0]
    cpt01 = [0,0]
    if car == 0:
        cptbytes[0] += 1
        cpt01[0]+=1
    else:
        cptbytes[1] += 1
        cpt01[1]+=1
        ltot.append([cpt01[0],cpt01[1]])
        cpt01 = [0,0]
        cptbytes = [0,0]
    cpt = 1
    while cpt < lg:
        zer = cptbytes[0]
        uno = cptbytes[1]
        if (zer < 15) and (uno < 15):
            curcar = arr[cpt]
            if curcar == 0 and car == 0:
                cptbytes[0] += 1
                cpt01[0]+=1
            elif curcar == 0 and car == 1:
                cptbytes[0] += 1
                ltot.append([cpt01[0], cpt01[1]])
                cpt01 = [1,0]
                cptbytes = [1,0]
                car = 0
            else:
                cptbytes[1] += 1
                cpt01[1] +=1
                car = curcar
            cpt +=1
        else:
            ltot.append([cpt01[0], cpt01[1]])
            cpt01 = [0,0]
            cptbytes = [0,0]
            car = 0
    ltot.append([cpt01[0], cpt01[1]])
    listhex = []
    for (one, zero) in ltot:
        listhex.append(one*2**4 + zero)
    listhex = [0, w] + listhex
    listhex[0] = len(listhex)
    return listhex



def rle_to_matrix(arr, height):
    line = []
    go = False
    w = arr[1]
    for elem in arr[2:]:
        if elem == 0:
            go = True
        elif go == True:
            go = False
            if elem > 128:
                for one in range((elem - 128)*8):
                    line.append(1)
            else :
                for zer in range(elem*8):
                    line.append(0)
        else :
            val0 = elem // 16
            val1 = elem % 16
            for zer in range(val0):
                line.append(0)
            for un in range(val1):
                line.append(1)
    mat = []
    for k in range(height):
        mat.append(line[k*w: (k+1)*w])
    return(mat)


def getFontData(height, path, first, last, newFormat=True):
    dataChar = []

    ofirst = ord(first)
    olast = ord(last)

    lfirst = utils.uShortToList(ofirst)
    llast = utils.uShortToList(olast)
    

    listcar = []
    for k in range(ofirst, olast + 1):
        listcar.append(chr(k))
    
    if newFormat:
        size = 6 + len(listcar)*2
    else:
        size = 256

    if newFormat:
        nbnew = 2
    else:
        nbnew = 1
    
    dataHeaders = [nbnew, height] + lfirst + llast
    prevoffset = [0x00, 0x00]
    dataoffset = []
    offset = 0
    for car in listcar:
        ## char -> pixel matrix
        arrPixel = char_to_pixels(car , height ,path)
        
        ## pixel matrix -> rle encoding
        arrHex = pixel_to_rle(arrPixel, height)        
        ##calculating size for first header
        size = size + len(arrHex)

        ##calculating offset
        offset = offset + len(arrHex)

        dataChar = dataChar + arrHex
        dataoffset = dataoffset + prevoffset
        
        prevoffset = utils.sShortToList(offset)
    nbcar = len(listcar)

    if newFormat:
        data = dataHeaders  + dataoffset + dataChar
    else:
        data = dataHeaders + dataoffset + [0x00 for k in range(2*(125-nbcar))] + dataChar

    return data, size

