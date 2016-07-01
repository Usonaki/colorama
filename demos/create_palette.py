# (C) Copyright 2016, Christian Burri
from __future__ import print_function
from time import sleep
import fixpath
from colormania import Shades, init

_min = min

init()


def adjust_rgb(r=0, g=0, b=0):
    def mix(background, foreground, mix):
        byte = 255

        def adjust(b, f, mix, min, max):
            if b == f:
                return b
            b = b / byte * (max - min) + min
            f = f / byte * (max - min) + min
            return round(f * mix + b * (1 - mix))

        R = adjust(background[0], foreground[0], mix, r, 255)
        G = adjust(background[1], foreground[1], mix, g, 255)
        B = adjust(background[2], foreground[2], mix, b, 255)
        return R, G, B

    return mix


Shades.create_palette(adjust_rgb(34, 37, 33))
Shades.save_current_palette('USER')
print("Palette saved")

sleep(2)
