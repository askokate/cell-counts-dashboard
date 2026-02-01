from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_part3_frequencies_structure():
    resp = client.get("/api/v1/part3/frequencies")
    assert resp.status_code == 200

    rows = resp.json()
    assert isinstance(rows, list)
    assert len(rows) > 0

    row = rows[0]
    expected_keys = {"sample", "response", "population", "percentage"}
    assert expected_keys.issubset(row.keys())

from collections import defaultdict

def test_part3_frequencies_sum_to_100_per_sample():
    resp = client.get("/api/v1/part3/frequencies")
    assert resp.status_code == 200

    rows = resp.json()
    assert len(rows) > 0

    by_sample = defaultdict(float)

    for r in rows:
        by_sample[r["sample"]] += r["percentage"]

    for sample, total in by_sample.items():
        assert abs(total - 100.0) <= 0.05, (
            f"Percentages for sample {sample} sum to {total}"
        )

def test_part3_frequencies_percentage_bounds():
    resp = client.get("/api/v1/part3/frequencies")
    rows = resp.json()

    for r in rows:
        assert 0.0 <= r["percentage"] <= 100.0