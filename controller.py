import pygame
import socket
import binascii # for printing the messages we send, not really necessary
from time import sleep


run_connection: bool = True
gui: bool = False

# Conect to Camera
if run_connection:
    camera_ip = '192.168.250.52'
    camera_port = 5002
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4, TCP
    s.connect((camera_ip, camera_port))
    print("Connected")

# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')

# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


pygame.init()
done = False

if gui:
    # Set the width and height of the screen (width, height).
    screen = pygame.display.set_mode((800, 200))
    pygame.display.set_caption("PTZ Jank")
    # Loop until the user clicks the close button.
    # Used to manage how fast the screen updates.
    clock = pygame.time.Clock()
    # Get ready to print.
    textPrint = TextPrint()
# Initialize the joysticks.
pygame.joystick.init()


pt_previous = None
z_previous = None
# -------- Main Program Loop -----------
while not done:

    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.
        elif event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        elif event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")

    if gui:
        screen.fill(WHITE)
        textPrint.reset()
    # Get count of joysticks.
    joystick_count = pygame.joystick.get_count()

    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        but4: bool = joystick.get_button(3)
        buttons_to_exclude = [4, 5, 9, 10]
        BUTTONS = []
        for i in range(1,17):
            if i not in buttons_to_exclude:
                BUTTONS.append({'value': joystick.get_button(i - 1), 'preset': f'{i}'.zfill(2), 'command': False})
        # for i in range(axes):
            # axis = joystick.get_axis(i)
            # textPrint.tprint(screen, "Axis {} value: {:>6.3f}".format(i, axis))
        # textPrint.unindent()

          

        pan: float = joystick.get_axis(0)
        tilt: float = joystick.get_axis(1)
        zoom: float = joystick.get_axis(2)
        axis3: float = -0.5 #joystick.get_axis(3)
        tilt_speed: str = str(hex(round(20*(abs(tilt)**((2 + axis3))))))[2:].zfill(2).upper()
        pan_speed: str = str(hex(round(24*(abs(pan)**((2 + axis3))))))[2:].zfill(2).upper()
        zoom_speed: str = str(round(2*abs(zoom)**1))  # Only goes up to 7, so doesn't need hex conversion

        preset_num: str = "00"
        preset_set: str = None
        presetCheck: bool = False
        preset_bytes: str = None
        sending_preset = False
        for button in BUTTONS:
            if button['value']:
                if but4:
                    button['command'] = f"00 09 81 01 04 3F 01 {button['preset']} FF"
                else:
                    sending_preset = True
                    button['command'] = f"00 09 81 01 04 3F 02 {button['preset']} FF"

        pan_direction_str: str = None
        pan_direction: str = '3'
        if pan > 0:
            pan_direction_str = 'Right'
            pan_direction = '2'
        elif pan < 0:
            pan_direction_str = 'Left'
            pan_direction = '1'
        if pan_speed == '00':
            # Since it can't be 0
            pan_direction_str = 'Stopped'
            pan_direction = '3'
            pan_speed = '01'  # Since it can't be 0
        
        tilt_direction_str: str = None
        tilt_direction: str = '3'
        if tilt > 0:
            tilt_direction_str = 'Down'
            tilt_direction = '2'
        elif tilt < 0:
            tilt_direction_str = 'Up'
            tilt_direction = '1'
        if tilt_speed == '00':
            # Since it can't be 0
            tilt_direction_str = 'Stopped'
            tilt_direction = '3'
            tilt_speed = '01'
        pt_command = f"81 01 06 01 {pan_speed} {tilt_speed} 0{pan_direction} 0{tilt_direction} FF"
        payload_type = '00'
        pt_payload_length = "0B"  # str(hex(11))[2:].zfill(2)
        pt_message = f"{payload_type} {pt_payload_length} {pt_command}"
        pt_bytes = bytearray.fromhex(pt_message)
 
        zoom_direction_str: str = None
        zoom_direction: str = '0'
        zoom_out: bool = joystick.get_button(18)
        zoom_in: bool = joystick.get_button(19)
        
        if zoom > 0:
            zoom_direction_str = 'In'
            zoom_direction = '2'
        elif zoom < 0:
            zoom_direction_str = 'Out'
            zoom_direction = '3'
        if zoom_speed == '0':
            zoom_direction_str = 'Stopped'
            zoom_direction = '0'
        if zoom_out:
            zoom_direction_str = 'out'
            zoom_direction = '3'
            zoom_speed = "F"
        if zoom_in:
            zoom_direction_str = 'In'
            zoom_direction = '2'
            zoom_speed = "F" 
        z_command = f"81 01 04 07 {zoom_direction}{zoom_speed} FF"
        payload_type = '00'
        z_payload_length = "08"  # str(hex(11))[2:].zfill(2)
        z_message = f"{payload_type} {z_payload_length} {z_command}"
        #print(z_message)
        z_bytes = bytearray.fromhex(z_message)
 

        # payload_type = bytearray.fromhex('00')
        # z_payload = bytearray.fromhex(z_command)
        # payload_length = bytearray.fromhex(hex_str)
        # z_message = payload_length + z_payload

        if gui:
            textPrint.tprint(screen, "Joystick {}".format(i))
            textPrint.indent()

            textPrint.tprint(screen, f"Pan-Tilt Command sent {pt_message}")
            textPrint.tprint(screen, f"Zoom Command sent {z_message}")

            # textPrint.tprint(screen, "Pan {} value: {:>6.3f}".format(0, pan))
            # textPrint.tprint(screen, "Tilt {} value: {:>6.3f}".format(1, tilt))
            # textPrint.tprint(screen, "Zoom {} value: {:>6.3f}".format(2, zoom))
            # textPrint.tprint(screen, "Axis {} value: {:>6.3f}".format(3, zoom))

            textPrint.tprint(screen, f"Tilting {tilt_direction_str} at Speed {tilt_speed}")
            textPrint.tprint(screen, f"Moving {pan_direction_str} at Speed {pan_speed}")
            textPrint.tprint(screen, f"Zooming {zoom_direction_str} at Speed {zoom_speed}")
            textPrint.tprint(screen, f"Pan-Tilt Command sent {pt_command}")
            textPrint.tprint(screen, f"Zoom Command sent {z_command}")
            textPrint.tprint(screen, f"Zoom Command sent {z_command}")
            for i, button in enumerate(BUTTONS):
                textPrint.tprint(screen, f"Button {i} sent {button['command']}")

        if run_connection:
            if pt_bytes != pt_previous:
                pt_previous = pt_bytes
                s.send(pt_bytes)
                # print(pt_bytes)
            elif pt_command == '81 01 06 01 01 01 03 03 FF' and not sending_preset : # Stop command
                s.send(pt_bytes)
                #print(pt_bytes)
                #s.send(z_bytes)
            if z_bytes != z_previous:
                z_previous = z_bytes
                s.send(z_bytes)
                #print(z_bytes)
            elif z_message == '81 01 04 07 00 FF' and not sending_preset :
                s.send(z_bytes)
                # print(z_bytes)
            for button in BUTTONS:
                if button['command']:
                    preset_bytes = bytearray.fromhex(button['command'])
                    s.send(preset_bytes)
            sleep(.01)






    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
    #
    # Go ahead and update the screen with what we've drawn.
    if gui:
        pygame.display.flip()
        # Limit to 20 frames per second.
        clock.tick(13)
    sleep(.05)
pygame.quit()
