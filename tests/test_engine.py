"""Automated tests for engine.py — no Streamlit imports, no network calls."""
import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from engine import (
    Household,
    HouseholdInput,
    LifelineStatus,
    ScreeningResult,
    screen,
    lifeline_income_limit,
    validate_household,
    LIFELINE_SOURCE,
    SNAP_SOURCE,
    SER_SOURCE,
)


# ---------------------------------------------------------------------------
# Threshold helpers
# ---------------------------------------------------------------------------

def test_thresholds_known_values():
    assert lifeline_income_limit(1) == 21546
    assert lifeline_income_limit(4) == 44550
    assert lifeline_income_limit(8) == 75222


def test_threshold_formula_sizes_1_to_20():
    """Income limit must equal 21546 + (size-1)*7668 for all sizes 1-20."""
    for size in range(1, 21):
        expected = 21546 + (size - 1) * 7668
        actual = lifeline_income_limit(size)
        assert actual == expected, (
            'size={}: expected {}, got {}'.format(size, expected, actual)
        )


def test_threshold_size_9_extrapolation():
    assert lifeline_income_limit(9) == 75222 + 7668  # == 82890


# ---------------------------------------------------------------------------
# Requirement 7 — ten required test scenarios
# ---------------------------------------------------------------------------

def test_income_at_threshold_qualifies():
    """R7.1 — income exactly at threshold -> LIKELY_QUALIFIES_INCOME."""
    h = Household('Michigan', 1, 21546)
    result = screen(h)[0]
    assert result.status == LifelineStatus.LIKELY_QUALIFIES_INCOME


def test_income_one_above_threshold():
    """R7.2 — income exactly $1 above threshold -> NOT_INDICATED."""
    h = Household('Michigan', 1, 21547)
    result = screen(h)[0]
    assert result.status == LifelineStatus.NOT_INDICATED


def test_size_zero_invalid():
    """R7.3 — household size 0 -> ValueError."""
    with pytest.raises(ValueError):
        screen(Household('Michigan', 0, 10000))


def test_size_negative_invalid():
    """R7.4 — household size -1 -> ValueError."""
    with pytest.raises(ValueError):
        screen(Household('Michigan', -1, 10000))


def test_non_integer_size_invalid():
    """R7.5 — non-integer size 2.5.
    Python dataclasses do not enforce field types at runtime, so Household(size=2.5)
    constructs without error. validate_household() must then catch it and raise ValueError.
    """
    h = Household('Michigan', 2.5, 10000)
    with pytest.raises(ValueError):
        screen(h)


def test_already_receiving_lifeline():
    """R7.6 — lifeline_already=True -> ALREADY_RECEIVING with one-benefit-per-household text."""
    h = Household('Michigan', 2, 15000, lifeline_already=True)
    result = screen(h)[0]
    assert result.status == LifelineStatus.ALREADY_RECEIVING
    assert 'one benefit per household' in result.explanation.lower()


def test_snap_participation_above_threshold():
    """R7.7 — income above threshold + snap=True -> LIKELY_QUALIFIES_PROGRAM."""
    h = Household('Michigan', 2, 60000, snap=True)
    result = screen(h)[0]
    assert result.status == LifelineStatus.LIKELY_QUALIFIES_PROGRAM


def test_snap_result_no_dollar_estimate():
    """R7.8 — SNAP result contains no numeric dollar estimate."""
    h = Household('Michigan', 2, 30000)
    snap_result = screen(h)[1]
    assert snap_result.savings_range is None
    assert not re.search(r'\$\d+', snap_result.explanation)


def test_ser_result_no_forbidden_words():
    """R7.9 — SER result never uses approved/guaranteed/will receive."""
    for utility_emergency in (True, False):
        h = Household('Michigan', 2, 20000, utility_emergency=utility_emergency)
        ser_result = screen(h)[2]
        low = ser_result.explanation.lower()
        assert 'approved' not in low
        assert 'guaranteed' not in low
        assert 'will receive' not in low


