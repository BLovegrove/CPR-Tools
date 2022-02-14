from types import NoneType
import cv2
from cv2 import imshow

class PizzaPreview:
    def __init__(self):
        self.image = None
        self.image_post = None
        
        self.billboard_boundary = None
        
        self.sauce_main_boundary = None
        self.sauce_main_position = None
        self.sauce_alt_boundary = None
        self.sauce_alt_position = None
        
        self.pizza_boundary = None
        self.pizza_position = None
    
    
    def update_overlay(self):
        
        # copy clean image
        image = self.image
        if (type(image) == NoneType):
            return
        
        # draw billboard position
        try:
            image = cv2.drawContours(image, [self.billboard_boundary.astype("int")], -1, (0, 255, 0), 5)
        except AttributeError:
            pass
        
        # draw sauce boundaries
        try:
            image = cv2.drawContours(image, [self.sauce_main_boundary.astype("int")], -1, (0, 255, 0), 5)
            image = cv2.drawContours(image, [self.sauce_alt_boundary.astype("int")], -1, (0, 255, 0), 5)
            # draw sauce center points
            image = cv2.circle(image, center=self.sauce_main_position, radius=9, color=(0,0,255), thickness=-1)
            image = cv2.circle(image, center=self.sauce_alt_position, radius=9, color=(0,0,255), thickness=-1)
        except AttributeError:
            pass
        
        # draw pizza boundary / center point
        try:
            image = cv2.drawContours(image, [self.pizza_boundary.astype("int")], -1, (0, 255, 0), 5)
            image = cv2.circle(image, center=self.pizza_position, radius=9, color=(0,0,255), thickness=-1)
        except AttributeError:
            pass
        
        # update post-process image
        self.image_post = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return    

    def draw(self):
        self.update_overlay()
        return self.image_post

    def update_image(self, image):
        self.image = image
        self.image_post = image
        return
    
    def update_billboard(self, billboard_bound):
        self.billboard_boundary = billboard_bound
        return
    
    def update_sauce_pos(self, sauce_main_pos, sauce_alt_pos):
        self.sauce_main_position = sauce_main_pos
        self.sauce_alt_position = sauce_alt_pos
        return
    
    def update_sauce_bounds(self, sauce_main_bound, sauce_alt_bound):
        self.sauce_main_boundary = sauce_main_bound
        self.sauce_alt_boundary = sauce_alt_bound
        return
        
    def update_pizza_pos(self, pizza_pos):
        self.pizza_position = pizza_pos
        return
    
    def update_pizza_bound(self, pizza_bound):
        self.pizza_boundary = pizza_bound
        return
        