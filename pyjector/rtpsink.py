#!/usr/bin/env python3

import logging
import sys
import os

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst


class rtpsink():

    def __init__(self):
        self.bin = Gst.Bin.new('rtpsink')
        videosink = Gst.ElementFactory.make("autovideosink")
        pad = videosink.get_static_pad("sink")
        ghostpad = Gst.GhostPad.new("sink", pad)
        self.bin.add_pad(ghostpad)
        self.bin.add(videosink)

    def get_bin(self):
        return self.bin