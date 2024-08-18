from random import randint
from time import perf_counter

import sdl2.ext

from sdlimdraw import SoftwareImDraw, WindowImDraw
from sdlimdraw.imdraw import ImageFormat

WIDTH = 2048 * 4
HEIGHT = 1600 * 4

t0 = perf_counter()

sid = SoftwareImDraw.new(WIDTH, HEIGHT)
# sid = WindowImDraw.new(WIDTH, HEIGHT)

t1 = perf_counter()

for _ in range(100000):
    x1 = randint(0, WIDTH - 1)
    y1 = randint(0, HEIGHT - 1)
    x2 = randint(0, WIDTH - 1)
    y2 = randint(0, HEIGHT - 1)
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    sid.renderer.draw_line([(x1, y1), (x2, y2)], sdl2.ext.Color(r, g, b))
    # sid.renderer.present()

t2 = perf_counter()

sid.renderer.present()

t3 = perf_counter()

sid.save("test.jpg", ImageFormat.JPG, overwrite=True)

t4 = perf_counter()

print(f"{t1 - t0 = :.6f}s")
print(f"{t2 - t1 = :.6f}s")
print(f"{t3 - t2 = :.6f}s")
print(f"{t4 - t3 = :.6f}s")