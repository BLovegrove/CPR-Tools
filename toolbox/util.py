import re
import time

import numpy as np
from PIL import ImageGrab
import cv2
import pytesseract as pt
import imutils
from imutils import perspective
import pyautogui as pgui

from toolbox.preview import PizzaPreview

from . import config

cfg = config.load_config()
pgui.PAUSE = 0

def screenshot(boundary: np.ndarray=None, scale=None):
    
    offset_x = left_x = cfg['display']['offset_x']
    offset_y = top_y = cfg['display']['offset_y']
    
    right_x = cfg['display']['width']
    bottom_y = cfg['display']['height']
    
    if (type(boundary) == np.ndarray):
        left_x = boundary[0, 0] + offset_x
        top_y = boundary[0, 1] + offset_y
        
        right_x = boundary[2, 0]
        bottom_y = boundary[2, 1]
        
    right_x += offset_x
    bottom_y += offset_y
        
    image = np.array(ImageGrab.grab(bbox=(left_x,top_y,right_x,bottom_y)))
        
    if (scale):
        width = int(image.shape[1] * scale)
        height = int(image.shape[0] * scale)
        dsize = (width, height)
        image = cv2.resize(image, dsize, interpolation=cv2.INTER_AREA)
    
    return image

def get_recipe(image: np.ndarray):
    
    # 0.71 is the percent width of the billboard that contains the recipe
    # Same with 0.24 for height. Format is left-to-righ\t, top-to-bottom
    recipe_w = int(image.shape[1] * 0.71)
    recipe_h = int(image.shape[0] * 0.24)
    
    # about 3% of the total width of the billboard is the width of the border
    border_offset = int(image.shape[1] * 0.03)
    
    # crop image to pizza recipe
    image = image[
        border_offset:recipe_h,
        border_offset:recipe_w
    ]
    
    cv2.imwrite('toolbox/debug/ocr.png', image)
    
    # scale image by 1.5x to help the OCR out a little. Skipping this causes frequent misses
    image = cv2.resize(image, (int(image.shape[1] * 1.5),int(image.shape[0] * 1.5)))
    
    ocr_result: str = pt.image_to_string(image).lower()
    ocr_result = ocr_result.replace("-", " ")
    ocr_result = ocr_result.replace("\n", " ")
    cleaned_result = ""
    
    for k in ocr_result.split("\n"):
        cleaned_result += " ".join(re.findall(r"[a-zA-Z]+", k))
    
    if ('pizza' in cleaned_result):
        return cleaned_result.replace("pizza", "")
    else:
        return None

def get_boundary(color_filter: list, image: np.ndarray, x_bound: int=0, y_bound: int=0) -> np.ndarray:

    # cut image to x and/or y boundaries for easier and cleaner processing
    if (x_bound > 0):
        image = image[0:image.shape[0], 0:x_bound]
    
    if (y_bound > 0):
        image = image[y_bound:image.shape[0], 0:image.shape[1]]
    
    
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
    contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[0]

    # compute the rotated bounding box of the largest contour
    try:
        largest_contour = max(contours, key=cv2.contourArea)
        
        if (cv2.contourArea(largest_contour) < 100):
            return None
        
        box = cv2.minAreaRect(largest_contour)
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        
        # add back the cut height to box y coords (if any)
        box[0,1] += y_bound
        box[1,1] += y_bound
        box[2,1] += y_bound
        box[3,1] += y_bound
        # cut x coords arent needed because we're only cutting after the bound not before
        
        # order the points in the contour such that they appear
        # in top-left, top-right, bottom-right, and bottom-left
        # order, then draw the outline of the rotated bounding
        # box
        box = perspective.order_points(box)
        
        return box
    except ValueError:
        return None

def get_center(boundary: np.ndarray) -> tuple[int, int]:
    
    x = (boundary[0,0] + boundary[1,0] + boundary[2,0] + boundary[3,0]) / 4
    y = (boundary[0,1] + boundary[1,1] + boundary[2,1] + boundary[3,1]) / 4
            
    return int(x), int(y)

def draw_mask(window_name: str, color_filter: list[int], image: np.ndarray):
    
    if (len(color_filter) == 3):
        filter_low = filter_high = np.array(color_filter)
    else:
        filter_low = np.array(color_filter[0])
        filter_high = np.array(color_filter[1])
    
    mask = cv2.inRange(image, filter_low, filter_high)  
    
    imshow_wait(f"{window_name} (mask)", mask)

