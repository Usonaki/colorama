# (C) Copyright 2016, Christian Burri
from functools import wraps
from colormania import Color, Shades, Style, _in_idle


def _add(a, b):
    return a + b


def _sub(a, b):
    return a - b


def _mul(a, b):
    return a * b


def _seq_mul(seq, b):
    return (i*b for i in seq)


def cashed(f):
    cashed_results = {}

    @wraps(f)  # keeps name, docstring etc. of f
    def cashed_function(*args, **kwargs):
        try:
            return cashed_results[(tuple(args), tuple(sorted(kwargs.items())))]
        except KeyError:
            pass

        result = f(*args, **kwargs)
        cashed_results[(tuple(args), tuple(sorted(kwargs.items())))] = result
        return result
    return cashed_function


class Image(object):
    def __init__(self, image_data, width, height):
        if len(image_data) != width*height:
            raise ValueError("data size incorrect")
        if len(image_data[0]) != 3:
            raise TypeError("incorrect data format")
        self.data = image_data
        self.width = width
        self.height = height
        self.size = None
        self.image = None

    def show(self, size=79, vstretch=1.33, pixel_format=0, greyscale=False, negative=False, smooth=0,
             alpha=None, tolerance=0):
        """
        :param size: width in number of characters
        :param vstretch: vertical stretching applied
        :param pixel_format: 0:▀, 1:▒, 2:▒▒, 3:▒▒▒
                                                  ▒▒▒
        :param smooth: radius of smoothing filter
        :param alpha: rgb value used for alpha
        :param tolerance: alpha tolerance
        """
        self._render(size, vstretch, pixel_format, greyscale, negative, smooth, alpha, tolerance, Shades.palette_name)
        print(self.image)

    @cashed
    def _render(self, size=79, vstretch=1.33, pixel_format=0, greyscale=False, negative=False, smooth=0,
                alpha=None, tolerance=0, palette=None):
        pf = pixel_format
        block_width = pf or 1  # width of a block in number of characters
        size = min(size, 80, self.width*block_width)
        block_height = [0.5, 1, 1, 2][pf]  # height of a block in number of printed lines
        new_width = size // block_width  # width of printed image in number of blocks (not characters)
        ratio = new_width / self.width
        new_height = int(self.height * ratio * vstretch / [1, 2, 1, 1.5][pf])  # height in number of blocks
        i_step = self.width/new_width
        j_step = self.height/new_height

        if smooth:
            weight = []
            total_weight = 0
            for l in range(-smooth, smooth+1):
                w_l = []
                for k in range(-smooth, smooth+1):
                    w_k = 1/max(abs(k)+1, abs(l)+1)
                    total_weight += w_k
                    w_l.append(w_k)
                weight.append(w_l)
        image = ''
        for j in range(new_height):
            if pf == 0 and j % 2:
                continue  # skip odd lines
            line = ''
            for i in range(new_width):
                rgb = self.data[int(i*i_step)+int(j*j_step)*self.width]
                if pf == 0:
                    try:
                        rgb2 = self.data[int(i*i_step)+int((j+1)*j_step)*self.width]
                    except IndexError:  # last line reached
                        if not alpha:
                            alpha = (-1, -1, -1)
                            tolerance = 0
                        rgb2 = alpha

                if alpha:
                    dif = max(map(abs, map(_sub, rgb, alpha)))
                    dif2 = dif
                    if pf == 0:
                        dif2 = max(map(abs, map(_sub, rgb2, alpha)))
                    if dif <= tolerance and dif2 <= tolerance:
                        line += Shades.block(0, 0, 0, shape=block_width, transparent=True)
                        continue

                if smooth:
                    total = (0, 0, 0)
                    total2 = (0, 0, 0)
                    for l in range(-smooth, smooth+1):
                        for k in range(-smooth, smooth+1):
                            try:
                                pixel = self.data[int(i*i_step)+k+int(j*j_step+l)*self.width]
                            except IndexError:
                                pixel = rgb
                            if pf == 0 and rgb2 != (-1, -1, -1):
                                try:
                                    pixel2 = self.data[int(i*i_step)+k+int((j+1)*j_step+l)*self.width]
                                except IndexError:
                                    pixel2 = rgb2
                            w = weight[l][k]
                            total = map(_add, total, _seq_mul(pixel, w))
                            if pf == 0:
                                total2 = map(_add, total2, _seq_mul(pixel2, w))
                    rgb = tuple(_seq_mul(total, 1/total_weight))
                    if pf == 0 and rgb2 != (-1, -1, -1):
                        rgb2 = tuple(_seq_mul(total2, 1/total_weight))

                if pf == 0:
                    match = Color.color_match(*rgb)
                    match2 = Color.color_match(*rgb2)
                    if alpha:
                        if dif <= tolerance:  # upper half is transparent
                            line += Shades.block(0, match2, 6, shape=1, transparent=True)
                            continue
                        if dif2 <= tolerance:  # lower half is transparent
                            line += Shades.block(0, match, 5, shape=1, transparent=True)
                            continue
                    if match != match2 and max(map(abs, map(_sub, rgb, rgb2))) >= 64:
                        line += Shades.block(match, match2, 6, shape=1)
                        continue
                    #rgb = _seq_mul(map(_add, rgb, rgb2), 0.5)

                match = Shades.color_match(*rgb, greyscale)
                ansi = not greyscale
                line += Shades.block(*match, shape=block_width, ansi=ansi)
            if size < 80:
                if not greyscale and not _in_idle:
                    line += Style.RESET_ALL
                line += '\n'
            image += line
            if pf == 3:
                image += line
        if not greyscale and not _in_idle:
            image += Style.RESET_ALL  # reset text color to default
        self.image = image
