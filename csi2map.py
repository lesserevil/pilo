#!/usr/bin/env python3

import io
import time
import threading
import picamera
import mmap
import signal
import math

capture_width = 1280
capture_height = 720
capture_framerate = 60

# Create mmapped file
fb_filename = "/tmp/PiLO_fb"
fb_file = open(fb_filename, "wb")
fb_file.seek((math.ceil(capture_width/16)*16)*(math.ceil(capture_height/16)*16)*4-1)
fb_file.write(b"\0")
fb_file.close()

fb_file = open(fb_filename, "a+b")
mapfile = mmap.mmap(fb_file.fileno(), 0)
fb_file.close()

# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []

last_count = 0

def signal_handler(sig, frame):
    done = True
signal.signal(signal.SIGINT, signal_handler)

class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.start()
    def run(self):
        # This method runs in a separate thread
        global done
        global last_count
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    # Read the image and do some processing on it
                    # Image.open(self.stream)
                    # ...
                    # ...
                    # Set done to True if you want the script to terminate
                    # at some point
                    # done=True
                    count = 0
                    read_count = self.stream.readinto(mapfile)
                    while read_count > 0:
                        count = count + read_count
                        read_count = self.stream.readinto(mapfile)
                    if count != last_count:
                        print(count)
                        last_count = count
                except:
                    done = True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the pool
                    with lock:
                        pool.append(self)

def streams():
    while not done:
        with lock:
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            yield processor.stream
            processor.event.set()
        else:
            # When the pool is starved, wait a while for it to refill
            #time.sleep(0.03)
            print("pool starved")
            time.sleep(0.3)

with picamera.PiCamera() as camera:
    pool = [ImageProcessor() for i in range(4)]
    camera.resolution = (capture_width, capture_height)
    camera.framerate = capture_framerate
    #camera.start_preview()
    time.sleep(2)
    camera.capture_sequence(streams(), format="bgr", use_video_port=True)

# Shut down the processors in an orderly fashion
while pool:
    with lock:
        processor = pool.pop()
    processor.terminated = True
    processor.join()
