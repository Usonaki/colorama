# Copyright Jonathan Hartley 2013. BSD 3-Clause license, see LICENSE file.
import sys
_in_idle = 'idlelib' in sys.modules  # check if running in IDLE

from .initialise import init, deinit, reinit, colorama_text
from .ansi import Fore, Back, Style, Cursor
from .ansitowin32 import AnsiToWin32
from .color import Color, Global, Shades
from .image import Image


