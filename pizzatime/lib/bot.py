import time
import pyautogui as pgui

from . import mouse

def apply_topping(topping_pos: tuple[int,int], pizza_pos: tuple[int,int]):
    
    mouse.move(topping_pos[0], topping_pos[1])
    pgui.mouseDown()
    time.sleep(0.05)
    mouse.move(pizza_pos[0], pizza_pos[1], duration=0.1, steps_per_second=240)
    time.sleep(0.05)
    pgui.mouseUp()
    time.sleep(0.05)
    
    return