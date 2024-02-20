# VISCA-IP-Controller-GUI

Basic VISCA Controller


## How to use

In the controller.py file look for `camera = Camera(ip, port)` line of code.
Change the ip and port to what your camera is.
In the same file, look for  `joystick = Joystick(0, pygame)`. If you have more than one joystick connected, the integer `0` may need to be something else. Also, you may need to modify the `PAN_AXIS`, `TILT_AXIS`, , `ZOOM_AXIS` and `DEADZONE` values depending on your joystick.

Once that is done, simply run `python ./controller.py`. You will also need to install `pygame`. `python -m pip install pygame`.

# NOTES
This this still missing support for dynamic speeds, and I haven't tested this yet. Probably breaks...


This uses code from [VISCA-IP-Controller](https://github.com/misterhay/VISCA-IP-Controller).
