import cv2
from .lib import mouse

from .lib import config
from .lib import vision
from .lib import display

cfg = config.load_config()

# TODO: track pizza base inside color seperately to determine when to start sauce and when to end it

def debug_rectangles(rectangles, image):
    
    for item in rectangles:
        x,y,w,h = item[0], item[1], item[2], item[3]
        cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),3)
        
    display.imshow_wait('debug', image)
    

def main():
    
    # loading message with some basic stats about what config you're running
    print("Starting Pizzatron3001 bot with the following settings:")
    print(f"Resolution (WxH): {cfg['display']['width']} x {cfg['display']['height']} pixels")
    print(f"Offset (WxH): {cfg['display']['offset_x']} x {cfg['display']['offset_y']} pixels")
    print()
    
    # init the preview window
    cv2.namedWindow('output', cv2.WINDOW_NORMAL)
    
    # detects the boundaries of the game window
    print("Waiting for game window...")
    print("(Dont scroll your screen when this has finished)")
    while True:
        
        image = vision.screenshot()
        image_bin = vision.filter(image, cfg['colors']['game_window'])
        rectangles = vision.get_rect(image_bin, mode="contour")
        
        game_window = vision.smallest_rect(rectangles)
        
        if (game_window):
            print('Window found.')
            break
    
    # detects the boundaries of the pizza billboard for the OCR to use
    print("Waiting for pizza billboard...")
    while True:
        
        image = vision.screenshot()
        image_bin = vision.filter(image, cfg['colors']['billboard'])
        rectangles = vision.get_rect(image_bin, mode="contour")
        
        billboard = vision.largest_rect(rectangles)
        
        if (billboard):
            print('Billboard found.')
            break
    
    # checks for one sweet/savoury sauce and searches for the other based on the result
    print("Determining sauce locations...")
    sauce_boundary = (
        game_window[0], 
        billboard[1] + billboard[3], 
        game_window[2] - billboard[2], 
        game_window[3] - (billboard[1] + billboard[3])
    )
    while True:
        
        # check for sweet sauce first because sprinkles contain enough red to
        # trigger the savoury flag on sweet mode damnit.
        image = vision.filter(vision.screenshot(), cfg['colors']['pink_sauce'])
        sauce_alt = vision.get_rect(image, sauce_boundary)
        
        if (sauce_alt):
            print("Sauce type: Sweet.")
            sauce_boundary_alt = (
                sauce_boundary[0], 
                sauce_boundary[1], 
                sauce_alt[0] - game_window[0], 
                sauce_boundary[3]
            )
            image = vision.filter(vision.screenshot(), cfg['colors']['choc_sauce'])
            rectangles = vision.get_rect(image, sauce_boundary_alt, mode="contour")
            sauce_main = vision.largest_rect(rectangles)
            break
            
        else:
            image = vision.filter(vision.screenshot(), cfg['colors']['hot_sauce'])
            sauce_alt = vision.get_rect(image, sauce_boundary)
            
            if (sauce_alt):
                print("Sauce type: Savoury.")
                sauce_boundary_alt = (
                    sauce_boundary[0], 
                    sauce_boundary[1], 
                    sauce_alt[0] - game_window[0], 
                    sauce_boundary[3]
                )
                
                image = vision.filter(vision.screenshot(), cfg['colors']['pizza_sauce'])
                sauce_main = vision.get_rect(image, sauce_boundary_alt)
                break
            
            else:
                print("WHERE IS THE lAmB S A U C E!?")
        
    print("Calculating topping locations...")
    # just a few pixels above bottom of sauce bottles is perfect
    toppings_x = []
    toppings_y = sauce_main[1] + sauce_main[3] + 5
    
    # get the total width of the toppings area and break it into 5
    start = sauce_alt[0] + sauce_alt[2]
    end = game_window[0] + game_window[2]
    step = (end - start) / 5
    
    # make the first topping half of 1/5th from the end, and add
    # the new topping pos in left-to-right at 1-step intervals
    x = end - (step / 2)
    toppings_x.insert(0, int(x))
    for i in range(3):
        x = end - (step * len(toppings_x))
        toppings_x.insert(0, int(x))
    
    # cheese/sprinkle pos is just half way between the space thats left
    x = start + ((toppings_x[0] - start) / 2)
    toppings_x.insert(0, int(x))
        
    waiting_for_pizza = True
    
    while True:
        
        # loop while waiting for pizza to enter screen. pizza base (not crust)
        # will trigger the exit statement
        while waiting_for_pizza:
            image = vision.screenshot()
            image_bin = vision.filter(image, cfg['colors']['pizza_base'])
            pizza_base = vision.get_rect(image_bin, (0, sauce_main[1] + sauce_main[3], 0, 0))
            
            if pizza_base:
                # find the recipe using font color as a filter
                image_bin = vision.filter(image, cfg['colors']['text'])
                rectangles = vision.get_rect(image_bin, billboard, "contour")
                recipe_rect = vision.largest_rect(rectangles)
                
                # perform OCR on the recipe region
                recipe = vision.get_recipe(recipe_rect)
                topping_ids = vision.get_toppings(recipe)
                print(f"topping IDs: {topping_ids}")
                
                # exit the loop and disable the 'waiting' flag
                waiting_for_pizza = False
                break
        
        # check for both pizza crust and base. base can be used to check
        # if more sauce is needed. no base = sauce finished
        image = vision.screenshot()
        image_bin = vision.filter(image, cfg['colors']['pizza_crust'])
        pizza = vision.get_rect(image_bin, (0, sauce_main[1] + sauce_main[3], 0, 0))
        image_bin = vision.filter(image, cfg['colors']['pizza_base'])
        pizza_base = vision.get_rect(image_bin, (0, sauce_main[1] + sauce_main[3], 0, 0))
        
        # this should fire when the pizza clears the screen
        if not pizza:
            waiting_for_pizza = True
            continue
        
        # draw all the rectangles on the preview image
        for item in [sauce_alt, sauce_main, billboard, game_window, pizza, pizza_base, recipe_rect]:
            x,y,w,h = item[0], item[1], item[2], item[3]
            cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),3)
            
        for x in toppings_x:
            cv2.circle(image, (x, toppings_y), 10, (255,0,0), -1)
            
        cv2.imshow('output', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            cv2.destroyAllWindows()
            break

# test loop for fucking around with test code while still having access to everything
def test():
    
    event = mouse.record(button='right', target_types=('down',))
    print(event)
    
    # for i in range(100):
    #     mouse.move(100, 0, absolute=False, duration=0.1, steps_per_second=1000)
    #     mouse.move(-100, 0, absolute=False, duration=0.1, steps_per_second=1000)

if __name__ == '__main__':
    main()
    # test()