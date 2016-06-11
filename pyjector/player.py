#!/usr/bin/env python3

import os
import threading
import time
import logging
import queue

import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject, Gtk, Gdk

from trickplayer_testing import TrickPlayer

class GTK_Main:

    def __init__(self):
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_default_size(640,480)
        window.connect("destroy", self.clean_quit, "WM destroy")
        
        viewer = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        viewer.set_default_size(640,480)
        viewer.connect("destroy", self.on_click_pause)
        drawing_area = Gtk.DrawingArea()
        viewer.add(drawing_area)
        viewer.show_all()
        self.xid = drawing_area.get_property('window').get_xid()

        
        grid = Gtk.Grid()
        window.add(grid)
        
        b_play = Gtk.Button(label="Play")
        b_play.connect("clicked", self.on_click_play)
        b_pause = Gtk.Button(label="Pause")
        b_pause.connect("clicked", self.on_click_pause)
        b_reverse = Gtk.Button(label="Reverse")
        b_reverse.connect("clicked", self.on_click_reverse)
        b_cue = Gtk.Button(label="Cue")
        b_cue.connect("clicked", self.on_click_cue)
        b_loop0 = Gtk.RadioButton.new_with_label_from_widget(None, "None")
        b_loop0.connect("toggled", self.on_toggle_loop, 0)
        b_loop1 = Gtk.RadioButton.new_with_label_from_widget(b_loop0, "Loop")
        b_loop1.connect("toggled", self.on_toggle_loop, 1)
        b_loop2 = Gtk.RadioButton.new_with_label_from_widget(b_loop0, "Bounce")
        b_loop2.connect("toggled", self.on_toggle_loop, 2)
        s_hue = Gtk.Scale.new_with_range(1,-1000,1000,50)
        s_hue.label = "Hue"
        s_hue.set_vexpand(True)
        s_hue.add_mark(0, Gtk.PositionType.LEFT, None)
        s_hue.set_value(0)
        s_hue.connect("value_changed", self.on_slider_move, "HUE")
        s_brt = Gtk.Scale.new_with_range(1,-1000,1000,50)
        s_brt.set_vexpand(True)
        s_brt.add_mark(0, Gtk.PositionType.LEFT, None)
        s_brt.set_value(0)
        s_brt.connect("value_changed", self.on_slider_move, "BRIGHTNESS")
        s_con = Gtk.Scale.new_with_range(1,-1000,1000,50)
        s_con.set_vexpand(True)
        s_con.add_mark(0, Gtk.PositionType.LEFT, None)
        s_con.set_value(0)
        s_con.connect("value_changed", self.on_slider_move, "CONTRAST")
        s_sat = Gtk.Scale.new_with_range(1,-1000,1000,50)
        s_sat.set_vexpand(True)
        s_sat.add_mark(0, Gtk.PositionType.LEFT, None)
        s_sat.set_value(0)
        s_sat.connect("value_changed", self.on_slider_move, "SATURATION")
        b_hue = Gtk.Button(label="Hue")
        b_hue.connect("clicked", self.on_slider_reset, s_hue)
        b_brt = Gtk.Button(label="Brightness")
        b_brt.connect("clicked", self.on_slider_reset, s_brt)        
        b_con = Gtk.Button(label="Contrast")
        b_con.connect("clicked", self.on_slider_reset, s_con)
        b_sat = Gtk.Button(label="Saturation")
        b_sat.connect("clicked", self.on_slider_reset, s_sat)
        s_speed = Gtk.Scale.new_with_range(0,1,2,.01)
        s_speed.set_hexpand(True)
        s_speed.set_value(1)
        s_speed.connect("value_changed", self.on_speed_move)
        self.speedmult = 1.0
        b_speed = Gtk.Button(label="Speed")
        b_speed.connect("clicked", self.on_speed_reset, s_speed)
        b_dbl = Gtk.Button(label="x2")
        b_dbl.connect("clicked", self.on_speed_mult, s_speed, 2.0)
        b_hlf = Gtk.Button(label="/2")
        b_hlf.connect("clicked", self.on_speed_mult, s_speed, 0.5)
        self.l_speed = Gtk.Label("Speed: %f" % (self.speedmult*s_speed.get_value()))
        
        g_files = Gtk.Grid()
        self.filenum = 0
        file_buttons = [None] * 32
        for i in range(32):
            fb = Gtk.RadioButton.new_with_label_from_widget(
                file_buttons[0],
                format("%02d"%i))
            fb.connect("toggled", self.on_toggle_file, i)
            file_buttons[i] = fb
            g_files.attach(fb, i%4, i//4, 1,1)
        
                
        grid.add(b_play)
        grid.attach(b_pause, 1,0,1,1)
        grid.attach(b_reverse,2,0,1,1)
        grid.attach(b_cue, 3,0,1,1)
        grid.attach(b_loop0, 0,1,1,1)
        grid.attach(b_loop1, 1,1,1,1)
        grid.attach(b_loop2, 2,1,1,1)
        grid.attach(b_speed, 0,2,1,1)
        grid.attach(b_dbl,1,2,1,1)
        grid.attach(b_hlf,2,2,1,1)
        grid.attach(self.l_speed,3,2,1,1)
        grid.attach(s_speed, 0,3,4,1)
        grid.attach(s_hue,0,5,1,4)
        grid.attach(s_brt,1,5,1,4)
        grid.attach(s_con,2,5,1,4)
        grid.attach(s_sat,3,5,1,4)
        grid.attach(b_hue,0,4,1,1)
        grid.attach(b_brt,1,4,1,1)
        grid.attach(b_con,2,4,1,1)
        grid.attach(b_sat,3,4,1,1)
        grid.attach(g_files, 4,0,16,16)
        
        self.player = TrickPlayer()
        self.player.run()

        bus = self.player.bus
        bus.add_signal_watch()
        bus.connect("message", self.player.on_message)
        
        bus.enable_sync_message_emission()
        bus.connect('sync-message::element', self.on_sync_message)
        
        window.show_all()
        
    def on_click_play(self, button):
        self.player.start()    
    
    def on_click_reverse(self, button):
        self.player.reverse()
        
    def on_click_pause(self, button):
        self.player.pause_play()
        
    def on_click_cue(self, button):
        filename = format("/home/nicola/vids/%02d.mp4" % self.filenum)
        self.player.change_file(filename)
    
    def on_toggle_loop(self, button, mode):
        self.player.loop = mode
        
    def on_slider_move(self, slider, channel):
        self.player.update_color_channel(channel, slider.get_value())
    
    def on_slider_reset(self, button, slider):
        slider.set_value(0)
        
    def on_toggle_file(self, button, filenum):
        self.filenum = filenum
    
    def clean_quit(self, destroy, *args):
        self.player.stop()
        Gtk.main_quit(destroy,*args)
        
    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.jump_loop()
        
    def on_sync_message(self, bus, msg):
        msg.src.set_property('force-aspect-ratio', True)
        msg.src.set_window_handle(self.xid)
        
    def on_speed_move(self, slider):
        self.player.set_speed(slider.get_value()*self.speedmult)
        self.l_speed.set_text("Speed: %f" % (self.speedmult*slider.get_value()))
        
    def on_speed_reset(self, button, slider):
        slider.set_value(1)
        self.speedmult = 1
        self.on_speed_move(slider)
        
    def on_speed_mult(self, button, slider, mult):
        self.speedmult *= mult
        self.on_speed_move(slider)

if __name__=='__main__':
    GObject.threads_init()
    Gst.init()
    g = GTK_Main()
    Gtk.main()
        
