# (C) Copyright 2016, Christian Burri
from colormania import Fore, Back, Style, Cursor, _in_idle
from .winterm import WinTerm
from os.path import dirname, join
from collections import OrderedDict
from configparser import ConfigParser
from time import time
from colorsys import rgb_to_hsv, rgb_to_hls
import sys

winterm = WinTerm()


def _add(a, b):
    return a + b


def _sub(a, b):
    return a - b


def _mul(a, b):
    return a * b


def _seq_mul(tup, b):
    return tuple((i * b for i in tup))


def _byte2range(byte, a, b=255):
    return byte / 255 * (b - a) + a


def _mix_color(c1, c2, mix):
    """mix of 0 returns c1 and mix of 1 returns c2"""
    return round(c2 * mix + c1 * (1 - mix))


class Color(object):
    """Provides color values
    """
    Black = 0
    Blue = 1
    Green = 2
    Aqua = 3
    Red = 4
    Purple = 5
    Yellow = 6
    White = 7
    LightBlack = 8
    LightBlue = 9
    LightGreen = 10
    LightAqua = 11
    LightRed = 12
    LightPurple = 13
    LightYellow = 14
    LightWhite = 15

    AllColors = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    ColorNames = ('Black', 'Blue', 'Green', 'Aqua', 'Red', 'Purple', 'Yellow', 'White', 'LightBlack', 'LightBlue',
                  'LightGreen', 'LightAqua', 'LightRed', 'LightPurple', 'LightYellow', 'LightWhite')

    _ColoramaNames = ('BLACK', 'BLUE', 'GREEN', 'CYAN', 'RED', 'MAGENTA', 'YELLOW', 'WHITE',
                      'LIGHTBLACK_EX', 'LIGHTBLUE_EX', 'LIGHTGREEN_EX', 'LIGHTCYAN_EX',
                      'LIGHTRED_EX', 'LIGHTMAGENTA_EX', 'LIGHTYELLOW_EX', 'LIGHTWHITE_EX')

    # standard color palette
    BasePalette = [(0, 0, 0), (0, 0, 128), (0, 128, 0), (0, 128, 128), (128, 0, 0), (128, 0, 128),
                        (128, 128, 0), (192, 192, 192), (128, 128, 128), (0, 0, 255), (0, 255, 0),
                        (0, 255, 255), (255, 0, 0), (255, 0, 255), (255, 255, 0), (255, 255, 255)]

    def import_palette(self, palette):
        self.BasePalette = palette

    def get_rgb(self, color):
        return self.BasePalette[color]

    def color_match(self, r, g, b):
        closest = None
        difference = 255 * 3
        for color, rgb in enumerate(self.BasePalette):
            dif = sum(map(abs, map(_sub, (r, g, b), rgb)))
            if dif < difference:
                difference = dif
                closest = color
        return closest


class Global(Color):
    """Sets the global background and foreground colors
    """

    @classmethod
    def set_background(cls, wincolor, on_stderr=False):
        if wincolor not in cls.AllColors:
            raise TypeError("not a valid color")
        current_fore = winterm.get_global_color() & 15
        back = wincolor << 4
        color = back + current_fore
        winterm.set_global_color(color, on_stderr)

    @classmethod
    def set_foreground(cls, wincolor, on_stderr=False):
        if wincolor not in cls.AllColors:
            raise TypeError("not a valid color")
        current_back = winterm.get_global_color() & (15 << 4)
        fore = wincolor
        color = current_back + fore
        winterm.set_global_color(color, on_stderr)

    @classmethod
    def reset_all(cls):
        winterm.reset_global()


