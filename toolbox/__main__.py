import re
from time import sleep
import cv2
import numpy as np
from PIL import ImageGrab
import pytesseract as pt

import imutils
from imutils import perspective

from . import config
from . import util

cfg = config.load_config()

def main():
    
    while True:
        window, window_img = find_bounding_box(cfg['colors']['game_bg'], (0,0,1920,1080))
        if (type(window) is np.ndarray):
            break
        else:
            print("Waiting for Club Penguin: Rewritten window...")
            sleep(0.5)
            
    window_rect = (window[0,0], window[0,1], window[2,0], window[2,1])
    
    while True:
        board, board_img = find_bounding_box(cfg['colors']['billboard'], window_rect)
        if (type(board) is np.ndarray):
            break
        else:
            print("Waiting for pizza billboard...")
            sleep(0.5)
    
    board_abs = board
    board_w = board[1,0] - board[0,0]
    board_h = board[2,1] - board[1,1]
    
    for coord in board_abs:
        coord[0] += window[0,0]
        coord[1] += window[0,1]
    
    pizza_name_rect = (
        board_abs[0,0], 
        board_abs[0,1], 
        board_abs[2,0] - (board_w * 0.29), 
        board_abs[2,1] - (board_h * 0.76)
    )
    
    cv2.namedWindow('Output', cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow('Output', 1920, 0)
    last_pizza = ""
    last_coord = [0,0]
    while True:
        try:
            pizza, pizza_img = read_pizza_name(pizza_name_rect)
            
            if (pizza):
                cv2.imshow('Output', cv2.cvtColor(pizza_img, cv2.COLOR_BGR2RGB))
                
                if (pizza != last_pizza):
                    print(f"Found pizza: {pizza}")
                    last_pizza = pizza
                
                
                pizza_x, pizza_y = get_pizza_coord()
                if (last_coord != [pizza_x, pizza_y]):
                    print(f"Pizza located: x: {pizza_x} | Y: {pizza_y}")
                    last_coord = [pizza_x, pizza_y]
                    
            else:
                print("Waiting for new pizza...")
            
            if cv2.getWindowProperty('Output', cv2.WND_PROP_VISIBLE) > 0:
                keyCode = cv2.waitKey(50) & 0xFF
                if keyCode == 27:
                    cv2.destroyAllWindows()
                    break
            else:
                cv2.waitKey(1)
                cv2.destroyAllWindows()
            
        except KeyboardInterrupt:
            break

def find_bounding_box(filter_colors: list, screenshot_area: tuple, debug: bool=False) -> np.ndarray | np.ndarray:
    
    # load the image, mask it, and convert to grayscale
    image = np.array(ImageGrab.grab(bbox=screenshot_area))
    
    if (len(filter_colors) == 3):
        filter_low = filter_high = np.array(filter_colors)
    else:
        filter_low = np.array(filter_colors[0])
        filter_high = np.array(filter_colors[1])
        
    gray = cv2.inRange(image, filter_low, filter_high)
    
    if (debug):
        util.imshow_wait('Output: Original', image)
        util.imshow_wait('Output: Mask', gray)
        
    # perform edge detection, then perform a dilation + erosion to
    # close gaps in between object edges
    edged = cv2.Canny(gray, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    # find contours in the edge map
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[0]

    boxes = []

    # loop over the contours individually
    for c in cnts:
        # This is to ignore that small hair countour which is not big enough
        if cv2.contourArea(c) < 1000:
            continue

        # compute the rotated bounding box of the contour
        box = cv2.minAreaRect(c)
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
        box = np.array(box, dtype="int")

        # order the points in the contour such that they appear
        # in top-left, top-right, bottom-right, and bottom-left
        # order, then draw the outline of the rotated bounding
        # box
        boxes.append(perspective.order_points(box))
        
    if (len(boxes) > 0):
        return boxes[-1], image
    else:
        return None, None

def read_pizza_name(name_box: tuple):
    
    image = np.array(ImageGrab.grab(bbox=name_box))
    
    ocr_result: str = pt.image_to_string(image).lower()
    ocr_result = ocr_result.replace('-', ' ')
    cleaned_result = ""
    
    for k in ocr_result.split("\n"):
        cleaned_result += " ".join(re.findall(r"[a-zA-Z0-9]+", k))
    
    if ('pizza' in cleaned_result):
        return cleaned_result.strip('pizza'), image
    else:
        return None, None

def get_pizza_coord():
    
    # snap image
    coords, image = find_bounding_box(cfg['colors']['base'], (0,0,1920,1080))
    
    pizza_w = coords[1,0] - coords[0,0]
    pizza_h = coords[2,1] - coords [1,1]
    
    x = (coords[0,0] + coords[1,0] + coords[2,0] + coords[3,0]) / 4
    y = (coords[0,1] + coords[1,1] + coords[2,1] + coords[3,1]) / 4
            
    return x, y

if __name__ == '__main__':
    
    main()