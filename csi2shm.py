#!/usr/bin/env python

# Gets input from rpi camera and pushes it to a raw shared memory
# area for other apps to use, in this case, x11vnc.

import picamera
#import posix_ipc
import io
import mmap
from time import sleep
import sys

# set up shared memory
# we set up enough space for 1920x1080x32 so we don't have to resize it later
#shm = posix_ipc.SharedMemory('PiLO_shm', posix_ipc.O_CREAT, size=1280*720*24/8)

fb_file = open("/tmp/PiLO_fb", "a+b")

mapfile = mmap.mmap(fb_file.fileno(), 0)

fb_file.close()

# attach to camera
try:
    with picamera.PiCamera() as camera:
        camera.resolution = (1280, 720)
        stream = io.BytesIO()
        for foo in camera.capture_continuous(stream, use_video_port=True, format='rgb'):
            print(stream.truncate())
            stream.seek(0)
            mapfile.seek(0)
            while stream.readinto(mapfile) > 0:
                continue
            print(mapfile.tell())
            print(mapfile.size())
            stream.truncate(0)
            stream.seek(0)
            #sleep(0.05)
finally:
    mapfile.close()
