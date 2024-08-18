import atexit

import sdl2
import sdl2.ext
from sdl2 import sdlimage

from .imdraw import ImageFormat as ImageFormat
from .imdraw import SoftwareImDraw as SoftwareImDraw
from .imdraw import WindowImDraw as WindowImDraw

sdl2.ext.init()
sdlimage.IMG_Init(sdlimage.IMG_INIT_JPG | sdlimage.IMG_INIT_PNG)
atexit.register(sdl2.ext.quit)
