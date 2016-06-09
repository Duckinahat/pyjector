#!/usr/bin/env python3

import sys
import os
import logging
import threading

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GstVideo


logger = logging.getLogger(__name__)


class TrickPlayer():

    def __init__(self):
        self.file = "/home/nicola/mt1.mp4"
        self.pipeline = None
        self.video_sink = None
        self.playing = False
        self.rate = 1.0
        self.loop = True

    def set_pipeline(self):
        self.pipeline = Gst.parse_launch("playbin uri=file://%s" % self.file)
        self.set_video_sink()
        self.pipeline.set_property('video_sink', self.video_sink)

    def set_video_sink(self):
        pass

    def run(self):
        pass

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

        logger.info("Current rate: %d", self.rate)

    def update_color_channel(self, channel_name, step_size):
        color_balance = self.pipeline.list_channels()
        channels = color_balance.list_channels()
        for ch in channels:
            if (ch.label == channel_name):
                channel = ch
        if (not channel):
            return

        step = step_size * (channel.max_value - channel.min_value)
        value = color_balance.get_value(channel)
        value += step
        if (value > channel.max_value):
            value = channel.max_value
        elif (value < channel.min_value):
            value = channel.min_value
        color_balance.set_value(channel, value)

    def __start(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        self.playing = True

    def __stop(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.playing = False

    def change_file(self, newfile):
        self.file = newfile
        self.__stop()
        self.pipeline.set_property('uri', "file://%s" % newfile)
        self.__start()

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

    def set_marker(self):
        pass

    def step_frame(self):
        if (self.video_sink == None):
            self.video_sink = self.pipeline.get_property('video_sink')
        self.video_sink.send_event(Gst.Event.new_step(Gst.Format.BUFFERS, 1, self.rate, True, False))