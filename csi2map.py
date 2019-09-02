#!/usr/bin/env python

import io
import time
import threading
import picamera
import mmap
import signal

# Create mmapped file
fb_filename = "/tmp/PiLO_fb"
fb_file = open(fb_filename, "wb")
fb_file.seek(1280*720*24/3-1)
fb_file.write(b"\0")
fb_file.close()

fb_file = open(fb_filename, "a+b")
mapfile = mmap.mmap(fb_file.fileno(), 0)
fb_file.close()

# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []

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
                    while self.stream.readinto(mapfile) > 0:
                        continue
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
            time.sleep(0.1)

with picamera.PiCamera() as camera:
    pool = [ImageProcessor() for i in range(4)]
    camera.resolution = (1280, 720)
    camera.framerate = 30
    #camera.start_preview()
    time.sleep(2)
    camera.capture_sequence(streams(), format="bgr", use_video_port=True)

# Shut down the processors in an orderly fashion
while pool:
    with lock:
        processor = pool.pop()
    processor.terminated = True
    processor.join()
