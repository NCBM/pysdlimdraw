from ctypes import c_int
from typing import Optional, Sequence

import sdl2
import sdl2.ext


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