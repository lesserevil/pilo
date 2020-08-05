from PIL import Image
import select
import time
import io
import numpy as np
import cv2
import v4l2capture
import select
import mmap
import math

import v4l2
import fcntl

from pprint import pprint

#capture_width = 1920
#capture_height = 1080
capture_width = 1280
capture_height = 720

# Create mmapped file
fb_filename = "/tmp/PiLO_fb"
fb_file = open(fb_filename, "wb")
fb_file.seek((math.ceil(capture_width/16)*16)*(math.ceil(capture_height/16)*16)*3-1)
fb_file.write(b"\0")
fb_file.close()

fb_file = open(fb_filename, "a+b")
mapfile = mmap.mmap(fb_file.fileno(), 0)
fb_file.close()

video = v4l2capture.Video_device("/dev/video0")
try:
    video.set_format(capture_width, capture_height, yuv420=0)
    (size_x, size_y, fmt) = video.get_format()
    print(size_x, size_y, fmt, video.fileno())

    v = video.fileno()
    v4l2_cap = v4l2.v4l2_capability()
    fcntl.ioctl(v, v4l2.VIDIOC_QUERYCAP, v4l2_cap)
    print(v4l2_cap.driver, v4l2_cap.card, v4l2_cap.version, v4l2_cap.capabilities)

    v4l2_input = v4l2.v4l2_input()
    fcntl.ioctl(v, v4l2.VIDIOC_ENUMINPUT, v4l2_input)
    print(v4l2_input.index, v4l2_input.name, v4l2_input.type, v4l2_input.status, v4l2_input.reserved[0], v4l2_input.reserved[1], v4l2_input.reserved[2], v4l2_input.reserved[3]   )

    v4l2_timings = v4l2.v4l2_dv_timings()
    fcntl.ioctl(v, v4l2.VIDIOC_G_DV_TIMINGS, v4l2_timings)
    print(v4l2_timings)

    video.create_buffers(1)
    video.start()
    time.sleep(5)
    t = time.time()
    while True:
        (size_x, size_y, fmt) = video.get_format()
        print(size_x, size_y)
        video.queue_all_buffers()
        select.select((video,), (), ())
        mapfile.seek(0)
        image = video.read()
        #pil_image = Image.frombuffer("RGB", (size_x, size_y), image)
        mapfile.write(cv2.cvtColor(np.frombuffer(image, np.uint8).reshape(size_y, size_x, 3), cv2.COLOR_RGB2BGR))
        mapfile.flush()
        #print(".", end='')
        #if time.time() > t+1:
            #print()
            #t = time.time()
finally:
    video.close()
    mapfile.close()
