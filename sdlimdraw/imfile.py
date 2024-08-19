import os
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Union

import sdl2
import sdl2.ext
from sdl2 import sdlimage
from sdl2.ext import load_img as load_img

if TYPE_CHECKING:
    from PIL.Image import Image as PILImage

# ENCODING = locale.getpreferredencoding(False)
ENCODING = "utf-8"


class ImageFormat(Enum):
    JPG = auto()
    PNG = auto()
    BMP = auto()


def load_svg(
    path: Union[str, Path], width: int = 0, height: int = 0, as_argb: bool = True
):
    return sdl2.ext.load_svg(str(path), width, height, as_argb)


def load_texture(renderer: sdl2.ext.Renderer, filename: Union[str, Path]):
    return sdlimage.IMG_LoadTexture(renderer.sdlrenderer, str(filename).encode(ENCODING))


def load_pil_image(img: "PILImage", as_argb: bool = True):
    return sdl2.ext.pillow_to_surface(img, as_argb)


def save_surface(
    surf,
    filename: Union[str, Path],
    format_: ImageFormat = ImageFormat.PNG,
    overwrite: bool = False,
    *,
    jpg_quality: int = 90
):
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
