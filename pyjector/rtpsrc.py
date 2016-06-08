#!/usr/bin/env python3

import logging
import threading

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObjecto, Gst


class SendRTP():

    def __init__(self, pipeline):
        self.pipeline = pipeline

