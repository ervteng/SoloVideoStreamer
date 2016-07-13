#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
# Use a queue to rtmpsink not block the pipeline
"""

import sys
import gst
import subprocess
import signal

from datetime import datetime
from time import sleep

#must import this module for video to function
subprocess.call(['modprobe', 'mxc_v4l2_capture'])

# Artoo IP and port
CONTROLLER_IP = "10.1.1.1"
CONTROLLER_PORT = 5550

# Add client as desired. 
CLIENT_IP = "10.1.1.191"
CLIENT_PORT = 5600

# Matches the 3DR pipe as close as possible
pipeline_str = """
mfw_v4lsrc device=/dev/video0 name=src ! mfw_ipucsc ! video/x-raw-yuv, format=(fourcc)I420, width=(int)1280, height=(int)720, framerate=(fraction)30/1, pixel-aspect-ratio=(fraction)1/1 ! 
queue name=q !  vpuenc codec=6 bitrate=1800000 gopsize=15 force-framerate=true framerate-nu=25 name=enc ! rtph264pay config-interval=1 pt=96 name=rtp ! 
multiudpsink name=sink clients=%s:%d,%s:%d sync=false async=false udpsrc port=5550 
""" %(CONTROLLER_IP, CONTROLLER_PORT, CLIENT_IP, CLIENT_PORT)

# Grab the parts of the pipeline by name
pipeline = gst.parse_launch(pipeline_str)
src = pipeline.get_by_name("src")
sink = pipeline.get_by_name("sink")
q = pipeline.get_by_name("q")
rtp = pipeline.get_by_name("rtp")
enc = pipeline.get_by_name("enc")


if not pipeline or not src or not sink:
    print "Not all elements could be created."
    exit(-1)

# Start the pipeline
ret = pipeline.set_state(gst.STATE_PLAYING)
if ret ==  gst.STATE_CHANGE_FAILURE:
    print "Unable to set the pipeline to the playing state."
    exit(-1)

print "Set the pipeline to the playing state."

# Wait until error or EOS
bus = pipeline.get_bus()
bus.add_signal_watch()

# Gracefully break on ctrl+c
def sigint_handler(signum, frame):
    pipeline.set_state(gst.STATE_NULL)
    print "Ending video stream..."
    sys.exit()
 
signal.signal(signal.SIGINT, sigint_handler)

# Create keyframe event 
struct = gst.structure_from_string('GstForceKeyUnit')
event = gst.event_new_custom (gst.EVENT_CUSTOM_DOWNSTREAM, struct)

while True:
    # Send a force keyframe event every second to allow syncing
    pipeline.send_event(event)
    sleep(1)

# Free resources
pipeline.set_state(gst.STATE_NULL)