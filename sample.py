import subprocess
import cv2
from time import sleep
from clicknium import clicknium as cc, locator, ui
import os

# Set original picture path
sourceImgPath = r'.\img\google_logo.png'
# Set the path to save the picture
savePath = r'.\img\google_logo_pixel.png'


clientRectX = 0
clientRectY = 0
maxX = 1800
maxY = 800

pR = 0
pG = 0
pB = 0


def main():
    
    global clientRectX
    global clientRectY
    global sourceImgPath

    #Adjust the picture size if necessary
    resizeSavePath = r'resize_temp.png'
    hasResize = resize_img(sourceImgPath, resizeSavePath)

    if(hasResize):
        sourceImgPath = resizeSavePath
    print(sourceImgPath)

    # Get binarization image
    binarizationSavePath = r'binar_temp.png'
    binarization(sourceImgPath,binarizationSavePath)
    
    # Open mspaint process and set client area size,background color
    open_mspaint()
    set_client_size()
    set_backgroun_color()

    # Get the coordinates of the upper left corner of the client area
    rect = ui(locator.mspaint.pane_clientarea).get_property('BoundingRectangle')
    lsRect = rect.split('{')[1].partition('}')[0].split(',')
    clientRectX = int(lsRect[0].split('=')[1])
    clientRectY = int(lsRect[1].split('=')[1])
    print(clientRectX,clientRectY)

    # Read binarization image,and get every point RGB value
    img = read_picture(binarizationSavePath)
    print(img.shape)
    max_y,max_x = img.shape[0],img.shape[1]
    dict_x_y = {}
    dict_y_x = {}
    x=0
    y=0
    while(x<max_x):
        y=0
        while(y<max_y):
            (B,G,R) = img[y][x]
            if(B==255):
                key = x
                if(key not in dict_x_y):
                    dict_x_y[key]=[y]
                else:
                    dict_x_y[key].append(y)
                key = y
                if(key not in dict_y_x):
                    dict_y_x[key]=[x]
                else:
                    dict_y_x[key].append(x)
            y+=1
        x += 1

    os.remove(binarizationSavePath)
    if(hasResize):
        os.remove(resizeSavePath)

    # Draw point on mspaint
    draw(dict_x_y,dict_y_x)

    save_file(savePath)
    print('end')

def resize_img(sourceImgPath,resizeSavePath):
    sourceImg = read_picture(sourceImgPath)
    (sourceHeight,sourceWidth,_) = sourceImg.shape
    if(sourceHeight>600 or sourceWidth>800):
        targetWidth = 0
        targetHeight = 0
        if(sourceHeight>600 and sourceWidth<=800):
            targetHeight = 600
            scale = sourceHeight/600 
            targetWidth = int(sourceWidth/scale)
        elif(sourceHeight<=600 and sourceWidth >800):
            targetWidth = 800
            scale = sourceWidth/800 
            targetHeight = int(sourceHeight/scale)
        elif(sourceHeight>600 and sourceWidth > 800):
            if(sourceWidth/sourceHeight > 800/600):
                targetWidth = 800
                scale = sourceWidth/800 
                targetHeight = int(sourceHeight/scale)
            else:
                targetHeight = 600
                scale = sourceHeight/600
                targetWidth = int(sourceWidth/scale)
        newimg = cv2.resize(sourceImg,(targetWidth,targetHeight))
        cv2.imwrite(resizeSavePath,newimg)
        return True
    return False

def open_mspaint():
    process = subprocess.Popen("mspaint")
    sleep(2)
    print('open mspaint success.')

def set_client_size():
    ui(locator.mspaint.btn_resize).click()
    ui(locator.mspaint.resize.checkbox_keep_h_v).set_checkbox(check_type='uncheck')
    ui(locator.mspaint.resize.radiobtn_pix).set_checkbox(check_type='check')
    ui(locator.mspaint.resize.edit_pix_h).set_text('1800')
    ui(locator.mspaint.resize.edit_pix_v).set_text('800')
    ui(locator.mspaint.resize.btn_resize_ok).click()

def set_backgroun_color():
    ui(locator.mspaint.btn_bgcolor).click()
    ui(locator.mspaint.pane_clientarea).click()
    ui(locator.mspaint.btn_pen).click()

def read_picture(sourceImgPath):
    if(sourceImgPath):
        image = cv2.imread(sourceImgPath)
        return image
    return None

def draw(dict_x_y,dict_y_x):
    listAlreadyDrawPoint = []
    listSinglePoint = []

    for k,v in dict_x_y.items():
        while(len(v) > 0):
            count = get_line(v)
            if(count==1):
                listSinglePoint.append([k,v.pop(0)])
            else:
                draw_line(k,v[0],k,v[count-1],255,255,255)
                for x in range(count):
                    listAlreadyDrawPoint.append([k,v.pop(0)])
    for k1,v1 in dict_y_x.items():
        while(len(v1) > 0):
            count = get_line(v1)
            if(count==1):
                tempX=v1.pop(0)
                if([tempX,k1] not in listSinglePoint):
                    listSinglePoint.append([tempX,k1])
            else:
                needDrawLine = False
                for m in range(count):
                    if([v1[m],k1] not in listAlreadyDrawPoint):
                        needDrawLine = True
                        break
                if(needDrawLine):
                    draw_line(v1[0],k1,v1[count-1],k1,255,255,255)
                for x in range(count):
                    if(needDrawLine):
                        listAlreadyDrawPoint.append([v1[0],k1])
                    v1.pop(0)
    
    for p in listSinglePoint:
        if([p[0],p[1]] not in listAlreadyDrawPoint):
            draw_point(p[0],p[1],255,255,255)

def get_line(v):
    i=v[0]
    index = 0
    while(index<len(v) and v[index] == i):
        index += 1
        i += 1
    return index

def draw_line(x,y1,x2,y2,R,G,B):
    global pR
    global maxX
    global maxY
    global clientRectX
    global clientRectY
    
    if(pR != R):
        set_pen_color(R,G,B)
        pR = R

    startX = clientRectX+5+x
    startY = clientRectY+5+y1
    endX = clientRectX+5+x2
    endY = clientRectY+5+y2
    cc.mouse.down(startX,startY)
    cc.mouse.move(endX,endY)
    cc.mouse.up(endX,endY)

def draw_point(x,y,R,G,B):
    global pR
    global maxX
    global maxY
    global clientRectX
    global clientRectY

    if(pR != R):
        set_pen_color(R,G,B)
        pR = R

    targetX = clientRectX+5+x
    targetY = clientRectY+5+y

    if(x <= maxX and y <= maxY):
        cc.mouse.click(targetX,targetY)

def set_pen_color(R,G,B):
    ui(locator.mspaint.btn_editcolor).click()
    ui(locator.mspaint.color.edit_R).set_text(R,'set-text')
    ui(locator.mspaint.color.edit_G).set_text(G,'set-text')
    ui(locator.mspaint.color.edit_B).set_text(B,'set-text')
    ui(locator.mspaint.color.btn_OK).click()

def binarization(sourceImgPath,binarizationSavePath):
    img = cv2.imread(sourceImgPath,cv2.IMREAD_GRAYSCALE)
    newImg = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 3, 5)
    cv2.imwrite(binarizationSavePath, newImg)

def save_file(path):
    if os.path.exists(path):
        os.remove(path)
    ui(locator.mspaint.save.btn_save).click()
    ui(locator.mspaint.save.edit_savepath).set_text(path)
    ui(locator.mspaint.save.btn_save_ok).click()
    print(f'save file to :{path}')

if __name__ == "__main__":
    main()
