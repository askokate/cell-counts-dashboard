from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_frequency_structure():
    resp = client.get("/api/v1/frequency")
    assert resp.status_code == 200

    rows = resp.json()
    assert isinstance(rows, list)
    assert len(rows) > 0

    row = rows[0]
    expected_keys = {
        "sample",
        "total_count",
        "population",
        "count",
        "percentage",
    }

    assert expected_keys.issubset(row.keys())

from collections import defaultdict

def test_frequency_counts_sum_to_total():
    resp = client.get("/api/v1/frequency")
    rows = resp.json()

    counts_by_sample = defaultdict(int)
    total_by_sample = {}

    for r in rows:
        sample = r["sample"]
        counts_by_sample[sample] += r["count"]
        total_by_sample[sample] = r["total_count"]

    for sample, summed in counts_by_sample.items():
        assert summed == total_by_sample[sample], (
            f"Counts for sample {sample} sum to {summed}, "
            f"but total_count is {total_by_sample[sample]}"
        )

from collections import defaultdict

def test_frequency_percentages_sum_to_100():
    resp = client.get("/api/v1/frequency")
    rows = resp.json()

    pct_by_sample = defaultdict(float)

    for r in rows:
        pct_by_sample[r["sample"]] += r["percentage"]

    for sample, total in pct_by_sample.items():
        assert abs(total - 100.0) <= 0.05, (
            f"Percentages for sample {sample} sum to {total}"
        )

def test_frequency_percentage_matches_count():
    resp = client.get("/api/v1/frequency")
    rows = resp.json()

    for r in rows:
        expected = round(100.0 * r["count"] / r["total_count"], 2)
        assert r["percentage"] == expected

def test_frequency_value_bounds():
    resp = client.get("/api/v1/frequency")
    rows = resp.json()

    for r in rows:
        assert r["total_count"] > 0
        assert r["count"] >= 0
        assert r["count"] <= r["total_count"]
        assert 0.0 <= r["percentage"] <= 100.0

def test_frequency_limit_respected():
    resp = client.get("/api/v1/frequency?limit=5")
    assert resp.status_code == 200

    rows = resp.json()
    assert len(rows) <= 5