class Shades(Color):
    chars = ['\u2588', '\u2593', '\u2592', '\u2591', ' ', '\u2580', '\u2584']

    full = chars[0]
    dark = chars[1]
    medium = chars[2]
    light = chars[3]
    empty = chars[4]
    upper = chars[5]
    lower = chars[6]

    shades = (empty, light, medium, dark, full, upper, lower)
    opacity = (0 / 100, 33 / 100, 50 / 100, 67 / 100, 100 / 100)
    preset_opacity = [(0, 33, 50, 67, 100), (0, 25, 50, 75, 100)]
    HEX = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')
    DEC = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'a': 10, 'b': 11, 'c': 12,
           'd': 13, 'e': 14, 'f': 15}
    dp = OrderedDict()
    for b in Color.AllColors:
        for f in Color.AllColors[b:]:
            for s in [1, 2, 3]:  # the shade
                b_rgb, f_rgb = Color.BasePalette[b], Color.BasePalette[f]
                R = _mix_color(b_rgb[0], f_rgb[0], opacity[s])
                G = _mix_color(b_rgb[1], f_rgb[1], opacity[s])
                B = _mix_color(b_rgb[2], f_rgb[2], opacity[s])
                dp[HEX[b] + HEX[f] + str(s)] = (R, G, B)
                if b == f:
                        break
    DefaultPalette = dp
    palette_name = 'DEFAULT'

    def __init__(self):
        super().__init__()
        try:
            self.load_palette('USER')
        except KeyError:
            try:
                self.load_palette('DEFAULT')
            except KeyError:
                self.FullPalette = self.DefaultPalette

    @classmethod
    def _test_chars(self):
        _pos = winterm.get_cursor_position()
        try:
            for c in self.chars:
                print(c)
        except:
            decoded = []
            for c in self.chars:
                c = c.encode('utf-8').decode(sys.stdout.encoding or 'utf-8')
                print(c)
                decoded.append(c)
            self.chars = decoded
        if not _in_idle:
            print(Cursor.POS(_pos.X, _pos.Y), end='')
            print('  \n'*7 + Cursor.POS(_pos.X, _pos.Y), end='')
        self.full = self.chars[0]
        self.dark = self.chars[1]
        self.medium = self.chars[2]
        self.light = self.chars[3]
        self.empty = self.chars[4]
        self.upper = self.chars[5]
        self.lower = self.chars[6]
        self.shades = (self.empty, self.light, self.medium, self.dark, self.full, self.upper, self.lower)

    def create_palette(self, rgb_func):
        # at this time, only the default palette should be loaded
        palette = OrderedDict()
        for b in Color.AllColors:
            for f in Color.AllColors[b:]:
                for s in [1, 2, 3]:  # the shade
                    b_rgb = self.BasePalette[b]
                    f_rgb = self.BasePalette[f]
                    key = self.HEX[b] + self.HEX[f] + str(s)
                    # will only adjust if background and foreground values are different
                    rgb = rgb_func(b_rgb, f_rgb, self.opacity[s])
                    palette[key] = rgb
                    if b == f:
                        break
        self.FullPalette = palette
        self.palette_name = str(time())

    def recreate_shades(self):
        self.shades = (self.empty, self.light, self.medium, self.dark, self.full, self.upper, self.lower)

    def save_current_palette(self, name):
        if name.upper() == 'DEFAULT':
            raise ValueError("'DEFAULT' can't be overwritten")
        palette = OrderedDict()
        for key, rgb in self.FullPalette.items():
            palette[key] = rgb

        file = join(dirname(__file__), 'palettes.ini')
        config = ConfigParser()
        config.read(file)
        config[name] = palette
        with open(file, 'w') as ini:
            config.write(ini)

    def load_palette(self, name):
        file = join(dirname(__file__), 'palettes.ini')
        palette = OrderedDict()
        config = ConfigParser()
        config.read(file)
        loaded = config[name]
        if len(loaded) != 376:
            if name.upper() == 'DEFAULT':
                raise KeyError("wrong value for DEFAULT")
            raise RuntimeError("Palette %s incomplete. Size is %d, should be 376" % (name, len(loaded)))
        for key in loaded:
            palette[key] = eval(loaded[key])
        self.FullPalette = palette
        self.palette_name = name

    def set_shade_opacity(self, empty, light, medium, full):
        self.opacity = (empty, light, medium, full)

    def color_match(self, r, g, b, greyscale=False, verbose=False):
        if greyscale:
            difference = 1
            light = rgb_to_hls(r/255, g/255, b/255)[1]
            value = rgb_to_hsv(r/255, g/255, b/255)[2]
            for i, op in enumerate(self.opacity):
                dif = abs(light-op)
                if dif < difference:
                    difference = dif
                    s = i
            return 0, 15, s

        if verbose:
            print('searching', (r, g, b))
        closest = None
        difference = 255 * 3
        for color, rgb in self.FullPalette.items():
            rgb = list(rgb)
            dif = sum(map(abs, map(_sub, (r, g, b), rgb)))
            if dif < difference:
                difference = dif
                closest = color
                found_rgb = rgb
        if verbose:
            print('found', found_rgb)
        b, f, s = closest
        return self.DEC[b], self.DEC[f], int(s)

    def block(self, back, fore, shade, shape=2, transparent=False, ansi=True):
        if not ansi or _in_idle:
            return '%s' % (self.shades[shade] * shape)

        background = getattr(Back, self._ColoramaNames[back])
        if transparent:
            background += Style.RESET_ALL

        return '%s%s%s' % (background,
                           getattr(Fore, self._ColoramaNames[fore]),
                           self.shades[shade] * shape)


Color = Color()
Shades = Shades()
