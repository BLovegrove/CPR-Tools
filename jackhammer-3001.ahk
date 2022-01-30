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
; as the pixel coords will match your screen coords

; distance to travel in a diamond pattern with your starting point being the southern point
; wouldn't recommend anything lower than 80 (default)
distance = 80

; delay (in seconds) after moving to make sure you're in the right position
; this should be higher the longer your distance is (1 default)
move_delay = 1

; delay (in seconds) after starting to dig before moving - 12 seems to be a good time
digging_delay = 12


; quit the script with esc
Esc::
MsgBox, "Bye-bye!"
ExitApp
return

; hitting shift + dance starts the sequence. moves counter-clockwise in a diamond pattern
; (starts south, then goes east, north, west and bac kto south before looping
+d::
Loop
{
    MouseClick, Left, distance, -distance, , 0, , R
    Sleep, move_delay * 1000
    SendInput, d
    Sleep, digging_delay * 1000

    MouseClick, Left, -distance, -distance, , 0, , R
    Sleep, move_delay * 1000
    SendInput, d
    Sleep, digging_delay * 1000

    MouseClick, Left, -distance, distance, , 0, , R
    Sleep, move_delay * 1000
    SendInput, d
    Sleep, digging_delay * 1000

    MouseClick, Left, distance, distance, , 0, , R
    Sleep, move_delay * 1000
    SendInput, d
    Sleep, digging_delay * 1000
}
return