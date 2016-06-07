#!/usr/bin/env python3

import sys, os

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst


data = {
    'pipeline' : None,
    'video_sink' : None,
    'loop' : True,
    'playing' : True,
    'rate' : 1.0,
}

def send_seek_event():
    global data
    position = 0
    fmat = Gst.Format.TIME
    seek_event = None

    ret, position = data['pipeline'].query_position(fmat)
    if (not ret):
        print("Unable to retrieve current position.")
        return data

    if (data['rate'] > 0):
        seek_event = Gst.Event.new_seek(data['rate'],
            Gst.Format.TIME,
            (Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE),
            Gst.SeekType.SET,
            position,
            Gst.SeekType.NONE,
            0)
    else:
        seek_event = Gst.Event.new_seek(data['rate'],
            Gst.Format.TIME,
            (Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE),
            Gst.SeekType.SET,
            0,
            Gst.SeekType.NONE,
            position)

    if (data['video_sink'] == None):
        data['video_sink'] = data['pipeline'].get_property('video_sink')

        data['video_sink'].send_event(seek_event)

    print("Current rate: %d" % data['rate'])

def handle_keyboard():
    global data
    inp = input("Enter command: ")
    if (inp == 'p'):
        data['playing'] = not data['playing']
        data['pipeline'].set_state(Gst.State.PLAYING if data['playing'] else Gst.State.PAUSED)
    elif (inp[0] == 's'):
        try:
            data['rate'] = float(input("Enter speed: "))
            send_seek_event()
        except:
            return
    elif (inp == 'r'):
        data['rate'] *= -1.0
        send_seek_event()
    elif (inp == 'n'):
        if (data['video_sink'] == None):
            data['video_sink'] = data['pipeline'].get_property('video_sink')
            data['video_sink'].send_event(Gst.Event.new_step(Gst.Format.BUFFERS, 1, data['rate'], True, False))
    elif (inp == 'q'):
        data['loop'] = False
    return

if __name__=='__main__':
    global data
    Gst.init()
    print(0)
    data['pipeline'] = Gst.parse_launch("playbin uri=file:///home/nicola/mt1.mp4")
    print(1)
    ret = data['pipeline'].set_state(Gst.State.PAUSED)
    if (ret == Gst.StateChangeReturn.FAILURE):
        Gst.Object.unref(data['pipeline'])
        exit(-1)

    while (data['loop']):
        handle_keyboard()
    
    data['pipeline'].set_state(Gst.State.NULL)
    if (data['video_sink'] != NULL):
        Gst.Object.unref(data['video_sink'])
    Gst.Object.unref(data['pipeline'])
    exit(0)
    
