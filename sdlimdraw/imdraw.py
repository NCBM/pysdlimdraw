from abc import ABC, abstractmethod
from contextlib import contextmanager
from ctypes import create_string_buffer
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Sequence, Union, overload

import sdl2
import sdl2.ext

from sdlimdraw.sdlext import (
    render_circle,
    render_circle_aa,
    render_circle_aa_fast,
    render_geometry,
)

from .imfile import ImageFormat, load_pil_image, save_surface

if TYPE_CHECKING:
    from PIL.Image import Image as PILImage


class BaseImDraw(ABC):
    renderer: sdl2.ext.Renderer
    width: int
    height: int

    @abstractmethod
    def __init__(self, root, width: int, height: int):
        raise NotImplementedError

    @overload
    @abstractmethod
    def save(
        self, filename: Union[str, Path],
        format_: Literal[ImageFormat.JPG],
        overwrite: bool = False,
        *,
        jpg_quality: int = 90
    ):
        ...
    
    @overload
    @abstractmethod
    def save(
        self, filename: Union[str, Path],
        format_: Literal[ImageFormat.PNG, ImageFormat.BMP] = ImageFormat.PNG,
        overwrite: bool = False
    ):
        ...

    @abstractmethod
    def save(
        self, filename: Union[str, Path],
        format_: ImageFormat = ImageFormat.PNG,
        overwrite: bool = False,
        *,
        jpg_quality: int = 90
    ):
        raise NotImplementedError

    def present(self):
        self.renderer.present()
        return self

    def setcolor(self, color: sdl2.ext.Color):
        self.renderer.color = color
        return self

    def line(
        self, *points: tuple[float, float], color: Optional[sdl2.ext.Color] = None
    ):
        if points:
            self.renderer.draw_line(points, color)
        return self

    def point(
        self, *points: tuple[float, float], color: Optional[sdl2.ext.Color] = None
    ):
        if points:
            self.renderer.draw_point(points, color)
        return self

    def rect(
        self,
        *rects: tuple[float, float, float, float],
        color: Optional[sdl2.ext.Color] = None
    ):
        if not rects:
            rects = ((0, 0, self.width, self.height),)
        self.renderer.draw_rect(rects, color)
        return self

    def fill(
        self,
        *rects: tuple[float, float, float, float],
        color: Optional[sdl2.ext.Color] = None
    ):
        if not rects:
            rects = ((0, 0, self.width, self.height),)
        self.renderer.fill(rects, color)
        return self

    def geometry(
        self,
        tex: sdl2.ext.Texture,
        *verts: sdl2.SDL_Vertex,
        indices: Optional[Sequence[int]] = None
    ):
        render_geometry(self.renderer, tex, *verts, indices=indices)
        return self

    def circle(
        self,
        center: tuple[int, int],
        r: int,
        color: Optional[sdl2.ext.Color] = None,
        aa: Literal["no", "fast", "fancy"] = "no"
    ):
        if aa == "no":
            render_circle(self.renderer, center, r, color)
        elif aa == "fast":
            render_circle_aa_fast(self.renderer, center, r, color)
        elif aa == "fancy":
            render_circle_aa(self.renderer, center, r, color)
        else:
            raise ValueError("anti-aliasing mode can only be set 'no', 'fast' or 'fancy'.")
        return self


class SoftwareImDraw(BaseImDraw):
    if TYPE_CHECKING:
        from ctypes import _Pointer
        surface: _Pointer[sdl2.SDL_Surface]

    def __init__(self, root, width: int, height: int) -> None:
        self.surface = root
        self.renderer = sdl2.ext.Renderer(root)
        self.width = width
        self.height = height

    def __del__(self):
        sdl2.SDL_FreeSurface(self.surface)

    @classmethod
    def new(
        cls, width: int, height: int, depth: int = 32,
        Rmask: int = 0, Gmask: int = 0, Bmask: int = 0, Amask: int = 0
    ):
        return cls(
            sdl2.SDL_CreateRGBSurface(
                0, width, height, depth, Rmask, Gmask, Bmask, Amask
            ),
            width, height
        )

    @classmethod
    def from_pil_image(cls, img: "PILImage"):
        return cls(load_pil_image(img), img.width, img.height)
    
    def save(
        self, filename: Union[str, Path],
        format_: ImageFormat = ImageFormat.PNG,
        overwrite: bool = False,
        *,
        jpg_quality: int = 90
    ):
        save_surface(
            self.surface, filename, format_, overwrite, jpg_quality=jpg_quality
        )


class WindowImDraw(BaseImDraw):
    def __init__(self, root: sdl2.ext.Window, width: int, height: int):
        self.window = root
        self.renderer = sdl2.ext.Renderer(root)
        self.width = width
        self.height = height

    @classmethod
    def new(
        cls, width: int, height: int,
        *,
        flags: int = sdl2.SDL_WINDOW_HIDDEN | sdl2.SDL_WINDOW_BORDERLESS
    ):
        return cls(
            sdl2.ext.Window("sdlimdraw", (width, height), flags=flags),
            width, height
        )

    @classmethod
    def from_pil_image(cls, img: "PILImage"):
        imd = cls.new(img.width, img.height)
        surf = sdl2.ext.pillow_to_surface(img)
        tex = sdl2.ext.Texture(imd.renderer, surf)
        imd.renderer.copy(tex)
        sdl2.SDL_FreeSurface(surf)
        return imd

    @contextmanager
    def copy_surface(self):
        w, h = self.window.size
        assert isinstance(w, int) and isinstance(h, int)
        pitch = sdl2.SDL_BYTESPERPIXEL(sdl2.SDL_PIXELFORMAT_ARGB8888) * w
        pixels = create_string_buffer(pitch * h)
        sdl2.SDL_RenderReadPixels(
            self.renderer.sdlrenderer,
            None,
            sdl2.SDL_PIXELFORMAT_ARGB8888,
            pixels,
            pitch
        )
        surf = sdl2.SDL_CreateRGBSurfaceWithFormatFrom(
            pixels, w, h, 32, pitch, sdl2.SDL_PIXELFORMAT_ARGB8888
        )
        yield surf
        sdl2.SDL_FreeSurface(surf)
        del pixels

    def save(
        self, filename: Union[str, Path],
        format_: ImageFormat = ImageFormat.PNG,
        overwrite: bool = False,
        *,
        jpg_quality: int = 90
    ):
        with self.copy_surface() as surf:
            save_surface(
                surf, filename, format_, overwrite, jpg_quality=jpg_quality
            )
