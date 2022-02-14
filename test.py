import numpy as np
import cv2
from mss import mss
from PIL import ImageGrab
import time
import os
import imutils
from imutils import perspective

bounding_box = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}

sct = mss()

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
    
def get_center_of(color_filter: list, image: np.ndarray) -> tuple[int, int]:
    
    # snap image
    coords = get_boundary(color_filter, image)
    
    if (type(coords) == np.ndarray):
        x = (coords[0,0] + coords[1,0] + coords[2,0] + coords[3,0]) / 4
        y = (coords[0,1] + coords[1,1] + coords[2,1] + coords[3,1]) / 4
                
        return int(x), int(y)
    
    else:
        return None, None


def draw_point(image: np.ndarray, coordinate: tuple):
    
    image = cv2.circle(image, center=coordinate, radius=9, color=(0,0,255), thickness=-1)
    
    return image

def draw_boundary(image: np.ndarray, box: np.ndarray):
    
    # draw the contours on the image
    cv2.drawContours(image, [box.astype("int")], -1, (0, 255, 0), 5)

    # show the output image, resize it as per your requirements    
    return image
    
while True:
    start = time.process_time()
    image = np.array(ImageGrab.grab(bbox=(cfg['display']['offset_x'],cfg['display']['offset_y'],cfg['display']['width'],cfg['display']['height'])))
    
    # pizza_loc = get_boundary([[119,69,0], [199,134,0]], image)
    # if (type(pizza_loc) == np.ndarray):
    #     image = draw_boundary(image, pizza_loc)
    
    pizza_loc = get_center_of([[119,69,0], [199,134,0]], image)
    if (pizza_loc):
        image = draw_point(image, pizza_loc)
    
    cv2.namedWindow('screen', cv2.WINDOW_NORMAL)
    cv2.imshow('screen', image)
    
    print(time.process_time() - start)

    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        cv2.destroyAllWindows()
        break