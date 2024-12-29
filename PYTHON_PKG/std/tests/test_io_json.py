import json
import pytest
import os
from zuu.io.json import Json

@pytest.fixture
def temp_json_file(tmp_path):
    file_path = tmp_path / "test.json"
    return str(file_path)

def test_dump_and_load_basic(temp_json_file):
    data = {"hello": "world", "number": 42}
    Json.dump(temp_json_file, data)
    loaded = Json.load(temp_json_file)
    assert loaded == data

def test_non_ascii_characters(temp_json_file):
    data = {
        "japanese": "こんにちは",
        "chinese": "你好",
        "emoji": "🌟🎉",
        "russian": "привет",
        "arabic": "مرحبا"
    }
    Json.dump(temp_json_file, data)
    loaded = Json.load(temp_json_file)
    assert loaded == data

def test_update(temp_json_file):
    initial = {"a": 1, "b": 2}
    Json.dump(temp_json_file, initial)
    
    update_data = {"b": 3, "c": 4}
    Json.update(temp_json_file, update_data)
    
    loaded = Json.load(temp_json_file)
    assert loaded == {"a": 1, "b": 3, "c": 4}

def test_append_list(temp_json_file):
    initial = [1, 2, 3]
    Json.dump(temp_json_file, initial)
    
    append_data = [4, 5]
    Json.append(temp_json_file, append_data)
    
    loaded = Json.load(temp_json_file)
    assert loaded == [1, 2, 3, 4, 5]

def test_append_dict(temp_json_file):
    initial = {"a": 1}
    Json.dump(temp_json_file, initial)
    
    append_data = {"b": 2}
    Json.append(temp_json_file, append_data)
    
    loaded = Json.load(temp_json_file)
    assert loaded == {"a": 1, "b": 2}

def test_touch_new_file(temp_json_file):
    default = {"initialized": True}
    Json.touch(temp_json_file, default)
    assert os.path.exists(temp_json_file)
    loaded = Json.load(temp_json_file)
    assert loaded == default

def test_touch_existing_file(temp_json_file):
    initial = {"existing": True}
    Json.dump(temp_json_file, initial)
    
    Json.touch(temp_json_file, {"should": "not override"})
    loaded = Json.load(temp_json_file)
    assert loaded == initial

def test_utf8_false(temp_json_file):
    data = {"japanese": "こんにちは"}
    Json.dump(temp_json_file, data, utf8=False)
    with open(temp_json_file, 'rb') as f:  # Open in binary mode
        content = f.read().decode('utf-8')
        assert any(ord(c) > 127 for c in content)  # Check for non-ASCII characters
    loaded = Json.load(temp_json_file)
    assert loaded == data

def test_invalid_json(temp_json_file):
    with open(temp_json_file, 'w', encoding='utf-8') as f:
        f.write('{"invalid": json')
    with pytest.raises(json.JSONDecodeError):
        Json.load(temp_json_file)

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        Json.load("nonexistent.json")

def test_ensure_ascii_in_kwargs(temp_json_file):
    with pytest.raises(AssertionError):
        Json.dump(temp_json_file, {}, ensure_ascii=True) 