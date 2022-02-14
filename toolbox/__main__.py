import re
from time import sleep
import time
from types import NoneType
import cv2
import numpy as np
from PIL import ImageGrab
import pytesseract as pt

import imutils
from imutils import perspective

from . import config
from . import util
from .preview import PizzaPreview

cfg = config.load_config()
preview = PizzaPreview()

def main():
    
    cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
            
    print("Waiting for pizza billboard...")
    while True:
        image = util.screenshot()
        board = get_boundary(cfg['colors']['billboard'], image)
        if (type(board) == np.ndarray):
            preview.update_billboard(board)
            break
            
    while True:
        sauce_found = False
        image = util.screenshot()
        
        sauce_main_bound = get_boundary(cfg['colors']['pizza_sauce'], image)
        if (type(sauce_main_bound) == np.ndarray):
            sauce_alt_bound = get_boundary(cfg['colors']['hot_sauce'], image)
            sauce_found = True
            
        else:
            sauce_main_bound = get_boundary(cfg['colors']['choc_sauce'], image)
            if (type(sauce_main_bound) == np.ndarray):
                sauce_alt_bound = get_boundary(cfg['colors']['pink_sauce'], image)
                sauce_found = True
            else:
                print("WHERE IS THE lAmB S A U C E!?")
        
        if (sauce_found):
            sauce_main_x, sauce_main_y = get_center(sauce_main_bound)
            sauce_alt_x, sauce_alt_y = get_center(sauce_alt_bound)
            
            preview.update_sauce_bounds(sauce_main_bound, sauce_alt_bound)
            preview.update_sauce_pos((sauce_main_x, sauce_main_y), (sauce_alt_x, sauce_alt_y))
            
            break
    
    board_w = board[1,0] - board[0,0]
    board_h = board[2,1] - board[1,1]
    
    recipe_coords = (
        board[0,0], 
        board[0,1], 
        board[2,0] - (board_w * 0.29), 
        board[2,1] - (board_h * 0.76)
    )
    
    time_to_ocr = 0
    last_recipe = ""
    
    while True:
        start_time = time.process_time()
        
        try:
        
            image = util.screenshot()
            preview.update_image(image)
            
            if (time_to_ocr < cfg['ocr']['ticks_between_reads']):
                
                # fetch recipe via OCR 
                recipe = get_recipe(recipe_coords)
                if (type(recipe) != str):
                    continue
                
                elif (recipe != last_recipe):
                    print(f"Found recipe: {recipe}")
                    last_recipe = recipe
                
                time_to_ocr += 1
            else:
                time_to_ocr = 0
                
            # use boundary detection to track current x,y of pizzas center
            pizza_bound = get_boundary(cfg['colors']['pizza_base'], image)
            if (type(pizza_bound) == np.ndarray):
                pizza_x, pizza_y = get_center(pizza_bound)
                preview.update_pizza_bound(pizza_bound)
                preview.update_pizza_pos((pizza_x, pizza_y))
            
            # toppings = util.get_toppings(recipe)
            
            cv2.imshow('Output', preview.draw())
            
            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                cv2.destroyAllWindows()
                break
            
        except KeyboardInterrupt:
            break
    
        print(time.process_time() - start_time)

def get_boundary(color_filter: list, image: np.ndarray) -> np.ndarray:
    
    # load the image, mask it, and convert to grayscale
    if (len(color_filter) == 3):
        filter_low = filter_high = np.array(color_filter)
    else:
        filter_low = np.array(color_filter[0])
        filter_high = np.array(color_filter[1])
        
    gray = cv2.inRange(image, filter_low, filter_high)
        
    # perform edge detection, then perform a dilation + erosion to
    # close gaps in between object edges
    edged = cv2.Canny(gray, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    # find contours in the edge map
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[0]

    boxes = []
    areas = []

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
        
        for box in boxes:
            
            width = box[1,0] - box[0,0]
            height = box[2,1] - box[1,1]
            
            area = float(width) * float(height)
            areas.append(area)
            
        largest_area = max(areas)
        
        return boxes[areas.index(largest_area)]
    else:
        return None

def get_recipe(name_box: tuple):
    
    image = np.array(ImageGrab.grab(bbox=name_box))
    
    ocr_result: str = pt.image_to_string(image).lower()
    ocr_result = ocr_result.replace('-', ' ')
    cleaned_result = ""
    
    for k in ocr_result.split("\n"):
        cleaned_result += " ".join(re.findall(r"[a-zA-Z]+", k))
    
    if ('pizza' in cleaned_result):
        return cleaned_result.replace("pizza", "")
    else:
        return None

def get_center(boundary: np.ndarray) -> tuple[int, int]:
    
    x = (boundary[0,0] + boundary[1,0] + boundary[2,0] + boundary[3,0]) / 4
    y = (boundary[0,1] + boundary[1,1] + boundary[2,1] + boundary[3,1]) / 4
            
    return int(x), int(y)

if __name__ == '__main__':
    
    main()