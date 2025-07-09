import pytest
from app.converters.graphml_converter import parse_graphml

@pytest.fixture
def sample_graphml_file(tmp_path):
    data = """<?xml version="1.0"?>
    <graphml>
        <node id="1">
            <data key="d1">User</data>
            <data key="d6">id:int\nname:string</data>
        </node>
    </graphml>"""
    path = tmp_path / "test.graphml"
    path.write_text(data)
    return str(path)

def test_graphml_converter_returns_list(sample_graphml_file):
    result = parse_graphml(sample_graphml_file)
    assert isinstance(result, list)

def test_graphml_converter_handles_empty_result():
    result = parse_graphml("nonexistent.graphml")
    assert isinstance(result, list)