import numpy as np
import cv2

from . import config

cfg = config.load_config()

def show_box_contour_data (window_name: str, image: np.ndarray, box: list):
    
    # draw the contours on the image
    cv2.drawContours(image, [box.astype("int")], -1, (0, 255, 0), 5)

    # loop over the original points
    for (xA, yA) in list(box):
        # draw circles corresponding to the current points and
        cv2.circle(image, (int(xA), int(yA)), 9, (0,0,255), -1)
        cv2.putText(image, "({},{})".format(xA, yA), (int(xA - 50), int(yA - 10) + 20),
            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,0,0), 5)

    # show the output image, resize it as per your requirements    
    imshow_wait(window_name, image)
        
def imshow_wait(window_name: str, image: np.ndarray):
    
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    image = cv2.resize(image, (1366,768))
    cv2.imshow(window_name, cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    while cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
        keyCode = cv2.waitKey(50) & 0xFF
        if keyCode == 27:
            cv2.destroyAllWindows()
            break
    
    cv2.waitKey(1)
    cv2.destroyAllWindows()

def topping_breakdown(pizza_name: str) -> list | bool:
    
    alt_sauce = False
    toppings = []
    
    for item in cfg['toppings']['sauce']:
        if item in pizza_name:
            alt_sauce = True
    
    for topping in cfg['toppings']:
        if topping == "sauces":
            continue
        
        if topping in pizza_name and topping not in toppings:
            toppings.append(topping)
            
    return toppings, alt_sauce


# def add_topping(game_window_box: np.ndarray, toppings: list, alt_sauce: bool=False):
    
#     if (len(toppings) == 4):
#         topping_qty = 1
#     elif (len(toppings) == 2):
#         topping_qty = 2
#     elif (len(toppings) == 1):
#         topping_qty = 5
#     else:
#         topping_qty = 0
        
    