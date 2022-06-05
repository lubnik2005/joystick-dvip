import pygame
import socket
from time import sleep
from TextPrint import _TextPrint
import dvip

CAMERA_IP: str = '192.168.250.52'
CAMERA_PORT: str = 5002
SEND_PACKETS: bool = True
SHOW_GUI: bool = False
CLOCK_FPS: int = 20


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4, TCP
s.connect((CAMERA_IP, CAMERA_PORT))
command = "00 08 81 01 06 01 07 FF"
hex_command = bytearray.fromhex(command)
r = s.send(hex_command)
print(r)
