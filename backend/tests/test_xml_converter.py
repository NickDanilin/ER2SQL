import pytest
from app.converters.xml_converter import parse_drawio_xml

@pytest.fixture
def sample_xml_file(tmp_path):
    data = """<mxfile><diagram><mxCell value="User[id:int]" style="shape=table"/></diagram></mxfile>"""
    path = tmp_path / "test.xml"
    path.write_text(data)
    return str(path)

def test_xml_converter_returns_list(sample_xml_file):
    result = parse_drawio_xml(sample_xml_file)
    assert isinstance(result, list)