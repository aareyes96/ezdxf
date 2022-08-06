#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Tuple
import sys
import enum
import itertools
import math
from ezdxf.math import Vec3, Vec2, Matrix44, AbstractBoundingBox, AnyVec
from ezdxf.path import Path
from ezdxf.render import hatching
from ezdxf.addons.drawing.backend import Backend, prepare_string_for_rendering
from ezdxf.addons.drawing.properties import Properties
from ezdxf.addons.drawing.type_hints import Color

from ezdxf.tools.fonts import FontFace, FontMeasurements, MonospaceFont
from .config import Configuration

try:
    from PIL import Image, ImageDraw
except ImportError:
    # The original PIL package does not work with Python3!
    print(
        "require Pillow package not found, install by:\n\n"
        "    pip install Pillow"
    )
    sys.exit(1)

# reuse the TextRenderer() from the matplotlib backend to create TextPath()
# objects
from matplotlib.font_manager import FontProperties
from .matplotlib import TextRenderer

INCH_TO_MM = 25.6


class TextMode(enum.IntEnum):
    PLACEHOLDER = 0
    OUTLINE = 1
    FILLED = 2


class PillowBackend(Backend):
    def __init__(
        self,
        region: AbstractBoundingBox,
        image_size: Tuple[int, int] = None,
        resolution: float = 1.0,
        margin: int = 10,
        dpi: int = 300,
        oversampling: int = 1,
        text_mode=TextMode.FILLED,

    ):
        """Backend which uses `Pillow` for image export.

        For linetype support configure the line_policy in the frontend as
        ACCURATE.

        Current limitations:

            - holes in hatches are not supported

        Args:
            region: output region of the layout in DXF drawing units
            image_size: image output size in pixels or ``None`` to be
                calculated by the region size and the `resolution`
            margin: image margin in pixels, same margin for all four borders
            resolution: pixels per DXF drawing unit, e.g. a resolution of 100
                for the drawing unit "meter" means, each pixel represents an
                area of 1cm x 1cm (1m is 100cm).
                If the `image_size` is given the `resolution` is calculated
                automatically
            dpi: output image resolution in dots per inch. The pixel width of
                lines is determined by the DXF lineweight (in mm) and this image
                resolution (dots/pixels per inch). The line width is independent
                of the drawing scale!
            oversampling: multiplier of the final image size to define the
                render canvas size (e.g. 1, 2, 3, ...), the final image will
                be scaled down by the LANCZOS method
            text_mode: set text rendering mode
                - PLACEHOLDER draws text as filled rectangles
                - OUTLINE draws text as outlines
                - FILLED draws text fillings

        """
        super().__init__()
        self.region = Vec2(region.size)
        if self.region.x <= 0.0 or self.region.y <= 0.0:
            raise ValueError("drawing region is empty")
        self.extmin = Vec2(region.extmin)
        self.margin_x = float(margin)
        self.margin_y = float(margin)
        self.dpi = int(dpi)
        self.oversampling = max(int(oversampling), 1)
        self.text_mode = text_mode
        # The lineweight is stored im mm,
        # line_pixel_factor * lineweight is the width in pixels
        self.line_pixel_factor = self.dpi / INCH_TO_MM  # pixel per mm
        # resolution: pixels per DXF drawing units, same resolution in all
        # directions
        self.resolution = float(resolution)
        if image_size is None:
            image_size = (
                math.ceil(self.region.x * resolution + 2.0 * self.margin_x),
                math.ceil(self.region.y * resolution + 2.0 * self.margin_y),
            )
        else:
            img_x, img_y = image_size
            if img_y < 1:
                raise ValueError(f"invalid image size: {image_size}")
            img_ratio = img_x / img_y
            region_ratio = self.region.x / self.region.y
            if img_ratio >= region_ratio:  # image fills the height
                self.resolution = (img_y - 2.0 * self.margin_y) / self.region.y
                self.margin_x = (img_x - self.resolution * self.region.x) * 0.5
            else:  # image fills the width
                self.resolution = (img_x - 2.0 * self.margin_x) / self.region.x
                self.margin_y = (img_y - self.resolution * self.region.y) * 0.5

        self.image_size = Vec2(image_size)
        self.bg_color: Color = "#000000"
        self.image_mode = "RGBA"
        self.text_renderer = TextRenderer(FontProperties(), True)

        # dummy values for declaration, both are set in clear()
        self.image = Image.new("RGBA", (10, 10))
        self.draw = ImageDraw.Draw(self.image)

    def configure(self, config: Configuration) -> None:
        super().configure(config)
        self.line_pixel_factor *= self.config.lineweight_scaling
        # set max flattening distance for Path() objects to 1 pixel
        one_px = 1.0 / self.resolution
        self.config = self.config.with_changes(max_flattening_distance=one_px)

    # noinspection PyTypeChecker
    def clear(self):
        x = int(self.image_size.x) * self.oversampling
        y = int(self.image_size.y) * self.oversampling
        self.image = Image.new(self.image_mode, (x, y), color=self.bg_color)
        self.draw = ImageDraw.Draw(self.image)

    def set_background(self, color: Color) -> None:
        self.bg_color = color
        self.clear()

    def width(self, lineweight: float) -> int:
        return max(int(lineweight * self.line_pixel_factor), 1)

    def pixel_loc(self, point: AnyVec) -> Tuple[float, float]:
        # Source: https://pillow.readthedocs.io/en/stable/handbook/concepts.html#coordinate-system
        # The Python Imaging Library uses a Cartesian pixel coordinate system,
        # with (0,0) in the upper left corner. Note that the coordinates refer
        # to the implied pixel corners; the centre of a pixel addressed as
        # (0, 0) actually lies at (0.5, 0.5).
        x = (point.x - self.extmin.x) * self.resolution + self.margin_x
        y = (point.y - self.extmin.y) * self.resolution + self.margin_y
        return (
            x * self.oversampling,
            # (0, 0) is the top-left corner:
            (self.image_size.y - y) * self.oversampling,
        )

    def draw_point(self, pos: Vec3, properties: Properties) -> None:
        self.draw.point([self.pixel_loc(pos)], fill=properties.color)

    def draw_line(self, start: Vec3, end: Vec3, properties: Properties) -> None:
        self.draw.line(
            [self.pixel_loc(start), self.pixel_loc(end)],
            fill=properties.color,
            width=self.width(properties.lineweight),
        )

    def draw_filled_polygon(
        self, points: Iterable[Vec3], properties: Properties
    ) -> None:
        points = [self.pixel_loc(p) for p in points]
        if len(points) > 2:
            self.draw.polygon(
                points,
                fill=properties.color,
                outline=properties.color,
            )

    def draw_filled_paths(
        self,
        paths: Iterable[Path],
        holes: Iterable[Path],
        properties: Properties,
    ) -> None:
        # Use the HatchBaseLine class to draw solid lines with an offset of one
        # pixel.
        one_px = 1.0 / (self.resolution * self.oversampling)
        baseline = hatching.HatchBaseLine(
            Vec2(0, 0), Vec2(1, 0), Vec2(0, one_px)
        )
        polygons = [
            Vec2.list(p.flattening(one_px))
            for p in itertools.chain(paths, holes)
        ]
        color = properties.color
        for line in hatching.hatch_polygons(baseline, polygons):
            self.draw.line(
                [self.pixel_loc(line.start), self.pixel_loc(line.end)],
                fill=color,
                width=1,
            )

    def draw_text(
        self,
        text: str,
        transform: Matrix44,
        properties: Properties,
        cap_height: float,
    ) -> None:
        if self.text_mode == TextMode.PLACEHOLDER:
            # draws a placeholder rectangle as text
            width = self.get_text_line_width(text, cap_height, properties.font)
            height = cap_height
            points = Vec3.list(
                [(0, 0), (width, 0), (width, height), (0, height)]
            )
            points = list(transform.transform_vertices(points))
            self.draw_filled_polygon(points, properties)
            return

        tr = self.text_renderer
        text = self._prepare_text(text)
        font_properties = tr.get_font_properties(properties.font)
        scale = tr.get_scale(cap_height, font_properties)
        m = Matrix44.scale(scale) @ transform
        if self.text_mode == TextMode.OUTLINE:
            ezdxf_path = tr.get_ezdxf_path(text, font_properties)
            if len(ezdxf_path) == 0:
                return
            ezdxf_path = ezdxf_path.transform(m)
            for path in ezdxf_path.sub_paths():
                self.draw_path(path, properties)
        else:  # render Text as filled polygons
            ezdxf_path = tr.get_ezdxf_path(text, font_properties)
            if len(ezdxf_path) == 0:
                return
            self.draw_filled_paths(
                (p for p in ezdxf_path.transform(m).sub_paths()), [], properties
            )

    def get_font_measurements(
        self, cap_height: float, font: FontFace = None
    ) -> FontMeasurements:
        if self.text_mode == TextMode.PLACEHOLDER:
            return MonospaceFont(cap_height).measurements
        return self.text_renderer.get_font_measurements(
            self.text_renderer.get_font_properties(font)
        ).scale_from_baseline(desired_cap_height=cap_height)

    def _prepare_text(self, text: str) -> str:
        dxftype = (
            self.current_entity.dxftype() if self.current_entity else "TEXT"
        )
        return prepare_string_for_rendering(text, dxftype)

    def get_text_line_width(
        self, text: str, cap_height: float, font: FontFace = None
    ) -> float:
        if not text.strip():
            return 0.0
        text = self._prepare_text(text)
        if self.text_mode == TextMode.PLACEHOLDER:
            return MonospaceFont(cap_height).text_width(text) * 0.8
        return self.text_renderer.get_text_line_width(text, cap_height, font)

    def export(self, filename: str, **kwargs) -> None:
        image = self.resize()
        if not supports_transparency(filename):
            # remove alpha channel if not supported
            image = image.convert("RGB")
        dpi = kwargs.pop("dpi", self.dpi)
        image.save(filename, dpi=(dpi, dpi), **kwargs)

    def resize(self):
        image = self.image
        if self.oversampling > 1:
            x = int(self.image_size.x)
            y = int(self.image_size.y)
            image = self.image.resize((x, y), resample=Image.LANCZOS)
        return image


SUPPORT_TRANSPARENCY = [".png", ".tif", ".tiff"]


def supports_transparency(filename: str) -> bool:
    filename = filename.lower()
    return any(filename.endswith(ftype) for ftype in SUPPORT_TRANSPARENCY)
