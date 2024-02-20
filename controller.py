import pygame
import socket
from time import sleep

# PT STOP COMMAND: 81 01 06 01 01 01 03 03 FF
# ZOOM STOP COMMAND: 81 01 04 07 00 FF


class Camera:
    PAN_SPEED = 1
    TILT_SPEED = 2
    PAN_DIRECTION = 3
    TILT_DIRECTION = 4

    _zoom_stop = "81 01 04 07 00 FF"
    _pt_stop = "81 01 06 01 01 01 03 03 FF"
    _pan_bytes = ""
    _pt_bytes_previous = ""
    _zoom_bytes_previous = ""
    _pan_speed = "01"
    _tilt_speed = "00"
    _pan_direction = "00"
    _tilt_direction = "00"
    # 30 => {zoom_direction}{zoom_speed}
    _z_command = ["81 01 04 07", "30", "FF"]
    _pt_command = [
        "81 01 06 01",
        _pan_speed,
        _tilt_speed,
        _pan_direction,
        _tilt_direction,
        "FF",
    ]

    def __init__(self, ip, port) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def pan_speed(self, speed):
        scale = -0.5
        self._pt_command[
            Camera.PAN_SPEED
        ] = "04"  # str(hex(round(24*(abs(speed)**((2 + scale))))))[2:].zfill(2).upper()
        if self._pt_command[Camera.PAN_SPEED] == "00":
            self._pt_command[Camera.PAN_DIRECTION] = "03"

    def tilt_speed(self, speed):
        scale = -0.5
        self._pt_command[
            Camera.TILT_SPEED
        ] = "04"  # str(hex(round(20*(abs(speed)**((2 + scale))))))[2:].zfill(2).upper()
        if self._pt_command[Camera.TILT_SPEED] == "00":
            self._pt_command[Camera.TILT_DIRECTION] = "03"

    def zoom_speed(self, speed):
        speed = "4"  # round(2*abs(speed)**1)  # Only goes up to 7, so doesn't need hex conversion
        self._z_command[1] = self._z_command[1][0] + str(speed)
        if speed == "0":
            self.zoom_in()

    def stop(self):
        stop = "00 0B 81 01 06 01 04 00 03 03 FF"
        self.socket.send(bytearray.fromhex(stop))

    def left(self, speed=None):
        self._pt_command[Camera.PAN_DIRECTION] = "01"
        if speed:
            self.pan_speed(speed)

    def right(self, speed=None):
        self._pt_command[Camera.PAN_DIRECTION] = "02"
        if speed:
            self.pan_speed(speed)

    def up(self, speed=None):
        self._pt_command[Camera.TILT_DIRECTION] = "01"
        if speed:
            self.tilt_speed(speed)

    def down(self, speed=None):
        self._pt_command[Camera.TILT_DIRECTION] = "02"
        if speed:
            self.tilt_speed(speed)

    def zoom_in(self, speed=None):
        self._z_command[1] = "2" + self._z_command[1][1]
        if speed:
            self.zoom_speed(speed)

    def zoom_out(self, speed=None):
        self._z_command[1] = "3" + self._z_command[1][1]
        if speed:
            self.zoom_speed(speed)

    def send(self, pt_stop=False, zoom_stop=False):
        # payload_type = '00'
        # pt_payload_length = "0B"  # str(hex(11))[2:].zfill(2)
        pt_command = ["00", "0B"]
        pt_command.extend(self._pt_command)
        pt_command = Camera._pt_stop if pt_stop else pt_command
        pt_bytes = bytearray.fromhex(" ".join(pt_command))
        if pt_bytes != self._pt_bytes_previous:
            self.socket.send(pt_bytes)
            self._pt_bytes_previous = pt_bytes
        zoom_command = ["00", "08"]
        zoom_command.extend(self._z_command)
        zoom_command = Camera._zoom_stop if zoom_stop else zoom_command
        zoom_bytes = bytearray.fromhex(" ".join(zoom_command))
        if zoom_bytes != self._zoom_bytes_previous:
            print("zoom_bytes", zoom_bytes)
            self._zoom_bytes_previous = zoom_bytes
            #  a = "00 08 81 01 04 07 37 FF"
            self.socket.send(zoom_bytes)


class Joystick:
    PAN_AXIS = 0
    TILT_AXIS = 1
    ZOOM_AXIS = 2
    DEADZONE = 0.004

    def __init__(self, id, pygame):
        self.joystick = pygame.joystick.Joystick(id)
        self.joystick.init()

    def left(self):
        return self.joystick.get_axis(Joystick.PAN_AXIS) < -Joystick.DEADZONE

    def right(self):
        return self.joystick.get_axis(Joystick.PAN_AXIS) > Joystick.DEADZONE

    def up(self):
        return self.joystick.get_axis(Joystick.TILT_AXIS) < -Joystick.DEADZONE

    def down(self):
        return self.joystick.get_axis(Joystick.TILT_AXIS) > Joystick.DEADZONE

    def zoom_in(self):
        return self.joystick.get_axis(Joystick.ZOOM_AXIS) < - Joystick.DEADZONE

    def zoom_out(self):
        return self.joystick.get_axis(Joystick.ZOOM_AXIS) > Joystick.DEADZONE

    def speed(self, axis):
        speed = abs(self.joystick.get_axis(axis)) - Joystick.DEADZONE
        return speed if speed > 0 else 0

    def pan_speed(self):
        speed = abs(self.joystick.get_axis(Joystick.PAN_AXIS)) - Joystick.DEADZONE
        return speed if speed > 0 else 0

    def tilt_speed(self):
        speed = abs(self.joystick.get_axis(Joystick.TILT_AXIS)) - Joystick.DEADZONE
        return speed if speed > 0 else 0

    def zoom_speed(self):
        speed = abs(self.joystick.get_axis(Joystick.ZOOM_AXIS)) - Joystick.DEADZONE
        return speed if speed > 0 else 0

    def pt_stop(self):
        return not (self.tilt_speed() or self.pan_speed())

    def zoom_stop(self):
        return not self.zoom_speed()

    def print_all(self):
        # Usefull for debugging
        print(
            "left: ",
            joystick.left(),
            "right:",
            joystick.right(),
            "up:",
            joystick.up(),
            "down:",
            joystick.down(),
            "in:",
            joystick.zoom_in(),
            "out:",
            joystick.zoom_out(),
        )


camera = Camera('192.168.250.52', 5002)
pygame.init()
pygame.joystick.init()
joystick = Joystick(0, pygame)
while not sleep(0.3):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break
    if joystick.left():
        camera.left(joystick.pan_speed())
    if joystick.right():
        camera.right(joystick.pan_speed())
    if joystick.up():
        camera.up(joystick.tilt_speed())
    if joystick.down():
        camera.down(joystick.tilt_speed())
    if joystick.zoom_in():
        camera.zoom_in(joystick.zoom_speed())
    if joystick.zoom_out():
        camera.zoom_out(joystick.zoom_speed())
    camera.send(joystick.pt_stop(), joystick.zoom_stop())
pygame.quit()
