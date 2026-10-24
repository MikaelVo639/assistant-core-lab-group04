import pytest

from assistant_core.errors import InvalidRequest
from assistant_core.tools import parse_credits, tuition


def test_parse_credits_standard():
    credits, retake = parse_credits("tuition for 18 credits and 2 retake")
    assert credits == 18
    assert retake == 2


def test_parse_credits_only_normal():
    credits, retake = parse_credits("tuition for 15 credits")
    assert credits == 15
    assert retake == 0


def test_parse_credits_retake_first():
    credits, retake = parse_credits("tuition for 2 retake and 12 credits")
    assert credits == 12
    assert retake == 2


def test_parse_credits_single_number():
    credits, retake = parse_credits("tuition 20")
    assert credits == 20
    assert retake == 0


def test_parse_credits_vietnamese():
    credits, retake = parse_credits("học phí cho 16 tín chỉ và 3 học lại")
    assert credits == 16
    assert retake == 3


def test_parse_credits_with_punctuation():
    credits, retake = parse_credits("tuition for 18 credits, and 2 retakes?")
    assert credits == 18
    assert retake == 2


def test_parse_credits_missing_raises():
    with pytest.raises(InvalidRequest, match="How many credits?"):
        parse_credits("what is the tuition fee?")


def test_parse_credits_zero_raises():
    with pytest.raises(InvalidRequest, match="How many credits?"):
        parse_credits("tuition 0 credits")


def test_tuition_calculation_standard():
    total = tuition(18, 2, rate=450_000, retake_multiplier=1.5, max_credits=30)
    assert total == 9_450_000


def test_tuition_calculation_no_retake():
    total = tuition(15, 0, rate=450_000, retake_multiplier=1.5, max_credits=30)
    assert total == 6_750_000


def test_tuition_boundary_max_credits():
    total = tuition(30, 0, max_credits=30)
    assert total == 13_500_000


def test_tuition_exceeds_max_credits_raises():
    with pytest.raises(InvalidRequest, match="too many credits"):
        tuition(31, 0, max_credits=30)


def test_tuition_zero_credits_raises():
    with pytest.raises(InvalidRequest, match="How many credits?"):
        tuition(0, 0)


def test_tuition_negative_credits_raises():
    with pytest.raises(InvalidRequest, match="How many credits?"):
        tuition(-5, 0)


def test_tuition_negative_retake_raises():
    with pytest.raises(InvalidRequest, match="retake credits must be non-negative"):
        tuition(10, -2)


def test_tuition_invalid_rate_raises():
    with pytest.raises(InvalidRequest, match="credit rate must be positive"):
        tuition(10, 0, rate=0)


def test_tuition_custom_settings():
    total = tuition(10, 2, rate=500_000, retake_multiplier=2.0, max_credits=20)
    assert total == 7_000_000
