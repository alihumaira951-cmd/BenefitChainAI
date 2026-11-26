
"""Michigan benefit discovery.

Provides possible assistance pathways, not official eligibility decisions.
"""

from dataclasses import dataclass

MI_BRIDGES = "https://newmibridges.michigan.gov"


# Michigan SNAP standard monthly gross-income limits.
# Effective October 1, 2026.
# Source: Michigan MDHHS Reference Table RFT 250.
# These limits do not apply to every household.

SNAP_MONTHLY_GROSS_LIMITS = {
    1: 1729,
    2: 2345,
    3: 2960,
    4: 3575,
    5: 4191,
    6: 4806,
    7: 5421,
    8: 6037,
}

SNAP_ADDITIONAL_PERSON = 616
# Additional Michigan SNAP income reference:
# 200% monthly categorical income limits, effective October 1, 2026.
# Applicability depends on Michigan SNAP categorical eligibility rules.

SNAP_MONTHLY_CATEGORICAL_LIMITS = {
    1: 2660,
    2: 3608,
    3: 4554,
    4: 5500,
    5: 6448,
    6: 7394,
    7: 8340,
    8: 9288,
}

SNAP_CATEGORICAL_ADDITIONAL_PERSON = 948

def compare_snap_income(household):
    """Compare income with Michigan SNAP reference limits.

    This is not an official eligibility determination.
    """
    size = household.size
    monthly_income = household.annual_income / 12

    if size <= 8:
        standard_limit = SNAP_MONTHLY_GROSS_LIMITS[size]
        categorical_limit = SNAP_MONTHLY_CATEGORICAL_LIMITS[size]
    else:
        extra_people = size - 8
        standard_limit = (
            SNAP_MONTHLY_GROSS_LIMITS[8]
            + extra_people * SNAP_ADDITIONAL_PERSON
        )
        categorical_limit = (
            SNAP_MONTHLY_CATEGORICAL_LIMITS[8]
            + extra_people * SNAP_CATEGORICAL_ADDITIONAL_PERSON
        )

    if monthly_income <= standard_limit:
        return "Below standard gross-income guideline"
    elif monthly_income <= categorical_limit:
        return "Above standard limit; other SNAP rules may apply"
    else:
        return "Above these reference limits; official review recommended"

@dataclass(frozen=True)
class BenefitOpportunity:
    name: str
    status: str
    explanation: str
    application_url: str


def discover_benefits(household):
    """Identify programs worth exploring for a Michigan household."""

    if household.state != "Michigan":
        return []

    opportunities = []

    if not household.snap:
        snap_income_status = compare_snap_income(household)
        opportunities.append(
            BenefitOpportunity(
                name="SNAP — Food Assistance",
                status=snap_income_status,
                explanation=(
    "Your household may qualify for Michigan food assistance. "
    "The income comparison is preliminary; deductions, household "
    "circumstances, and other SNAP rules still apply. "
    "Apply through MI Bridges for an official decision."
),
                application_url=MI_BRIDGES,
            )
        )

    if not household.medicaid:
        children_count = getattr(household, "children_under_19", 0)

        if children_count > 0:
            coverage_message = (
                f"Your household includes {children_count} child(ren) under age 19. "
                "Michigan offers children's health coverage through Medicaid "
                "and MIChild. Income, age, household circumstances, and other "
                "rules determine eligibility. Apply through MI Bridges "
                "for an official decision."
            )
        else:
            coverage_message = (
                "Your household may have health insurance options through "
                "Michigan Medicaid, the Healthy Michigan Plan, or other "
                "coverage programs. Eligibility depends on age, income, "
                "household circumstances, and other requirements."
            )
        opportunities.append(
            BenefitOpportunity(
                name="Medicaid and Health Coverage",
                status="Worth exploring",
                explanation=coverage_message,
                application_url=MI_BRIDGES,
            )
        )

    return opportunities
