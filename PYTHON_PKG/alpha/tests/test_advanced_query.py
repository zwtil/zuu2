import pytest
from src.zuu.common.advancedQuery import DefaultQuery, QueryModel, AdvancedQuery

@pytest.fixture
def sample_data():
    return [
        {"id": "1", "name": "test_item"},
        {"id": 2, "name": "another_item"},
        {"id": "3", "name": "test_something"},
        {"id": 4, "name": "completely_different"},
    ]

def test_id_matching(sample_data):
    # Test integer ID
    result = DefaultQuery.match(2, sample_data)
    assert len(result) == 1
    assert result[0]["id"] == 2

    # Test string ID
    result = DefaultQuery.match("1", sample_data)
    assert len(result) == 1
    assert result[0]["id"] == "1"

def test_name_exact_match(sample_data):
    result = DefaultQuery.match("test_item", sample_data)
    assert len(result) == 1
    assert result[0]["name"] == "test_item"

def test_regex_name_matching(sample_data):
    # Test wildcard matching
    result = DefaultQuery.match("test_*", sample_data)
    assert len(result) == 2
    assert all("test_" in item["name"] for item in result)

    # Test alphanumeric exact matching
    result = DefaultQuery.match("test_item", sample_data)
    assert len(result) == 1
    assert result[0]["name"] == "test_item"

def test_eval_query(sample_data):
    # Test evaluation query
    result = DefaultQuery.match('?x["name"].startswith("test")', sample_data)
    assert len(result) == 2
    assert all(item["name"].startswith("test") for item in result)

def test_or_query(sample_data):
    # Test OR query with multiple conditions
    result = DefaultQuery.match(["test_item", 2], sample_data)
    assert len(result) == 2
    assert any(item["name"] == "test_item" for item in result)
    assert any(item["id"] == 2 for item in result)

def test_and_query(sample_data):
    # Test AND query
    result = DefaultQuery.match(('?x["name"].startswith("test")', '?x["name"].endswith("item")'), sample_data)
    assert len(result) == 1
    assert result[0]["name"] == "test_item"

def test_custom_query_model():
    # Test creating a custom query model
    custom_query = AdvancedQuery()
    
    @QueryModel.fromFunc(queryMatch=int)
    def custom_matcher(obj, query, original_obj):
        return [original_obj] if isinstance(obj, dict) and obj.get("value") == query else []

    custom_query.models.append(custom_matcher)
    
    test_data = [{"value": 42}, {"value": 24}]
    result = custom_query.match(42, test_data)
    assert len(result) == 1
    assert result[0]["value"] == 42

def test_invalid_queries(sample_data):
    # Test with invalid query types
    result = DefaultQuery.match(None, sample_data)
    assert len(result) == 0

    result = DefaultQuery.match({}, sample_data)
    assert len(result) == 0

def test_empty_data():
    # Test with empty data set
    result = DefaultQuery.match("test", [])
    assert len(result) == 0 