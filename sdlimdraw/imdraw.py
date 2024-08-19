import locale
import os
from abc import ABC, abstractmethod
from contextlib import contextmanager
from ctypes import create_string_buffer
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Union, overload

import sdl2
import sdl2.ext
from sdl2 import sdlimage

if TYPE_CHECKING:
    from PIL.Image import Image as PILImage

ENCODING = locale.getpreferredencoding(False)


class ImageFormat(Enum):
    JPG = auto()
    PNG = auto()
    BMP = auto()


class BaseImDraw(ABC):
    renderer: sdl2.ext.Renderer

    @abstractmethod
    def __init__(self, root):
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
    
    @staticmethod
    def _save(
        filename: Union[str, Path],
        format_: ImageFormat = ImageFormat.PNG,
        overwrite: bool = False,
        *,
        jpg_quality: int = 90,
        _surface=None
    ):
        surf = _surface
        if os.path.exists(filename) and not overwrite:
            raise RuntimeError(
                f"file '{filename!s}' already exists. "
                "use overwrite=True if needed."
            )
        if format_ == ImageFormat.PNG:
            sdlimage.IMG_SavePNG(surf, str(filename).encode(ENCODING))
        elif format_ == ImageFormat.BMP:
            sdl2.SDL_SaveBMP(surf, str(filename).encode(ENCODING))
        elif format_ == ImageFormat.JPG:
            sdlimage.IMG_SaveJPG(
                surf, str(filename).encode(ENCODING), jpg_quality
            )


class SoftwareImDraw(BaseImDraw):
    if TYPE_CHECKING:
        from ctypes import _Pointer
        surface: _Pointer[sdl2.SDL_Surface]

    def __init__(self, root) -> None:
        self.surface = root
        self.renderer = sdl2.ext.Renderer(root)

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
            )
        )

    @classmethod
    def from_pil_image(cls, img: "PILImage"):
        return cls(sdl2.ext.pillow_to_surface(img))
    
    def save(
        self, filename: Union[str, Path],
        format_: ImageFormat = ImageFormat.PNG,
        overwrite: bool = False,
        *,
        jpg_quality: int = 90
    ):
        super()._save(filename, format_, overwrite, jpg_quality=jpg_quality, _surface=self.surface)


class WindowImDraw(BaseImDraw):
    def __init__(self, root: sdl2.ext.Window):
        self.window = root
        self.renderer = sdl2.ext.Renderer(root)

    @classmethod
    def new(cls, width: int, height: int):
        return cls(
            sdl2.ext.Window(
                "sdlimdraw", (width, height),
                flags=(
                    sdl2.SDL_WINDOW_HIDDEN | sdl2.SDL_WINDOW_BORDERLESS
                    | sdl2.SDL_WINDOW_OPENGL
                )
            )
        )

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
            super()._save(filename, format_, overwrite, jpg_quality=jpg_quality, _surface=surf)
