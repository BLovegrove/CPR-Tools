import cv2
import numpy as np
from PIL import ImageGrab
import pytesseract as pt
import re

from toolbox.util import imshow_wait

from . import config

cfg = config.load_config()

def screenshot(crop: tuple=None, scale: float=None):
    
    # grab screen res / offset values from config file.
    # offsets used for pickign which screen the game is on
    image = np.array(
        ImageGrab.grab(
            bbox=(
                cfg['display']['offset_x'],
                cfg['display']['offset_y'],
                cfg['display']['width'],
                cfg['display']['height']
            )
        )
    )
    
    if crop:
        x, y, w, h = crop
            
        image = image[y:y+h, x:x+w]
        
    if scale:
        width = int(image.shape[1] * scale)
        height = int(image.shape[0] * scale)
        dsize = (width, height)
        image = cv2.resize(image, dsize, interpolation=cv2.INTER_AREA)
    
    return image

def filter(image: np.ndarray, color_filter: list):
    
    # load the color filters, mask the image, and convert to grayscale
    if (len(color_filter) == 3):
        filter_low = filter_high = np.array(color_filter)
    else:
        filter_low = np.array(color_filter[0])
        filter_high = np.array(color_filter[1])
    
    # filter the color out to create binary image    
    image = cv2.inRange(image, filter_low, filter_high)
    
    # dilate the image to close any gaps and remove noise
    kernel = np.ones((10,10), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    
    # exclude everything but edges in the image
    image = cv2.Canny(image, 10, 20)
    
    # dilate edges again to close gaps and clear any noise that made it through
    kernel = np.ones((5,5), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    
    return image

def get_rect(image: np.ndarray, crop: tuple=(0,0,0,0), mode: str="bounding"):
    
    x, y, w, h = crop
    
    w = crop[2] if crop[2] > 0 else image.shape[1]
    h = crop[3] if crop[3] > 0 else image.shape[0]
        
    image = image[y:y+h, x:x+w]
    
    match mode:
        
        case "bounding":
            # return rect for all 1's in binary image
            
            rect = cv2.boundingRect(image)
            rect = (rect[0] + x, rect[1] + y, rect[2], rect[3])
            
            return rect
        
        case "contour":
            # return all rectangles in image using contour detection
            
            contours = cv2.findContours(
                image, 
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )[0]
            
            try:
                rectangles = []
                
                for contour in contours:
                    if cv2.contourArea(contour) > 100:
                        rect = cv2.boundingRect(contour)        
                        rect = (rect[0] + x, rect[1] + y, rect[2], rect[3])
                        
                        rectangles.append(rect)
            
                return rectangles
                        
            except ValueError:
                return []
            
def largest_rect(rectangles: list[tuple]) -> tuple:
    
    largest_area = 0
    largest = None
    
    for rect in rectangles:
        area = rect[2] * rect[3]
        if area > largest_area:
            largest = rect
            largest_area = area
            
    return largest

def smallest_rect(rectangles: list[tuple]) -> tuple:
    
    smallest_area = rectangles[0][2] * rectangles[0][3]
    smallest = rectangles[0]
    
    for rect in rectangles:
        area = rect[2] * rect[3]
        if area < smallest_area:
            smallest = rect
            smallest_area = area
            
    return smallest

def get_recipe(recipe_rect: tuple):
    
    image = screenshot(recipe_rect, 1.5)
    
    ocr_result = pt.image_to_string(image).lower()
    ocr_result = ocr_result.replace("-", " ")
    ocr_result = ocr_result.replace("\n", " ")
    cleaned_result = ""
    
    for k in ocr_result.split("\n"):
        cleaned_result += " ".join(re.findall(r"[a-zA-Z]+", k))
    
    if ('pizza' in cleaned_result):
        return cleaned_result.replace("pizza", "")
    else:
        return None
    
def get_toppings(recipe: str) -> list:
    
    toppings = []
    
    for topping in cfg['topping_ids']:
        if topping == "sauces":
            continue
        
        if topping in recipe and topping not in toppings:
            topping_id = cfg['topping_ids'][topping]
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