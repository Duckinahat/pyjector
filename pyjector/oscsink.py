#! /usr/bin/env python3

import argparse
import threading
import queue
import logging

from pythonosc import dispatcher
from pythonosc import osc_server


class ListenOSC(threading.Thread):
    def __init__(self, command_q):
        threading.Thread.__init__(self)        
        self.command_q = command_q

    def run(self):

    
