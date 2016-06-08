#!/usr/bin/env python3

import sys
import os
import logging
import queue

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

from TrickPlayer import TrickPlayer


def handle_keyboard(player):
    inp = input("Enter command: ")
    if (inp == 'p'):
        player.play_pause()
    elif (inp == 's'):
        try:
            player.set_speed(float(input("Enter speed: ")))
        except:
            return
    elif (inp == 'r'):
        player.reverse()
    elif (inp == 'n'):
        player.step_frame()
    elif (inp == 'c'):
    	player.change_file("/home/nicola/Desktop/deepdream/t2.mp4")
    elif (inp == 'q'):
        return False
    return True

if __name__=='__main__':
    Gst.init()
    player = TrickPlayer()
    player.set_pipeline()
    ret = player.pipeline.set_state(Gst.State.PAUSED)
    if (ret == Gst.StateChangeReturn.FAILURE):
        exit(-1)
    loop = True
    while (loop):
        loop = handle_keyboard(player)
    exit(0)
