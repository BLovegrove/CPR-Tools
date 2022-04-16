import time
import pyautogui as pgui

from . import mouse
from . import config

cfg = config.load_config()

def apply_topping(topping_pos: tuple[int,int], pizza_pos: tuple[int,int]):
    
    # adjust for screen offset before adding toppings
    offset_x = cfg['display']['offset_x']
    offset_y = cfg['display']['offset_y']
    
    topping_pos = (
        topping_pos[0] + offset_x,
        topping_pos[1] + offset_y
    )
    
    pizza_pos = (
        pizza_pos[0] + offset_x,
        pizza_pos[1] + offset_y
    )
    
    pgui.moveTo(topping_pos[0], topping_pos[1])
    pgui.mouseDown()
    mouse.move(pizza_pos[0], pizza_pos[1], duration=0.03, steps_per_second=240)
    time.sleep(0.01)
    pgui.mouseUp()
    
    return