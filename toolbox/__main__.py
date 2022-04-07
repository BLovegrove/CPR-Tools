import time
import cv2
from cv2 import imshow
import numpy as np

from . import config
from . import util
from . preview import PizzaPreview

cfg = config.load_config()
preview = PizzaPreview()
DEBUGGING = False
PREVIEW = False
AUTOMATIC = True

def main():
    
    print("Starting Pizzatron3001 bot with the following settings:")
    print(f"Resolution (WxH): {cfg['display']['width']} x {cfg['display']['height']} pixels")
    print(f"Offset (WxH): {cfg['display']['offset_x']} x {cfg['display']['offset_y']} pixels")
    print(f"OCR read delay: {cfg['ocr']['seconds_before_read']} seconds")
    print()
    
    if (PREVIEW):
        cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
        
    game_window = None
    
    print("Waiting for game window...")
    print("(Dont scroll your screen when this has finished)")
    while True:
        image = util.screenshot()
        if (PREVIEW):
            imshow('Output', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            cv2.destroyAllWindows()
            break
        
        game_window = util.get_boundary(cfg['colors']['game_window'], image)
        if (type(game_window) == np.ndarray):
            print('Window found.')
            break
            
    print("Waiting for pizza billboard...")
    while True:
        image = util.screenshot()
        if (PREVIEW):
            imshow('Output', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            cv2.destroyAllWindows()
            break
        
        board = util.get_boundary(cfg['colors']['billboard'], image)
        if (type(board) == np.ndarray):
            print('Billboard found.')
            preview.set_billboard(board)
            break
    
    print("Determining Pizzatron sweet/savoury mode...")
    while True:
        sauce_found = False
        image = util.screenshot()
        if (PREVIEW):
            imshow('Output', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                cv2.destroyAllWindows()
                break
        
        sauce_alt_bound = util.get_boundary(cfg['colors']['hot_sauce'], image, y_bound=int(board[2,1]))
        if (type(sauce_alt_bound) == np.ndarray):
            print("Sauce type: Savoury.")
            sauce_main_bound = util.get_boundary(cfg['colors']['pizza_sauce'], image, x_bound=int(sauce_alt_bound[0,0]))
            sauce_found = True
            
        else:
            sauce_main_bound = util.get_boundary(cfg['colors']['choc_sauce'], image, y_bound=int(board[2,1]))
            if (type(sauce_main_bound) == np.ndarray):
                print("Sauce type: Sweet.")
                sauce_alt_bound = util.get_boundary(cfg['colors']['pink_sauce'], image, y_bound=int(board[2,1]))
                sauce_found = True
            else:
                print("WHERE IS THE lAmB S A U C E!?")
        
        if (sauce_found):
            sauce_main_x, sauce_main_y = util.get_center(sauce_main_bound)
            sauce_alt_x, sauce_alt_y = util.get_center(sauce_alt_bound)
            
            preview.set_sauce_bounds(sauce_main_bound, sauce_alt_bound)
            preview.set_sauce_pos((sauce_main_x, sauce_main_y), (sauce_alt_x, sauce_alt_y))
            
            break
        
    print("Determining topping locations...")
    toppings_pos_x = util.get_topping_locations(game_window)
    topping_pos_y = sauce_main_bound[2,1] - 10
    print(f"Calculated X pos: Main={toppings_pos_x[0]} 1={toppings_pos_x[1]} 2={toppings_pos_x[2]} 3={toppings_pos_x[3]} 4={toppings_pos_x[4]}")
    print(f"Calculated Y pos: {topping_pos_y}")
    print()
        
    pizza_visible_last = False
    pizza_visible = False
    
    pizza_x = pizza_y = 0
    
    while True:
        start_time = time.process_time()
        
        image = util.screenshot()
        preview.set_image(image)
            
        # use boundary detection to track current x,y of pizzas center
        pizza_bound = util.get_boundary(cfg['colors']['pizza_base'], image, y_bound=int(sauce_alt_bound[2,1]))
        if (type(pizza_bound) == np.ndarray):
            pizza_x, pizza_y = util.get_center(pizza_bound)
            preview.set_pizza_bound(pizza_bound)
            preview.set_pizza_pos((pizza_x, pizza_y))
            
            pizza_visible = True
        else:
            pizza_visible = False
        
        # only fire OCR when the pizza first peaks onto the conveyor to prevent weird recipe reads
        if (pizza_visible != pizza_visible_last):
            
            ocr_image = util.screenshot(board)
            
            # fetch recipe via OCR
            recipe = util.get_recipe(ocr_image)
            if (recipe):
                print(f"Found recipe: {recipe}")
                recipe_code = util.get_toppings(recipe)
                print(recipe_code)
                
                if (recipe.split()[0] in cfg['toppings']['sauces']):
                    sauce_alt = True
                else:
                    sauce_alt = False
                
                # super handy flag for debugging. turn it off to take amnual control
                if (AUTOMATIC):
                    game_window_height = game_window[2][1] - game_window[1][1]
                    util.apply_sauce(preview, game_window_height, toppings_pos_x[0], sauce_alt)
                    
                    # small sleep timers prevents game from failing to register clicks / movements
                    time.sleep(0.1)
                    pizza_bound = util.get_boundary(
                        cfg['colors']['pizza_base'], 
                        util.screenshot(), 
                        y_bound=int(sauce_alt_bound[2,1])
                    )
                    pizza_x, pizza_y = util.get_center(pizza_bound)
                    pizza_x = pizza_bound[1,0] - ((pizza_bound[1,0] - pizza_bound[0,0]) * 0.1)
                    # always apply cheese/sprinkles followed by whatever topping IDs are in the recipe code
                    util.apply_topping(topping_pos_y, toppings_pos_x[0], (pizza_x, pizza_y))
                    for topping_id in recipe_code:
                        time.sleep(0.1)
                        pizza_bound = util.get_boundary(
                            cfg['colors']['pizza_base'], 
                            util.screenshot(), 
                            y_bound=int(sauce_alt_bound[2,1])
                        )
                        pizza_x, pizza_y = util.get_center(pizza_bound)
                        pizza_x = pizza_bound[1,0] - ((pizza_bound[1,0] - pizza_bound[0,0]) * 0.1)
                        util.apply_topping(topping_pos_y, toppings_pos_x[topping_id], (pizza_x, pizza_y))
                        print(f"pizza: {pizza_x},{pizza_y}")
                
            else:
                if (DEBUGGING):
                    print("Failed to find pizza recipe!")
                pass
        
        pizza_visible_last = pizza_visible
        
        if (PREVIEW):
            cv2.imshow('Output', preview.draw())
        
        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            cv2.destroyAllWindows()
            break
    
        if (DEBUGGING):
            print(time.process_time() - start_time)

if __name__ == '__main__':
    try:
        # Thread(target=main).start()
        main()
    except KeyboardInterrupt:
        exit()