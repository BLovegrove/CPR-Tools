import cv2
import numpy as np

def imshow_wait(window_name: str, image: np.ndarray):
    
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    try:
        cv2.imshow(window_name, cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    except cv2.error:
        cv2.imshow(window_name, image)
    
    while cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
        keyCode = cv2.waitKey(50) & 0xFF
        if keyCode == 27:
            cv2.destroyAllWindows()
            break
    
    cv2.waitKey(1)
    cv2.destroyAllWindows()