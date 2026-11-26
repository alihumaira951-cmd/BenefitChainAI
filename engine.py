"""Transparent benefit screening, NOT an official eligibility determination."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# ---------------------------------------------------------------------------
# URL constants — plain HTTPS strings, no Markdown formatting
# ---------------------------------------------------------------------------
LIFELINE_SOURCE = 'https://www.usac.org/lifeline/consumer-eligibility/'
SNAP_SOURCE = 'https://www.michigan.gov/mdhhs/assistance-programs/food/eligibility'
SER_SOURCE = 'https://www.michigan.gov/mdhhs/assistance-programs/emergency-relief/eligibility'
MI_BRIDGES_URL = 'https://newmibridges.michigan.gov'

# ---------------------------------------------------------------------------
# Lifeline 2026 income thresholds (USAC 135% FPG)
# ---------------------------------------------------------------------------
LIFELINE_2026 = {
    1: 21546, 2: 29214, 3: 36882, 4: 44550,
    5: 52218, 6: 59886, 7: 67554, 8: 75222,
}
LIFELINE_PER_ADDITIONAL_PERSON = 7668

# Standard Lifeline discount — Tribal-land enhanced benefit NOT included
LIFELINE_STANDARD_MONTHLY_MAX = 9.25
LIFELINE_STANDARD_ANNUAL_MAX = 111.0
LIFELINE_SAVINGS_NOTE = 'actual discount depends on service provider and program rules'


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class LifelineStatus(str, Enum):
    LIKELY_QUALIFIES_INCOME  = 'LIKELY_QUALIFIES_INCOME'
    LIKELY_QUALIFIES_PROGRAM = 'LIKELY_QUALIFIES_PROGRAM'
    ALREADY_RECEIVING        = 'ALREADY_RECEIVING'
    NOT_INDICATED            = 'NOT_INDICATED'
    INCOMPLETE_DATA          = 'INCOMPLETE_DATA'


@dataclass(frozen=True)
class ProgramRule:
    name: str
    source_url: str
    effective_year: int
    policy_review_date: str


@dataclass(frozen=True)
class SavingsRange:
    monthly_max: float
    annual_max: float
    note: str


@dataclass(frozen=True)
class Household:
    state: str
    size: int
    annual_income: float
    snap: bool = False
    medicaid: bool = False
    ssi: bool = False
    public_housing: bool = False
    veterans_pension: bool = False
    utility_emergency: bool = False
    lifeline_already: bool = False
    children_under_19: int = 0


# Canonical alias used in design docs; Household is the primary name so
# existing imports continue to work.
HouseholdInput = Household


@dataclass(frozen=True)
class ScreeningResult:
    rule: ProgramRule
    status: str
    explanation: str
    steps: list
    savings_range: Optional[SavingsRange] = None


# ---------------------------------------------------------------------------
# Program rule records
# ---------------------------------------------------------------------------
LIFELINE_RULE = ProgramRule(
    name='Lifeline phone / internet discount',
    source_url=LIFELINE_SOURCE,
    effective_year=2026,
    policy_review_date='2026-11-22',
)
SNAP_RULE = ProgramRule(
    name='Michigan Food Assistance Program (SNAP)',
    source_url=SNAP_SOURCE,
    effective_year=2026,
    policy_review_date='2026-11-22',
)
SER_RULE = ProgramRule(
    name='Michigan State Emergency Relief (energy)',
    source_url=SER_SOURCE,
    effective_year=2026,
    policy_review_date='2026-11-22',
)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_household(h):
    """Raise ValueError for invalid Household fields."""
    if isinstance(h.size, bool) or not isinstance(h.size, int):
        raise ValueError('Household size must be a positive integer')
    if h.size < 1:
        raise ValueError('Household size must be a positive integer')
    if h.annual_income < 0:
        raise ValueError('Annual income must be non-negative')


# ---------------------------------------------------------------------------
# Income threshold helper
# ---------------------------------------------------------------------------

def lifeline_income_limit(size):
    """Return the 2026 Lifeline 135% FPG annual income threshold.

    Args:
        size: Positive integer household size.

    Returns:
        Annual income threshold in whole dollars.

    Raises:
        ValueError: If size < 1.
    """
    if size < 1:
        raise ValueError('Household size must be at least 1')
    if size <= 8:
        return LIFELINE_2026[size]
    return LIFELINE_2026[8] + (size - 8) * LIFELINE_PER_ADDITIONAL_PERSON


# ---------------------------------------------------------------------------
# Individual screening functions
# ---------------------------------------------------------------------------

_LIFELINE_SAVINGS = SavingsRange(
    monthly_max=LIFELINE_STANDARD_MONTHLY_MAX,
    annual_max=LIFELINE_STANDARD_ANNUAL_MAX,
    note=LIFELINE_SAVINGS_NOTE,
)

_QUALIFYING_FLAGS = ('snap', 'medicaid', 'ssi', 'public_housing', 'veterans_pension')

_FLAG_NAMES = {
    'snap': 'SNAP',
    'medicaid': 'Medicaid',
    'ssi': 'SSI',
    'public_housing': 'Federal Public Housing Assistance',
    'veterans_pension': 'Veterans/Survivors Pension',
}


def screen_lifeline(h):
    """Screen household for Lifeline eligibility pathway."""
    limit = lifeline_income_limit(h.size)
    qualifying = [f for f in _QUALIFYING_FLAGS if getattr(h, f)]

    if h.lifeline_already:
        return ScreeningResult(
            rule=LIFELINE_RULE,
            status=LifelineStatus.ALREADY_RECEIVING,
            explanation=(
                'Your household already receives Lifeline. Generally only '
                'one benefit per household is permitted under the Lifeline '
                'one benefit per household rule.'
            ),
            steps=[
                'Review the USAC one-benefit-per-household policy at the link below.',
                'Contact your Lifeline provider if you have questions about your current benefit.',
            ],
            savings_range=None,
        )

    if qualifying:
        program_names = ', '.join(_FLAG_NAMES[f] for f in qualifying)
        return ScreeningResult(
            rule=LIFELINE_RULE,
            status=LifelineStatus.LIKELY_QUALIFIES_PROGRAM,
            explanation=(
                'Potential Qualification Pathway (program-based): Participation in '
                + program_names
                + ' is a recognized Lifeline qualification pathway. Official verification '
                'and a separate Lifeline application are still required. This is a '
                'preliminary screening result, not an official determination.'
            ),
            steps=[
                'Gather documentation of your program participation (e.g., award letter).',
                'Visit the National Verifier at the official USAC link below to apply.',
                'Review the USAC one-benefit-per-household rule before applying.',
            ],
            savings_range=_LIFELINE_SAVINGS,
        )

    if h.annual_income <= limit:
        return ScreeningResult(
            rule=LIFELINE_RULE,
            status=LifelineStatus.LIKELY_QUALIFIES_INCOME,
            explanation=(
                'Potential Qualification Pathway (income-based): Your reported annual income '
                'is at or below the 2026 Lifeline income guideline of $'
                + '{:,.0f}'.format(limit)
                + ' for a household of '
                + str(h.size)
                + '. Official income verification and a separate application are still '
                'required. This is a preliminary screening result, not an official determination.'
            ),
            steps=[
                'Gather recent income documentation (pay stubs, benefit award letters).',
                'Visit the National Verifier at the official USAC link below to apply.',
                'Review the USAC one-benefit-per-household rule before applying.',
            ],
            savings_range=_LIFELINE_SAVINGS,
        )

    return ScreeningResult(
        rule=LIFELINE_RULE,
        status=LifelineStatus.NOT_INDICATED,
        explanation=(
            'Not Indicated: Your reported income ($'
            + '{:,.0f}'.format(h.annual_income)
            + ') is above the 2026 Lifeline income guideline of $'
            + '{:,.0f}'.format(limit)
            + ' for a household of '
            + str(h.size)
            + ', and no qualifying program participation was reported. '
            'Other special pathways were not screened by this tool.'
        ),
        steps=[
            'Visit the official USAC Lifeline page to review all eligibility pathways.',
            'Contact USAC or a Lifeline provider if your circumstances have changed.',
        ],
        savings_range=None,
    )


def screen_snap(h):
    """Screen household for SNAP — preliminary referral only, no eligibility decision."""
    if h.snap:
        explanation = (
            'Preliminary Screening: You indicated your household already receives SNAP '
            'food assistance. SNAP eligibility involves Michigan-specific income '
            'deductions, household composition rules, and other criteria not '
            'evaluated by this tool.'
        )
        status = 'already_receiving'
        steps = [
            'No action needed if you are already receiving SNAP.',
            'Visit MI Bridges to report any changes to your household or income.',
        ]
    else:
        explanation = (
            'Preliminary Screening — Refer to MI Bridges: An accurate Michigan SNAP '
            'determination requires income deductions, household composition rules, and '
            'other criteria not collected here. SNAP eligibility involves '
            'Michigan-specific income deductions, household composition rules, and '
            'other criteria not evaluated by this tool.'
        )
        status = 'needs_review'
        steps = [
            'Visit MI Bridges to screen and apply for Michigan food assistance.',
            'Gather household size, income, and expense information before applying.',
            'Review Michigan SNAP eligibility requirements at the official link below.',
        ]

    return ScreeningResult(
        rule=SNAP_RULE,
        status=status,
        explanation=explanation,
        steps=steps,
        savings_range=None,
    )


def screen_ser(h):
    """Screen household for Michigan SER — emergency referral only."""
    if h.utility_emergency:
        explanation = (
            'Emergency Referral: You reported an active energy emergency or shutoff '
            'risk. Contact MDHHS via MI Bridges promptly. Michigan State Emergency '
            'Relief requires a caseworker review by MDHHS — this tool cannot replicate '
            'that review. Only MDHHS can determine whether assistance is available.'
        )
        status = 'urgent_referral'
        steps = [
            'If disconnection is imminent, contact your utility provider immediately.',
            'Apply for State Emergency Relief through MI Bridges at the link below.',
            'Have your utility account number and recent bills ready.',
        ]
    else:
        explanation = (
            'Michigan State Emergency Relief was not triggered because no active energy '
            'emergency was reported. SER assistance requires a caseworker review by '
            'MDHHS. This tool cannot replicate that review.'
        )
        status = 'needs_review'
        steps = [
            'If your situation changes and you face an energy emergency, contact MDHHS.',
            'Review SER eligibility conditions at the official MDHHS link below.',
        ]

    return ScreeningResult(
        rule=SER_RULE,
        status=status,
        explanation=explanation,
        steps=steps,
        savings_range=None,
    )


# ---------------------------------------------------------------------------
# Main screening entry point
# ---------------------------------------------------------------------------

def screen(h):
    """Run all three screenings and return [lifeline, snap, ser] ScreeningResults.

    Args:
        h: Household (or HouseholdInput) instance.

    Returns:
        List of three ScreeningResult objects: [0] Lifeline, [1] SNAP, [2] SER.

    Raises:
        ValueError: If household size or income is invalid.
    """
    validate_household(h)
    if h.state != 'Michigan':
        out_of_scope = ScreeningResult(
            rule=SNAP_RULE,
            status='out_of_scope',
            explanation='This tool currently covers Michigan only.',
            steps=['Select Michigan as your state to use this tool.'],
            savings_range=None,
        )
        return [out_of_scope, out_of_scope, out_of_scope]
    return [screen_lifeline(h), screen_snap(h), screen_ser(h)]
