#!/usr/bin/env python3

import sys
import os
import logging
import threading

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import GObject, Gst, GstVideo


logger = logging.getLogger(__name__)


class TrickPlayer():

    def __init__(self):
        self.file = None
        self.pipeline = None
        self.video_sink = None
        self.bus = None
        self.playing = False
        self.rate = 1.0
        self.loop = 0

    def set_pipeline(self):
        self.pipeline = Gst.parse_launch("playbin uri=file://%s" % self.file)
        self.pipeline.set_state(Gst.State.PAUSED)

    def set_video_sink(self):
        self.pipeline.set_property('video_sink', Gst.ElementFactory.make("autovideosink"))
        self.video_sink = self.pipeline.get_property('video_sink')
        
    def set_bus(self):
        self.bus = self.pipeline.get_bus()

    def run(self):
        self.set_pipeline()
        self.set_video_sink()
        self.set_bus()

        
    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.jump_loop()    

    def __send_seek_event(self):
        fmat = Gst.Format.TIME
        ret, position = self.pipeline.query_position(fmat)
        print(position)
        if (not ret):
            print("Unable to retrieve current position.")
            return 

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
        self.video_sink.send_event(seek_event)
        logger.info("Current rate: %d", self.rate)

    def update_color_channel(self, channel_name, value):
        channels = self.pipeline.list_channels()
        for ch in channels:
            if (ch.label == channel_name):
                channel = ch
        if (not channel):
            return
        #step = step_size * (channel.max_value - channel.min_value)
        #self.pipeline.get_value = GstVideo.ColorBalance.get_value
        #value = self.pipeline.get_value(self.pipeline,channel)
        #print(value)
        #value += step
        if (value > channel.max_value):
            value = channel.max_value
        elif (value < channel.min_value):
            value = channel.min_value
        self.pipeline.set_value(channel, value)

    def start(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        self.playing = True

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.playing = False

    def change_file(self, newfile):
        self.file = newfile
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline.set_property('uri', "file://%s" % newfile)
        self.set_video_sink()
        if self.playing:
            self.pipeline.set_state(Gst.State.PLAYING)
        else:
            self.pipeline.set_state(Gst.State.PAUSED)


    def cleanup(self):
        self.pipeline.set_state(Gst.State.NULL)
        if (self.video_sink):
            self.video_sink.unref()
        self.pipeline.unref()

    def pause_play(self):
        self.pipeline.set_state(Gst.State.PAUSED if self.playing else Gst.State.PLAYING)
        self.playing = not self.playing

    def set_speed(self, rate):
        self.rate = rate
        self.__send_seek_event()

    def reverse(self):
        self.rate *= -1.0
        self.__send_seek_event()
    
    def jump_loop(self):
        if self.loop:
            if self.loop > 1:
                self.reverse()
            if (self.rate > 0):
                self.jump(0)
            else:
                self.jump(-1)
        
    def jump(self, position):
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

        self.video_sink.send_event(seek_event)

    def set_marker(self):
        pass

    def step_frame(self):
        if (self.video_sink == None):
            self.video_sink = self.pipeline.get_property('video_sink')
        self.video_sink.send_event(Gst.Event.new_step(Gst.Format.BUFFERS, 1, self.rate, True, False))