def draw_boundary(image: np.ndarray, box: np.ndarray):
    
    # draw the contours on the image
    cv2.drawContours(image, [box.astype("int")], -1, (0, 255, 0), 5)

    # show the output image, resize it as per your requirements    
    return image

def draw_point(image: np.ndarray, coordinate: tuple):
    
    image = cv2.circle(image, center=coordinate, radius=9, color=(0,0,255), thickness=-1)
    
    return image
 
def imshow_wait(window_name: str, image: np.ndarray):
    
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    # image = cv2.resize(image, (1366,768))
    cv2.imshow(window_name, cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    while cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
        keyCode = cv2.waitKey(50) & 0xFF
        if keyCode == 27:
            cv2.destroyAllWindows()
            break
    
    cv2.waitKey(1)
    cv2.destroyAllWindows()

def get_topping_locations(window_boundary: np.ndarray):
    
    game_width = window_boundary[1][0] - window_boundary[0][0]
    
    # magic numbers are percentages of total pixel width of main game window.
    # .25 = space between x=0 and cheese/sprinkles for the game window
    offset_main = 0.25 * game_width
    # .46 = space between x=0 and first 'secondary ingredient'
    offset_toppings = 0.46 * game_width
    
    # .21 = width of the cheese/sprinkles area
    width_main = 0.21 * game_width
    # .54 = width of the 'secondary ingredient' total area. divide by 4 to get individual area size
    width_topping = (0.54 * game_width) / 4
    
    toppings = [0, 0, 0, 0]
    
    # add window_boundary[0][0] to go from relative positioning (ref: game window) to abs screen position
    # we do this because all other coords are done in abs screen position. Makes it easier to control inputs that way
    i = 0
    while i < len(toppings):
        toppings[i] = int(offset_toppings + (i * width_topping) + (width_topping  / 2) + window_boundary[0][0])
        i += 1
    
    main = int(offset_main + (width_main / 2)) + window_boundary[0][0]
    toppings.insert(0, main)
    
    return toppings

def get_toppings(recipe: str) -> list | bool:
    
    toppings = []
    
    for topping in cfg['toppings']:
        if topping == "sauces":
            continue
        
        if topping in recipe and topping not in toppings:
            topping_id = cfg['toppings'][topping]
            if (type(topping_id) != int):
                for id in topping_id:
                    toppings.append(id)
            else:
                toppings.append(topping_id)
                
    if (len(toppings) == 1):
        for i in range(4):
            toppings.append(toppings[0])
    elif (len(toppings) == 2):
        toppings.append(toppings[0])
        toppings.append(toppings[1])

    return toppings

# def pizza_progress()

def apply_sauce(pizza_preview: PizzaPreview, game_window_height: int, x_cutoff:int, sauce_alt: bool = False):
    
    conveyor_height = game_window_height * .35
    
    if (sauce_alt):
        sauce_pos = pizza_preview.get_sauce_pos()[1]
    else:
        sauce_pos = pizza_preview.get_sauce_pos()[0]
        
    pgui.moveTo(sauce_pos[0], sauce_pos[1])
    
    pgui.mouseDown()
    
    pgui.moveTo(pizza_preview.get_sauce_pos()[0][0], sauce_pos[1], 0.1)
    
    pizza_x = 0
    
    while (pizza_x < x_cutoff):
        
        try:
            y_bound = int(pizza_preview.get_sauce_bounds()[0][2,1])
            y_bound = y_bound + (conveyor_height * 0.5)
            pizza_pos = get_center(get_boundary(cfg['colors']['pizza_base'], screenshot(), y_bound=y_bound))
            pizza_x = pizza_pos[0]
            print(pizza_x)
        except TypeError:
            continue
    
        pgui.moveRel(0, conveyor_height, 0.2)
        pgui.moveRel(0, -conveyor_height, 0.2)
        
    pgui.mouseUp()
    
    return

def apply_topping(y_pos: int, x_pos: int, pizza_pos: tuple[int,int]):
    
    pgui.moveTo(x_pos, y_pos)
    pgui.mouseDown()
    pgui.moveTo(pizza_pos[0], pizza_pos[1], 0.2)
    time.sleep(0.05)
    pgui.mouseUp()
    
    return