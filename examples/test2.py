from random import randint

import sdl2.ext

import sdlimdraw
from sdlimdraw import SoftwareImDraw, WindowImDraw  # noqa: F401
from sdlimdraw.imdraw import ImageFormat

WIDTH = 2048
HEIGHT = 1600

def randpoint(w: int, h: int):
    return randint(0, w - 1), randint(0, h - 1)

sdlimdraw.init_sdl()

white = SoftwareImDraw.new(16, 16)
white.fill(color=sdl2.ext.Color())

# sid = SoftwareImDraw.new(WIDTH, HEIGHT)
sid = WindowImDraw.new(WIDTH, HEIGHT)
tex_white = sdl2.ext.Texture(sid.renderer, white.surface)

sid.fill((0, 0, WIDTH, HEIGHT), color=sdl2.ext.Color(64, 64, 64, 255))

for _ in range(1000):
    x1, y1 = randpoint(WIDTH, HEIGHT)
    x2, y2 = randpoint(WIDTH, HEIGHT)
    x3, y3 = randpoint(WIDTH, HEIGHT)

    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    vt1 = sdl2.SDL_Vertex((x1, y1), (r, g, b, 255), (1, 1))  # type: ignore
    vt2 = sdl2.SDL_Vertex((x2, y2), (r, g, b, 255), (1, 1))  # type: ignore
    vt3 = sdl2.SDL_Vertex((x3, y3), (r, g, b, 255), (1, 1))  # type: ignore

    sid.geometry(tex_white, vt1, vt2, vt3)

sid.renderer.present()

sid.save("test2.jpg", ImageFormat.JPG, overwrite=True)