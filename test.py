import pyautogui as pgui
pgui.PAUSE = 0

def apply_sauce():
    
    sauce_pos = (365, 548)
    pizza_pos = (968, 638)
        
    pgui.moveTo(sauce_pos[0], sauce_pos[1])
    
    # pgui.mouseDown()
    print("mouse down")
    
    pgui.moveTo(pizza_pos[0], pizza_pos[1])
    
    speed = 0.11
    drift = 50
    for i in range(3):
        pgui.moveTo(pizza_pos[0] - (i * drift), pizza_pos[1] + 230, speed)
        pgui.moveTo(pizza_pos[0] - (i * drift), pizza_pos[1], speed)
    
    # pgui.mouseUp()
    print("mouse up")
    
    return

apply_sauce()