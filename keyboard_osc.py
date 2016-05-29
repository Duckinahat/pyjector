#! /usr/bin/env python3
"""
This converts keyboard input to basic OSC commands for controlling video playback
"""
import argparse
import sys
import tty
import termios

from pythonosc import osc_message_builder
from pythonosc import udp_client


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
        help="The ip of the OSC server")
    parser.add_argument("--port", type=int,  default=12345,
        help="The port the OSC server is listening on")
    args = parser.parse_args()

    client = udp_client.UDPClient(args.ip, args.port)

    keymap = {
        'p' : "/play",
        'n' : "/next",
        'b' : "/previous",
        'f' : "/faster",
        's' : "/slower"
    }

    ch = ''
    while ch != 'q':
        ch = getch()
        if ch in keymap:
            msg = osc_message_builder.OscMessageBuilder(address = "/video"+keymap[ch])
            msg = msg.build()
            client.send(msg)
