
"""Tests for Michigan benefit discovery."""

from engine import Household
from discovery import discover_benefits, compare_snap_income


def make_household(income, size=3, snap=False, medicaid=False):
    return Household(
        state="Michigan",
        size=size,
        annual_income=income,
        snap=snap,
        medicaid=medicaid,
    )


def test_low_income_snap_comparison():
    household = make_household(15000)
    assert compare_snap_income(household) == (
        "Below standard gross-income guideline"
    )


def test_intermediate_income_snap_comparison():
    household = make_household(45000)
    assert compare_snap_income(household) == (
        "Above standard limit; other SNAP rules may apply"
    )


def test_high_income_snap_comparison():
    household = make_household(100000)
    assert compare_snap_income(household) == (
        "Above these reference limits; official review recommended"
    )


def test_no_existing_benefits():
    household = make_household(15000)
    opportunities = discover_benefits(household)

    names = [item.name for item in opportunities]

    assert "SNAP — Food Assistance" in names
    assert "Medicaid and Health Coverage" in names


def test_already_receiving_snap():
    household = make_household(15000, snap=True)
    opportunities = discover_benefits(household)

    names = [item.name for item in opportunities]

    assert "SNAP — Food Assistance" not in names
    assert "Medicaid and Health Coverage" in names


def test_already_receiving_medicaid():
    household = make_household(15000, medicaid=True)
    opportunities = discover_benefits(household)

    names = [item.name for item in opportunities]

    assert "SNAP — Food Assistance" in names
    assert "Medicaid and Health Coverage" not in names


def test_other_state_not_screened():
    household = Household(
        state="Ohio",
        size=3,
        annual_income=15000,
    )

    assert discover_benefits(household) == []

def test_health_coverage_with_two_children():
    household = Household(
        state="Michigan",
        size=3,
        annual_income=15000,
        children_under_19=2,
    )

    opportunities = discover_benefits(household)
    health = next(
        item for item in opportunities
        if item.name == "Medicaid and Health Coverage"
    )

    assert "2 child(ren)" in health.explanation
    assert "MIChild" in health.explanation


def test_health_coverage_without_children():
    household = Household(
        state="Michigan",
        size=2,
        annual_income=20000,
        children_under_19=0,
    )

    opportunities = discover_benefits(household)
    health = next(
        item for item in opportunities
        if item.name == "Medicaid and Health Coverage"
    )

    assert "Healthy Michigan Plan" in health.explanation


def test_health_coverage_not_recommended_if_receiving_medicaid():
    household = Household(
        state="Michigan",
        size=3,
        annual_income=15000,
        children_under_19=2,
        medicaid=True,
    )

    opportunities = discover_benefits(household)

    assert not any(
        item.name == "Medicaid and Health Coverage"
        for item in opportunities
    )

