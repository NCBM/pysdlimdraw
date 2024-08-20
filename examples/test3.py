from random import randint

import sdl2.ext

import sdlimdraw
from sdlimdraw import SoftwareImDraw, WindowImDraw  # noqa: F401
from sdlimdraw.imdraw import ImageFormat
from sdlimdraw.sdlext import (  # noqa: F401
    render_circle,
    render_circle_aa,
    render_circle_aa_fast,
)

WIDTH = 800
HEIGHT = 800

def randpoint(w: int, h: int):
    return randint(0, w - 1), randint(0, h - 1)

sdlimdraw.init_sdl()

sid = SoftwareImDraw.new(WIDTH, HEIGHT)
# sid = WindowImDraw.new(WIDTH, HEIGHT)

sid.fill((0, 0, WIDTH, HEIGHT), color=sdl2.ext.Color(64, 64, 64, 0))
sid.renderer.blendmode = sdl2.SDL_BLENDMODE_BLEND

for _ in range(300):
    x1, y1 = randpoint(WIDTH, HEIGHT)

    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)

    sid.circle((x1, y1), randint(5, 133), sdl2.ext.Color(r, g, b), aa="no")
    # sid.circle((x1, y1), randint(5, 133), sdl2.ext.Color(r, g, b), aa="fast")
    # sid.circle((x1, y1), randint(5, 133), sdl2.ext.Color(r, g, b), aa="fancy")

sid.renderer.present()

sid.save("test3.png", ImageFormat.PNG, overwrite=True)