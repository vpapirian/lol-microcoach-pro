from microcoach.compare import compare_to_baseline

def test_compare_has_percentile():
    r = compare_to_baseline(10, 8, 2, tier="Gold")
    assert r.z is not None
    assert r.percentile_approx is not None
    assert 0 <= r.percentile_approx <= 100
