import sdl2.ext
from sdl2 import sdlimage

from .imdraw import ImageFormat as ImageFormat
from .imdraw import SoftwareImDraw as SoftwareImDraw
from .imdraw import WindowImDraw as WindowImDraw


def init_sdl(register_atexit: bool = True):
    sdl2.ext.init()
    sdlimage.IMG_Init(
        sdlimage.IMG_INIT_JPG | sdlimage.IMG_INIT_PNG
        | sdlimage.IMG_INIT_TIF | sdlimage.IMG_INIT_WEBP
        | sdlimage.IMG_INIT_JXL | sdlimage.IMG_INIT_AVIF
    )
    if register_atexit:
        import atexit
        atexit.register(sdl2.ext.quit)
