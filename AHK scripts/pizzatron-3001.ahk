; basic config stuff. you can ignore this
#NoEnv
#SingleInstance, Force
SendMode Input
SetWorkingDir, %A_ScriptDir%

; All this data is based on a 1920x1080 monitor while the browser window is maximised
; and scrolled to the top. Results with different setups may vary.

; To change these variables and match the relevant points on your own monitor,
; take a fullscreen snip while the game is running and open the image in Gimp
; (or similar image editing software) then use the cursor to find your coords 
; as the pixel coords will match your screen coords.

topping_x1 = 985
topping_x2 = 1160
topping_x3 = 1330
topping_x4 = 1500

toppings_y = 550

; quit the script with esc
Esc::
MsgBox, "Bye-bye!"
ExitApp
return

; #1 handles seaweed/liqurice 
1::
BlockInput, MouseMove
MouseGetPos, currentX, currentY
MouseClickDrag, Left, topping_x1, toppings_y, currentX, currentY, 0
BlockInput, MouseMoveOff
return

; #2 handles shrimp/chocolate
2::
BlockInput, MouseMove
MouseGetPos, currentX, currentY
MouseClickDrag, Left, topping_x2, toppings_y, currentX, currentY, 0
BlockInput, MouseMoveOff
return

; #3 handles squid/marshmellow
3::
BlockInput, MouseMove
MouseGetPos, currentX, currentY
MouseClickDrag, Left, topping_x3, toppings_y, currentX, currentY, 0
BlockInput, MouseMoveOff
return

; #4 handles fish/jellybean
4::
BlockInput, MouseMove
MouseGetPos, currentX, currentY
MouseClickDrag, Left, topping_x4, toppings_y, currentX, currentY, 0
BlockInput, MouseMoveOff
return