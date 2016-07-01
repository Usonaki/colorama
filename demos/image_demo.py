# (C) Copyright 2016, Christian Burri
import fixpath

from time import sleep
from colormania import Image, init, _in_idle
from py_logo import py_logo, width, height
init()

image = Image(py_logo, width, height)
image.show(pixel_format=1, greyscale=False, vstretch=0.92 if _in_idle else 1.28)
image.show(pixel_format=1, greyscale=True, vstretch=0.92 if _in_idle else 1.28)
sleep(60)
