from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_meta_filters_structure():
    resp = client.get("/api/v1/meta/filters")
    assert resp.status_code == 200

    data = resp.json()
    expected_keys = {
        "conditions",
        "treatments",
        "sample_types",
        "time_from_treatment_start",
        "responses",
        "sexes",
    }

    assert set(data.keys()) == expected_keys

def test_meta_filters_no_empty_or_null_strings():
    resp = client.get("/api/v1/meta/filters")
    data = resp.json()

    for key in ["conditions", "treatments", "sample_types", "responses", "sexes"]:
        for v in data[key]:
            assert isinstance(v, str)
            assert v.strip() != ""

def test_meta_filters_sorted():
    resp = client.get("/api/v1/meta/filters")
    data = resp.json()

    assert data["conditions"] == sorted(data["conditions"], key=str.lower)
    assert data["treatments"] == sorted(data["treatments"], key=str.lower)
    assert data["sample_types"] == sorted(data["sample_types"], key=str.lower)

    # response ordering is explicit in SQL
    assert data["responses"] == sorted(data["responses"])

def test_meta_filters_timepoints_are_sorted_ints():
    resp = client.get("/api/v1/meta/filters")
    data = resp.json()

    tps = data["time_from_treatment_start"]

    assert all(isinstance(v, int) for v in tps)
    assert tps == sorted(tps)