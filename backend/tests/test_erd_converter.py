import pytest
import os
from app.converters.erd_converter import parse_erd

@pytest.fixture
def sample_erd_file(tmp_path):
    data = """<?xml version="1.0"?>
    <er-diagram>
        <entity name="User">
            <attribute name="id" type="int" primary="true"/>
            <attribute name="name" type="string"/>
        </entity>
    </er-diagram>"""
    path = tmp_path / "test.erd"
    path.write_text(data)
    return str(path)

def test_erd_converter_returns_list(sample_erd_file):
    result = parse_erd(sample_erd_file)
    assert isinstance(result, list)
    assert len(result) > 0

def test_erd_converter_contains_table_name(sample_erd_file):
    result = parse_erd(sample_erd_file)
    assert "User" in result[0]

def test_erd_converter_handles_invalid_file():
    result = parse_erd("nonexistent.erd")
    assert "Ошибка" in result[0]