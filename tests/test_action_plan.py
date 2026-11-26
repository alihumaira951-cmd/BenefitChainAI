
"""Tests for BenefitChain AI's personalized action plan."""

from engine import Household, screen
from discovery import discover_benefits
from action_plan import create_action_plan


def make_plan(
    income=15000,
    size=3,
    children=2,
    snap=False,
    medicaid=False,
    emergency=False,
):
    household = Household(
        state="Michigan",
        size=size,
        annual_income=income,
        children_under_19=children,
        snap=snap,
        medicaid=medicaid,
        utility_emergency=emergency,
    )
    return create_action_plan(
        household,
        screen(household),
        discover_benefits(household),
    )


def test_household_without_benefits_gets_three_actions():
    actions = make_plan()
    programs = [item.program for item in actions]

    assert len(actions) == 3
    assert any("Lifeline" in name for name in programs)
    assert any("SNAP" in name for name in programs)
    assert any("Medicaid" in name for name in programs)


def test_already_receiving_snap_has_no_snap_action():
    actions = make_plan(snap=True)
    assert not any("SNAP" in item.program for item in actions)


def test_already_receiving_medicaid_has_no_medicaid_action():
    actions = make_plan(medicaid=True)
    assert not any("Medicaid" in item.program for item in actions)


def test_utility_emergency_is_first():
    actions = make_plan(emergency=True)

    assert actions[0].program.startswith("State Emergency Relief")
    assert actions[0].priority == "Urgent referral"


def test_actions_have_links_and_next_steps():
    actions = make_plan()

    for item in actions:
        assert item.url.startswith("https://")
        assert item.reason
        assert len(item.next_steps) > 0


def test_other_state_has_no_action_plan():
    household = Household(
        state="Ohio",
        size=3,
        annual_income=15000,
    )

    actions = create_action_plan(
        household,
        screen(household),
        discover_benefits(household),
    )

    assert actions == []
