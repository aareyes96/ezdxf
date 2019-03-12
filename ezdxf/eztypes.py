# Created: 11.12.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
"""
ezdxf typing collection

Only usable in type checking mode:

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFTag

"""
from typing import *

if TYPE_CHECKING:
    # Low level stuff
    from ezdxf.math.vector import Vector, Vec2
    from ezdxf.math.matrix44 import Matrix44
    from ezdxf.math.bbox import BoundingBox, BoundingBox2d
    from ezdxf.math.ucs import UCS
    from ezdxf.tools.handle import HandleGenerator
    from ezdxf.lldxf.types import DXFTag, DXFBinaryTag, DXFVertex
    from ezdxf.lldxf.attributes import XType, DXFAttr
    from ezdxf.lldxf.tags import Tags
    from ezdxf.lldxf.extendedtags import ExtendedTags
    from ezdxf.lldxf.tagwriter import TagWriter
    from ezdxf.tools.complex_ltype import ComplexLineTypePart

    # Entity factories
    from ezdxf.entities.factory import EntityFactory

    from ezdxf.layouts.base import BaseLayout
    from ezdxf.layouts.layout import Layout
    from ezdxf.layouts.blocklayout import BlockLayout

    # Entities manager
    from ezdxf.entitydb import EntitySpace
    from ezdxf.drawing import Drawing
    from ezdxf.entitydb import EntityDB

    # Sections and Tables
    from ezdxf.sections.table import Table, ViewportTable, LayerTable, StyleTable
    from ezdxf.sections.blocks import BlocksSection
    from ezdxf.sections.header import HeaderSection
    from ezdxf.sections.tables import TablesSection
    from ezdxf.sections.blocks import BlocksSection
    from ezdxf.sections.classes import ClassesSection
    from ezdxf.sections.objects import ObjectsSection
    from ezdxf.sections.entities import EntitySection
    from ezdxf.sections.unsupported import UnsupportedSection

    # Table entries
    from ezdxf.entities.blockrecord import BlockRecord
    from ezdxf.entities.layer import Layer
    from ezdxf.entities.ltype import Linetype
    from ezdxf.entities.dimstyle import DimStyle
    from ezdxf.entities.appid import AppID
    from ezdxf.entities.ucs import UCSTable
    from ezdxf.entities.view import View
    from ezdxf.entities.vport import VPort

    # Style Manager
    from ezdxf.entities.dxfgroups import GroupCollection
    from ezdxf.entities.material import MaterialCollection
    from ezdxf.entities.mleader import MLeaderStyleCollection
    from ezdxf.entities.mline import MLineStyleCollection
    from ezdxf.dimstyleoverride import DimStyleOverride

    # DXF objects
    from ezdxf.entities.dxfobj import DXFObject, AcDbPlaceholder, XRecord, VBAProject, SortEntsTable
    from ezdxf.entities.layout import DXFLayout
    from ezdxf.entities.dictionary import Dictionary, DictionaryWithDefault, DictionaryVar
    from ezdxf.entities.idbuffer import IDBuffer, FieldList, LayerFilter

    # DXF entities
    from ezdxf.entities.dxfentity import DXFEntity, DXFNamespace, DXFTagStorage
    from ezdxf.entities.dxfgfx import DXFGraphic
    from ezdxf.entities.line import Line
    from ezdxf.entities.point import Point
    from ezdxf.entities.circle import Circle
    from ezdxf.entities.arc import Arc
    from ezdxf.entities.shape import Shape
    from ezdxf.entities.solid import Solid, Trace, Face3d

    from ezdxf.entities.polyline import Polyline, Polyface, Polymesh, DXFVertex
    from ezdxf.entities.insert import Insert
    from ezdxf.entities.attrib import Attdef, Attrib
    from ezdxf.entities.dimension import Dimension
    from ezdxf.entities.text import Text
    from ezdxf.entities.viewport import Viewport
    from ezdxf.entities.block import Block, EndBlk
    from ezdxf.entities.lwpolyline import LWPolyline
    from ezdxf.entities.ellipse import Ellipse
    from ezdxf.entities.xline import XLine, Ray
    from ezdxf.entities.mtext import MText
    from ezdxf.entities.spline import Spline
    from ezdxf.entities.mesh import Mesh
    from ezdxf.entities.hatch import Hatch
    from ezdxf.entities.image import Image, ImageDef, ImageDefReactor, RasterVariables
    from ezdxf.entities.underlay import PdfUnderlay, DwfUnderlay, DgnUnderlay, Underlay
    from ezdxf.entities.underlay import PdfDefinition, DwfDefinition, DgnDefinition, UnderlayDef
    from ezdxf.entities.acis import Body, Region, Solid3d
    from ezdxf.entities.acis import Surface, ExtrudedSurface, LoftedSurface, RevolvedSurface, SweptSurface
    from ezdxf.entities.sun import Sun
    from ezdxf.entities.geodata import GeoData
    from ezdxf.entities.light import Light
    from ezdxf.entities.leader import Leader
    from ezdxf.render.dimension import BaseDimensionRenderer

    # other
    from ezdxf.audit import Auditor
    from ezdxf.lldxf.tags import DXFInfo

    # Type compositions
    Vertex = Union[Sequence[float], Vector, Vec2]
    VecXY = Union[Vec2, Vector]  # Vector with x and y attributes
    TagValue = Union[str, int, float, Sequence[float], Vector]
    RGB = Tuple[int, int, int]
    IterableTags = Iterable[Tuple[int, TagValue]]
    SectionDict = Dict[str, List[Union[Tags, ExtendedTags]]]
    KeyFunc = Callable[['DXFEntity'], Hashable]
    FaceType = Sequence[Vertex]

    # Type Unions
    GenericLayoutType = Union[Layout, BlockLayout]
    SectionType = Union[
        HeaderSection, TablesSection, BlocksSection, ClassesSection, ObjectsSection, EntitySection, UnsupportedSection]