def test_no_streamlit_import():
    """R7.10 — engine.py source code must not contain 'import streamlit'.

    This check reads the engine.py source file and parses its AST to find
    import statements. It does not manipulate sys.modules.
    """
    engine_path = Path(__file__).resolve().parents[1] / 'engine.py'
    source = engine_path.read_text(encoding='utf-8')
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name != 'streamlit', (
                    'engine.py must not import streamlit (found: import streamlit)'
                )
        if isinstance(node, ast.ImportFrom):
            assert node.module != 'streamlit', (
                'engine.py must not import from streamlit'
            )


# ---------------------------------------------------------------------------
# Additional correctness checks
# ---------------------------------------------------------------------------

def test_screen_returns_three_results():
    """screen() always returns exactly 3 ScreeningResult objects for Michigan."""
    h = Household('Michigan', 2, 30000)
    results = screen(h)
    assert len(results) == 3
    assert all(isinstance(r, ScreeningResult) for r in results)


def test_ser_urgent_referral_on_emergency():
    h = Household('Michigan', 2, 8000, utility_emergency=True)
    assert screen(h)[2].status == 'urgent_referral'


def test_ser_label_is_emergency_referral():
    """SER explanation contains 'Emergency Referral' when emergency is active."""
    h = Household('Michigan', 2, 8000, utility_emergency=True)
    result = screen(h)[2]
    assert 'Emergency Referral' in result.explanation


def test_household_alias():
    """HouseholdInput and Household are the same class."""
    assert HouseholdInput is Household


def test_url_constants_are_plain_strings():
    """URL constants must be plain HTTPS strings, not Markdown links."""
    for url in (LIFELINE_SOURCE, SNAP_SOURCE, SER_SOURCE):
        assert url.startswith('https://'), 'URL not HTTPS: ' + url
        assert '[' not in url, 'URL contains Markdown bracket: ' + url
        assert ']' not in url, 'URL contains Markdown bracket: ' + url


def test_validate_household_rejects_float_size():
    """validate_household raises ValueError for non-integer size."""
    h = Household('Michigan', 2, 30000)
    # Bypass frozen dataclass by creating a plain object for the validator
    class FakeH:
        size = 2.5
        annual_income = 30000
    with pytest.raises(ValueError):
        validate_household(FakeH())


def test_snap_no_savings_range_on_already_receiving():
    """SNAP result has savings_range=None even when household receives SNAP."""
    h = Household('Michigan', 2, 30000, snap=True)
    snap_result = screen(h)[1]
    assert snap_result.savings_range is None


def test_status_value_attribute():
    """LifelineStatus.value returns the bare string key (not 'LifelineStatus.X').

    This confirms the fix for Python 3.11+ where str(LifelineStatus.X)
    returns 'LifelineStatus.X' rather than 'X'.
    """
    assert LifelineStatus.LIKELY_QUALIFIES_PROGRAM.value == 'LIKELY_QUALIFIES_PROGRAM'
    assert LifelineStatus.LIKELY_QUALIFIES_INCOME.value  == 'LIKELY_QUALIFIES_INCOME'
    assert LifelineStatus.ALREADY_RECEIVING.value        == 'ALREADY_RECEIVING'
    assert LifelineStatus.NOT_INDICATED.value            == 'NOT_INDICATED'
    assert LifelineStatus.INCOMPLETE_DATA.value          == 'INCOMPLETE_DATA'


def test_format_savings_string():
    """Savings range formats as plain text with 'per month' / 'per year' wording."""
    from engine import SavingsRange, LIFELINE_STANDARD_MONTHLY_MAX, LIFELINE_STANDARD_ANNUAL_MAX, LIFELINE_SAVINGS_NOTE
    sr = SavingsRange(
        monthly_max=LIFELINE_STANDARD_MONTHLY_MAX,
        annual_max=LIFELINE_STANDARD_ANNUAL_MAX,
        note=LIFELINE_SAVINGS_NOTE,
    )
    # Reproduce format_savings logic (defined in app.py) using plain-text wording
    # that avoids Markdown/LaTeX dollar-sign parsing
    formatted = (
        'Up to $' + '{:.2f}'.format(sr.monthly_max) + ' per month'
        + ' ($' + '{:.0f}'.format(sr.annual_max) + ' per year)'
        + ' — ' + sr.note
    )
    assert formatted.startswith('Up to $9.25 per month ($111 per year)')
    assert 'actual discount' in formatted
