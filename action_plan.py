
"""Personalized next steps for BenefitChain AI.

Educational guidance only, not an official eligibility determination.
"""

from dataclasses import dataclass

from engine import LifelineStatus

LIFELINE_URL = "https://www.usac.org/lifeline/consumer-eligibility/"
MI_BRIDGES_URL = "https://newmibridges.michigan.gov/"


@dataclass(frozen=True)
class ActionItem:
    program: str
    reason: str
    next_steps: list
    url: str
    priority: str


def create_action_plan(household, results, opportunities):
    """Create household-specific actions from existing screening results."""

    if household.state != "Michigan":
        return []

    actions = []

    lifeline = results[0]
    lifeline_status = lifeline.status

    if lifeline_status in (
        LifelineStatus.LIKELY_QUALIFIES_INCOME,
        LifelineStatus.LIKELY_QUALIFIES_PROGRAM,
    ):
        actions.append(
            ActionItem(
                program="Lifeline — Phone and Internet Discount",
                reason=lifeline.explanation,
                next_steps=[
                    "Review the official Lifeline qualification rules.",
                    "Prepare income or qualifying-program documentation.",
                    "Apply through the official Lifeline process.",
                ],
                url=LIFELINE_URL,
                priority="Potential pathway identified",
            )
        )

    if results[2].status == "urgent_referral":
        actions.insert(
            0,
            ActionItem(
                program="State Emergency Relief — Energy Assistance",
                reason="You reported an active utility emergency or shutoff risk.",
                next_steps=[
                    "Contact your utility provider promptly.",
                    "Review Michigan State Emergency Relief.",
                    "Apply through MI Bridges and provide requested documents.",
                ],
                url=MI_BRIDGES_URL,
                priority="Urgent referral",
            )
        )

    for opportunity in opportunities:
        if opportunity.name == "SNAP — Food Assistance":
            actions.append(
                ActionItem(
                    program="SNAP — Food Assistance",
                    reason=(
                        opportunity.status + ". "
                        + opportunity.explanation
                    ),
                    next_steps=[
                        "Review Michigan's SNAP eligibility requirements.",
                        "Prepare household income and expense information.",
                        "Apply through MI Bridges for an official decision.",
                    ],
                    url=opportunity.application_url,
                    priority="Explore food assistance",
                )
            )

        elif opportunity.name == "Medicaid and Health Coverage":
            actions.append(
                ActionItem(
                    program="Medicaid and Health Insurance",
                    reason=opportunity.explanation,
                    next_steps=[
                        "Review health coverage options for household members.",
                        "Prepare age, income, and household information.",
                        "Explore coverage and apply through MI Bridges.",
                    ],
                    url=opportunity.application_url,
                    priority="Explore health coverage",
                )
            )

    return actions
