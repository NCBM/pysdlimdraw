from ctypes import c_int
from typing import Optional, Sequence

import sdl2
import sdl2.ext


def aacolor(color: sdl2.ext.Color, ratio: float = 1.):
    return sdl2.ext.Color(color.r, color.g, color.b, int(color.a * ratio))


def render_geometry(
    renderer: sdl2.ext.Renderer,
    texture: sdl2.ext.Texture,
    *vertices: sdl2.SDL_Vertex,
    indices: Optional[Sequence[int]] = None
):
    c_renderer = renderer.sdlrenderer
    c_texture = texture.tx
    vert_l = len(vertices)
    c_vertices = (sdl2.SDL_Vertex * vert_l)(*vertices)
    c_indices = None
    idcs_l = 0
    if indices:
        idcs_l = len(indices)
        c_indices = (c_int * idcs_l)(*indices)
    sdl2.SDL_RenderGeometry(c_renderer, c_texture, c_vertices, vert_l, c_indices, idcs_l)


def render_circle(
    renderer: sdl2.ext.Renderer,
    center: tuple[int, int],
    r: int,
    color: Optional[sdl2.ext.Color] = None
):
    # Middlepoint circle
    d = 2 * r
    x, y = r - 1, 0
    tx, ty = 1, 1
    cx, cy = center
    err = tx - d

    while x >= y:
        points = (
            (cx + x, cy - y),
            (cx + x, cy + y),
            (cx - x, cy - y),
            (cx - x, cy + y),
            (cx + y, cy - x),
            (cx + y, cy + x),
            (cx - y, cy - x),
            (cx - y, cy + x),
        )
        renderer.draw_point(points, color)

        if err <= 0:
            y += 1
            err += ty
            ty += 2

        if err > 0:
            x -= 1
            tx += 2
            err += (tx - d)


def render_circle_aa(
    renderer: sdl2.ext.Renderer,
    center: tuple[int, int],
    r: int,
    color: Optional[sdl2.ext.Color] = None
):
    # Excerpted and transpiled from https://zingl.github.io/bresenham.c
    # /**
    #  * Bresenham Curve Rasterizing Algorithms
    #  * @author alois zingl
    #  * @version V20.15 april 2020
    #  * @copyright MIT open-source license software
    #  * @url https://github.com/zingl/Bresenham
    #  * @author  Zingl Alois
    # */
    xm, ym = center
    # II. quadrant from bottom left to top right
    x, y = r, 0
    # error of 1.step
    err = 2 - 2 * r
    res = 1 - err
    while 1:
        i = abs(err + 2 * (x + y) - 2) / res  # get blend value of pixel
        renderer.draw_point(
            (
                (xm + x, ym - y),  # I. Quadrant
                (xm + y, ym + x),  # II. Quadrant
                (xm - x, ym + y),  # III. Quadrant
                (xm - y, ym - x)   # IV. Quadrant
            ),
            aacolor(color or renderer.color, 1 - i)
        )
        if x == 0:
            break
        e2, x2 = err, x  # remember values
        if err > y: # x step
            i = (err + 2 * x - 1) / res  # outward pixel
            if (i < 1):
                renderer.draw_point(
                    (
                        (xm + x, ym - y + 1),
                        (xm + y - 1, ym + x),
                        (xm - x, ym + y - 1),
                        (xm - y + 1, ym - x)
                    ),
                    aacolor(color or renderer.color, 1 - i)
                )
            x -= 1
            err -= x * 2 - 1
        x2 -= 1
        if e2 <= x2 :  # y step
            i = (1 - 2 * y - e2) / res  # inward pixel
            if i < 1:
                renderer.draw_point(
                    (
                        (xm + x2, ym - y),
                        (xm + y, ym + x2),
                        (xm - x2, ym + y),
                        (xm - y, ym - x2)
                    ),
                    aacolor(color or renderer.color, 1 - i)
                )
            y -= 1
            err -= y * 2 - 1


def render_circle_aa_fast(
    renderer: sdl2.ext.Renderer,
    center: tuple[int, int],
    r: int,
    color: Optional[sdl2.ext.Color] = None
):
    d = 2 * r
    x, y = r - 1, 0
    cx, cy = center
    err = 2 - d
    res = d - 1

    while x >= y:
        i = abs(err + 2 * (x + y) - 2) / res  # get blend value of pixel
        if abs(abs(x) - abs(y)) < r / 2:
            i /= 1.8
        if i < 1:
            points = (
                (cx + x, cy - y),
                (cx + x, cy + y),
                (cx - x, cy - y),
                (cx - x, cy + y),
                (cx + y, cy - x),
                (cx + y, cy + x),
                (cx - y, cy - x),
                (cx - y, cy + x),
            )
            renderer.draw_point(points, aacolor(color or renderer.color, 1 - i))
        # renderer.draw_point(points, color)

        e2, y2 = err, y
        if err <= 0:
            i = abs(2 - 2 * y - err) / res * 1.1  # inward pixel
            x_ = x - 1
            if i < 1:
                renderer.draw_point(
                    (
                        (cx + x_, cy - y),
                        (cx + x_, cy + y),
                        (cx - x_, cy - y),
                        (cx - x_, cy + y),
                        (cx + y, cy - x_),
                        (cx + y, cy + x_),
                        (cx - y, cy - x_),
                        (cx - y, cy + x_),
                    ),
                    aacolor(color or renderer.color, 1 - i)
                )
            y += 1
            # err += ty
            # ty += 2
            err += y * 2 - 1

        if e2 > 0:
            i = (e2 + 2 * x - 1) / res  # outward pixel
            y_ = y2 - 1
            if i < 1:
                renderer.draw_point(
                    (
                        (cx + x, cy - y_),
                        (cx + x, cy + y_),
                        (cx - x, cy - y_),
                        (cx - x, cy + y_),
                        (cx + y_, cy - x),
                        (cx + y_, cy + x),
                        (cx - y_, cy - x),
                        (cx - y_, cy + x),
                    ),
                    aacolor(color or renderer.color, 1 - i)
                )
            x -= 1
            # tx += 2
            # err += (tx - d)
            err -= x * 2 - 1