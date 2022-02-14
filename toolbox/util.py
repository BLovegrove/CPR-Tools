import numpy as np
from PIL import ImageGrab
import cv2

from . import config

cfg = config.load_config()

def screenshot():
    
    return np.array(ImageGrab.grab(bbox=(0,0,1920,1080)))

def draw_mask(window_name: str, color_filter: list[int], screenshot_area: tuple):
    
    image = np.array(ImageGrab.grab(bbox=screenshot_area))
    
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

def get_toppings(recipe: str) -> list | bool:
    
    toppings = []
    
    for topping in cfg['toppings']:
        if topping == "sauces":
            continue
        
        if topping in recipe and topping not in toppings:
            toppings.append(topping)
            
    return toppings