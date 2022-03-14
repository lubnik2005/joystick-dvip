import pygame
import socket
from time import sleep
from TextPrint import _TextPrint
import dvip

# Variable
CAMERA_IP: str = '192.168.250.52'
CAMERA_PORT: str = 5002
SEND_PACKETS: bool = True
SHOW_GUI: bool = False
CLOCK_FPS: int = 20

# Defaults

if SEND_PACKETS:
    # Connect to Camera
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4, TCP
    s.connect((CAMERA_IP, CAMERA_PORT))

pygame.init()
pygame.joystick.init()  # Initialize the joysticks.

if SHOW_GUI:  # Initialize GUI
    # Define some colors.
    WHITE = pygame.Color('white')
    # Set the width and height of the screen (width, height).
    screen = pygame.display.set_mode((800, 200))
    pygame.display.set_caption("PTZ Joystick Controller")
    # Loop until the user clicks the close button.
    # Used to manage how fast the screen updates.
    clock = pygame.time.Clock()
    # Get ready to print.
    textPrint = _TextPrint()

pt_previous = None
z_previous = None
# -------- Main Program Loop -----------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break

    if SHOW_GUI:
        screen.fill(WHITE)
        textPrint.reset()

    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for joystick in joysticks:
        joystick.init()
        pan: float = joystick.get_axis(0)
        tilt: float = joystick.get_axis(1)
        zoom: float = joystick.get_axis(2)
        axis3: float = joystick.get_axis(3)
        tilt_speed: str = str(hex(round(20*(abs(tilt)**((2 + axis3))))))[2:].zfill(2).upper()
        pan_speed: str = str(hex(round(24*(abs(pan)**((2 + axis3))))))[2:].zfill(2).upper()
        zoom_speed: str = str(round(7*abs(zoom)**1.7))

        pan_direction_str: str = None
        pan_direction: str = '3'
        if pan > 0:
            pan_direction_str = 'Right'
            pan_direction = '2'
        elif pan < 0:
            pan_direction_str = 'Left'
            pan_direction = '1'
        if pan_speed == '00':
            pan_direction_str = 'Stopped'
            pan_direction = '3'
            pan_speed = '01'

        tilt_direction_str: str = None
        tilt_direction: str = '3'
        if tilt > 0:
            tilt_direction_str = 'Down'
            tilt_direction = '2'
        elif tilt < 0:
            tilt_direction_str = 'Up'
            tilt_direction = '1'
        if tilt_speed == '00':
            tilt_direction_str = 'Stopped'
            tilt_direction = '3'
            tilt_speed = '01'

        pt_command = f"81 01 06 01 {pan_speed} {tilt_speed} 0{pan_direction} 0{tilt_direction} FF"
        pt_message = f"{dvip.PAYLOAD_TYPE} {dvip.PAN_TILT_PAYLOAD_LENGTH} {pt_command}"
        pt_bytes = bytearray.fromhex(pt_message)

        zoom_direction_str: str = None
        zoom_direction: str = '0'
        if zoom > 0:
            zoom_direction_str = 'In'
            zoom_direction = '2'
        elif zoom < 0:
            zoom_direction_str = 'Out'
            zoom_direction = '3'
        if zoom_speed == '0':
            zoom_direction_str = 'Stopped'
            zoom_direction = '0'
        z_command = f"81 01 04 07 {zoom_direction}{zoom_speed} FF"
        z_message = f"{dvip.PAYLOAD_TYPE} {dvip.ZOOM_PAYLOAD_LENGTH} {z_command}"
        z_bytes = bytearray.fromhex(z_message)

        if SHOW_GUI:
            textPrint.tprint(screen, "Joystick")
            textPrint.indent()
            textPrint.tprint(screen, f"Tilting {tilt_direction_str} at Speed {tilt_speed}")
            textPrint.tprint(screen, f"Moving {pan_direction_str} at Speed {pan_speed}")
            textPrint.tprint(screen, f"Zooming {zoom_direction_str} at Speed {zoom_speed}")
            textPrint.tprint(screen, f"Pan-Tilt Command sent {pt_command}")
            textPrint.tprint(screen, f"Zoom Command sent {z_command}")
            textPrint.tprint(screen, f"Zoom Command sent {z_command}")

        if SEND_PACKETS:
            if pt_bytes != pt_previous:
                pt_previous = pt_bytes
                s.send(pt_bytes)
            if z_bytes != z_previous:
                z_previous = z_bytes
                s.send(z_bytes)

            if pt_command == dvip.PAN_TILT_STOP_COMMAND:
                s.send(pt_bytes)
            if z_bytes == dvip.ZOOM_STOP_COMMAND:
                s.send(z_bytes)

    if SHOW_GUI:
        pygame.display.flip()
        clock.tick(CLOCK_FPS)
    else:
        sleep(1/CLOCK_FPS)
pygame.quit()
