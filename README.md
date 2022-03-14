# Joystick to DVIP

## Introduction

VISCA generally runs over serial, but some cameras/gimbles support VISCA-over-IP.
Because DataVideo thinks they are special, they have DVIP which is the same as 
VISCA-over-IP, but with two additional headers.

## What this code does

Allows the user to control a DVIP camera with a 4 axis joystick.
If you only have a 3 axis joystick, you'll need to remove 
```
axis3: float = joystick.get_axis(3)
```
with
```
axis3: float = 1
```
This axis controls the sensitivity of the pan and tilt. So choose any number between -1 and 1.

## Configuring and Running

Open `joystick.py` and set the gimble/camera ip and port. Plug in a joystick into the computer
where this code will run. Then in terminal or cmd run 
```
Linux: python3 joystick.py
MacOS: python joystick.py
Windows: python.exe joystick.py
```
And it should magically work.

## Future additions

VISCA over IP : There are plenty of VISCA over IP repos, so it is not vital, but would be an easy addition to make this code work with just VISCA as well.

Joystick to VISCA : DVIP is slow, especially since socket.io does not support QOS. Might as well make the code work with serial as well.

Add QOS: Would have to work with socket.io to make this happen.