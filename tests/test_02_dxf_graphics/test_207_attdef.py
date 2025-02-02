# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.entities.attrib import AttDef
from ezdxf.lldxf import const
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text


TEST_CLASS = AttDef
TEST_TYPE = "ATTDEF"

ENTITY_R12 = """0
ATTDEF
5
0
8
0
10
0.0
20
0.0
30
0.0
40
1.0
1
DEFAULTTEXT
50
0.0
51
0.0
7
STANDARD
41
1.0
71
0
72
0
11
0.0
21
0.0
31
0.0
3
PROMPTTEXT
2
TAG
70
0
74
0
"""

ENTITY_R2000 = """0
ATTDEF
5
0
330
0
100
AcDbEntity
8
0
100
AcDbText
10
0.0
20
0.0
30
0.0
40
1.0
1
DEFAULTTEXT
50
0.0
51
0.0
7
STANDARD
41
1.0
71
0
72
0
11
0.0
21
0.0
31
0.0
100
AcDbAttributeDefinition
3
PROMPTTEXT
2
TAG
70
0
73
0
74
0
"""


@pytest.fixture(params=[ENTITY_R12, ENTITY_R2000])
def entity(request):
    return TEST_CLASS.from_text(request.param)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES

    assert TEST_TYPE in ENTITY_CLASSES


def test_default_init():
    entity = TEST_CLASS()
    assert entity.dxftype() == TEST_TYPE


def test_default_new():
    entity = TEST_CLASS.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "insert": (1, 2, 3),
        },
    )
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == "BYLAYER"
    assert entity.dxf.insert == (1, 2, 3)
    assert entity.dxf.insert.x == 1, "is not Vec3 compatible"
    assert entity.dxf.insert.y == 2, "is not Vec3 compatible"
    assert entity.dxf.insert.z == 3, "is not Vec3 compatible"
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1
    assert entity.dxf.extrusion == (0.0, 0.0, 1.0)
    assert entity.dxf.hasattr("extrusion") is False, "just the default value"


def test_load_from_text(entity):
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 256, "default color is 256 (by layer)"
    assert entity.dxf.insert == (0, 0, 0)


@pytest.mark.parametrize(
    "txt,ver", [(ENTITY_R2000, const.DXF2000), (ENTITY_R12, const.DXF12)]
)
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    attdef = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    attdef.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    attdef.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


class TestEmbeddedMTextSupport:
    @pytest.fixture
    def attdef(self) -> AttDef:
        return AttDef.from_text(EMBEDDED_MTEXT)

    def test_has_embedded_mtext(self, attdef):
        assert attdef.has_embedded_mtext_entity is True

    def test_get_plain_mtext(self, attdef):
        assert attdef.plain_mtext() == "TEST VENUE\nTEST FLOOR PLAN"

    def test_get_virtual_mtext_entity(self, attdef):
        mtext = attdef.virtual_mtext_entity()
        assert mtext.plain_text() == "TEST VENUE\nTEST FLOOR PLAN"

    def test_attdef_graphic_attributes(self, attdef):
        assert attdef.dxf.color == 7
        assert attdef.dxf.layer == "AttribLayer"

    def test_mtext_graphic_attdefutes_inherited_from_host(self, attdef):
        mtext = attdef.virtual_mtext_entity()
        assert mtext.dxf.color == 7
        assert mtext.dxf.layer == "AttribLayer"

    def test_mtext_entity_attributes(self, attdef):
        mtext = attdef.virtual_mtext_entity()
        # These seems to be the required DXF tag for the embedded MTEXT entity:
        assert mtext.dxf.insert.isclose((45.3, 45.0, 0))
        assert mtext.dxf.char_height == 3.0
        assert mtext.dxf.width == 0
        assert mtext.dxf.defined_height == 0
        assert mtext.dxf.attachment_point == 5
        assert mtext.dxf.flow_direction == 5
        assert mtext.dxf.style == "Arial_3 NARROW"
        assert mtext.dxf.line_spacing_style == 1
        assert mtext.dxf.line_spacing_factor == 1.0

    def test_dxf_export_matches_test_data(self, attdef):
        result = TagCollector.dxftags(attdef, dxfversion=const.DXF2018)
        expected = basic_tags_from_text(EMBEDDED_MTEXT)
        assert result == expected


EMBEDDED_MTEXT = r"""  0
ATTDEF
5
28A
330
285
100
AcDbEntity
8
AttribLayer
62
7
100
AcDbText
10
45.3
20
43.5
30
0.0
40
3.0
1
TEST VENUE
7
Arial_3 NARROW
72
1
11
45.3
21
45.0
31
0.0
100
AcDbAttributeDefinition
280
0
3
TITLE-OF-DRAWING
2
DRAWING-NAME
70
0
74
2
280
0
71
4
72
0
11
45.3
21
45.0
31
0.0
101
Embedded Object
10
45.3
20
45.0
30
0.0
40
3.0
41
0.0
46
0.0
71
5
72
5
1
TEST VENUE\PTEST FLOOR PLAN
7
Arial_3 NARROW
73
1
44
1.0
1001
AcadAnnotative
1000
AnnotativeData
1002
{
1070
1
1070
0
1002
}
"""
