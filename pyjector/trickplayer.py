#!/usr/bin/env python3

import sys
import os
import logging

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

from rtpsink import rtpsink

class TrickPlayer():

    def __init__(self):
        self.file = "/home/nicola/mt1.mp4"
        self.pipeline = None
        self.video_sink = None
        self.playing = False
        self.rate = 1.0

    def set_pipeline(self):
        self.pipeline = Gst.parse_launch("playbin uri=file://%s" % self.file)
        videosink = Gst.ElementFactory.make("autovideosink")
        self.pipeline.set_property('video_sink', videosink)

    def __send_seek_event(self):
        fmat = Gst.Format.TIME
        seek_event = None

        ret, position = self.pipeline.query_position(fmat)
        if (not ret):
            print("Unable to retrieve current position.")
            return data

        if (self.rate > 0):
            seek_event = Gst.Event.new_seek(self.rate,
                Gst.Format.TIME,
                (Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE),
                Gst.SeekType.SET,
                position,
                Gst.SeekType.SET,
                -1)
        else:
            seek_event = Gst.Event.new_seek(self.rate,
                Gst.Format.TIME,
                (Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE),
                Gst.SeekType.SET,
                -1,
                Gst.SeekType.SET,
                position)

        if (self.video_sink == None):
            self.video_sink = self.pipeline.get_property('video_sink')

        self.video_sink.send_event(seek_event)

        print("Current rate: %d" % self.rate)

    def change_file(self, newfile):
        self.file = newfile
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline.set_property('uri', "file://%s" % newfile)
        self.pipeline.set_state(Gst.State.PLAYING if self.playing else Gst.State.PAUSED)

    def cleanup(self):
        self.pipeline.set_state(Gst.State.NULL)
        if (self.video_sink):
            self.video_sink.unref()
        self.pipeline.unref()

    def play_pause(self):
        self.playing = not self.playing
        self.pipeline.set_state(Gst.State.PLAYING if self.playing else Gst.State.PAUSED)

    def set_speed(self, rate):
        self.rate = rate
        self.__send_seek_event()

    def reverse(self):
        self.rate *= -1.0
        self.__send_seek_event()

    def step_frame(self):
        if (self.video_sink == None):
            self.video_sink = self.pipeline.get_property('video_sink')
        self.video_sink.send_event(Gst.Event.new_step(Gst.Format.BUFFERS, 1, self.rate, True, False))