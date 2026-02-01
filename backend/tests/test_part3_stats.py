from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_part3_stats_structure():
    resp = client.get("/api/v1/part3/stats")
    assert resp.status_code == 200

    stats = resp.json()
    assert isinstance(stats, list)
    assert len(stats) > 0

    row = stats[0]
    expected_keys = {
        "population",
        "n_yes",
        "n_no",
        "median_yes",
        "median_no",
        "p_value",
        "q_value",
        "significant_fdr_0_05",
    }

    assert expected_keys.issubset(row.keys())

def test_part3_stats_numeric_sanity():
    resp = client.get("/api/v1/part3/stats")
    assert resp.status_code == 200

    stats = resp.json()
    assert len(stats) > 0

    prev_q = 0.0

    for row in stats:
        # sample counts
        assert row["n_yes"] >= 0
        assert row["n_no"] >= 0
        assert row["n_yes"] + row["n_no"] > 0

        # medians are percentages
        assert 0.0 <= row["median_yes"] <= 100.0
        assert 0.0 <= row["median_no"] <= 100.0

        # p-values / q-values are valid probabilities
        assert 0.0 <= row["p_value"] <= 1.0
        assert 0.0 <= row["q_value"] <= 1.0

        # BH monotonicity (sorted by p-value)
        assert row["q_value"] >= prev_q
        prev_q = row["q_value"]

        # FDR flag consistency
        assert row["significant_fdr_0_05"] == (row["q_value"] < 0.05)
    
def test_part3_stats_significance_consistency():
    resp = client.get("/api/v1/part3/stats")
    assert resp.status_code == 200

    stats = resp.json()
    assert len(stats) > 0

    for row in stats:
        p_sig = row["p_value"] < 0.05
        q_sig = row["q_value"] < 0.05

        # q-significant implies p-significant
        assert not (q_sig and not p_sig), (
            f"Inconsistent significance for population {row['population']}: "
            f"p={row['p_value']}, q={row['q_value']}"
        )