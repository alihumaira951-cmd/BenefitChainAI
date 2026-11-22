"""BenefitChain AI — Streamlit application entry point."""
import streamlit as st
from engine import (
    Household, screen, LifelineStatus, SavingsRange,
    LIFELINE_STANDARD_MONTHLY_MAX, LIFELINE_STANDARD_ANNUAL_MAX,
)
from graph import render_benefit_graph

# ---------------------------------------------------------------------------
# Page config — centered layout, no sidebar
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title='BenefitChain AI',
    page_icon='🔗',
    layout='centered',
)

# A3 — CSS for visual polish
st.markdown("""
<style>
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 10px !important;
    border: 1px solid #e0e0e0 !important;
    margin-bottom: 8px !important;
}
[data-testid="stMetric"] {
    background: #f0f7f4;
    border-radius: 10px;
    padding: 12px;
    border: 1px solid #c8e6c9;
}
[data-testid="stFormSubmitButton"] > button {
    background-color: #1a6b3c !important;
    color: white !important;
    border-radius: 8px !important;
    font-size: 1.05em !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# UI constants
# ---------------------------------------------------------------------------
PRIVACY_NOTICE = (
    'BenefitChain AI uses the information you enter to provide preliminary benefit '
    'screening. Your responses are processed by the application server during your '
    'session. We do not ask for names, Social Security numbers, or case numbers, and '
    'the application is designed not to save household profiles to a permanent '
    'database. Please do not enter sensitive identifying information.'
)

FOOTER_DISCLAIMER = (
    'This tool provides preliminary screening only. Results are not an official '
    'eligibility determination. Contact the program directly to apply.'
)

# DOMINO_EFFECT_EXPLANATION replaced by _domino_explanation() below

# A2 — user-friendly status labels
STATUS_LABELS = {
    'LIKELY_QUALIFIES_INCOME':  'Potential Lifeline Pathway — Income Qualifies',
    'LIKELY_QUALIFIES_PROGRAM': 'Potential Lifeline Pathway — Existing Program Participation',
    'ALREADY_RECEIVING':        'Already Receiving Lifeline',
    'NOT_INDICATED':            'Not Indicated by Current Inputs',
    'INCOMPLETE_DATA':          'Please Complete All Fields',
    'needs_review':             'Preliminary Screening — Visit MI Bridges to Apply',
    'urgent_referral':          'Emergency Referral — Contact MDHHS Promptly',
    'already_receiving':        'Already Receiving This Benefit',
    'out_of_scope':             'Outside Coverage Area',
}

# A4 — status icons
STATUS_ICONS = {
    'LIKELY_QUALIFIES_INCOME':  '🟢',
    'LIKELY_QUALIFIES_PROGRAM': '🟢',
    'ALREADY_RECEIVING':        '🔵',
    'NOT_INDICATED':            '⚪',
    'INCOMPLETE_DATA':          '🟡',
    'needs_review':             '🟡',
    'urgent_referral':          '🟠',
    'already_receiving':        '🔵',
    'out_of_scope':             '⚪',
}

DEMO_HOUSEHOLD = dict(
    household_size=3,
    annual_income=28000.0,
    snap=True,
    medicaid=True,
    ssi=False,
    public_housing=False,
    veterans_pension=False,
    utility_emergency=False,
    lifeline_already=False,
    demo_loaded=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def format_savings(sr):
    # Returns plain text — do NOT pass this through st.markdown/st.success/st.info
    # (dollar signs in Markdown are parsed as LaTeX math delimiters)
    return (
        'Up to $' + '{:.2f}'.format(sr.monthly_max) + ' per month'
        + ' ($' + '{:.0f}'.format(sr.annual_max) + ' per year)'
        + ' — ' + sr.note
    )


def _safe_write(text):
    # Render plain text safely: escape dollar signs so Markdown/MathJax
    # does not interpret '$...$' as LaTeX math.
    # Uses st.markdown with HTML entity escaping — preserves normal prose.
    escaped = text.replace('$', '&#36;')
    st.markdown(escaped)


def _domino_explanation(h, results):
    """Return a household-specific Benefit Domino Effect explanation.

    Describes which connections are active for this household and which
    are general examples not triggered by the current inputs.
    """
    lifeline_status = results[0].status if results else None
    has_snap      = getattr(h, "snap", False)
    has_medicaid  = getattr(h, "medicaid", False)
    has_emergency = getattr(h, "utility_emergency", False)

    active_programs = []
    if has_snap:     active_programs.append("SNAP")
    if has_medicaid: active_programs.append("Medicaid")

    lines = []

    # --- Lifeline section ---
    if lifeline_status == LifelineStatus.LIKELY_QUALIFIES_PROGRAM and active_programs:
        prog_list = " and ".join(active_programs)
        lines.append(
            "Your reported " + prog_list + " participation activates a Lifeline "
            "program-based pathway for this household. Lifeline providers will "
            "require proof of " + prog_list + " enrollment. A separate Lifeline "
            "application is still required — this is not automatic enrollment."
        )
    elif lifeline_status == LifelineStatus.LIKELY_QUALIFIES_INCOME:
        lines.append(
            "Your household's reported income falls at or below the 2026 Lifeline "
            "income guideline, suggesting a potential income-based Lifeline pathway. "
            "Income verification will be required when you apply."
        )
    elif lifeline_status == LifelineStatus.ALREADY_RECEIVING:
        lines.append(
            "Your household already receives Lifeline. Generally only one Lifeline "
            "benefit is permitted per household."
        )
    else:
        lines.append(
            "No Lifeline pathway was identified for this household based on the "
            "current inputs."
        )
        # If neither SNAP nor Medicaid reported, clarify the graph edges are general
        if not has_snap and not has_medicaid:
            lines.append(
                "The SNAP and Medicaid connections shown in the graph are general "
                "examples of how those programs can open a Lifeline pathway. They "
                "are not active pathways for this household because neither SNAP "
                "nor Medicaid participation was reported."
            )

    # --- SER section ---
    if has_emergency:
        lines.append(
            "An active energy emergency was reported. The SER card above provides "
            "an emergency referral to MDHHS — contact them promptly via MI Bridges."
        )

    # --- General note if SNAP/Medicaid present but no active Lifeline pathway found ---
    # (edge case: e.g. already_receiving)
    if active_programs and lifeline_status not in (
        LifelineStatus.LIKELY_QUALIFIES_PROGRAM,
        LifelineStatus.LIKELY_QUALIFIES_INCOME,
    ):
        prog_list = " and ".join(active_programs)
        lines.append(
            "In general, " + prog_list + " participation is a recognized Lifeline "
            "qualification pathway, though it was not the primary finding for this "
            "household based on the current inputs."
        )

    lines.append(
        "Each program connection shown in the graph requires a separate application "
        "and official verification. No automatic enrollment occurs."
    )

    return " ".join(lines)


def _init_session_state():
    defaults = dict(
        household_size=1,
        annual_income=0.0,
        snap=False,
        medicaid=False,
        ssi=False,
        public_housing=False,
        veterans_pension=False,
        utility_emergency=False,
        lifeline_already=False,
        demo_loaded=False,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
_init_session_state()

st.title('🔗 BenefitChain AI')
st.caption(
    'Discover connections between Michigan assistance programs '
    '• Preliminary screening only • Version 0.2'
)

# Privacy notice — always visible, above the form
st.info(PRIVACY_NOTICE)

# Try sample household button — above the form, outside form block
if st.button('Try sample household', help='Load a fictional household to explore the tool'):
    for k, v in DEMO_HOUSEHOLD.items():
        st.session_state[k] = v
    st.rerun()

if st.session_state.get('demo_loaded'):
    st.info('Demo data loaded — this is a fictional household for illustration.')

st.markdown('---')
st.subheader('Your household information')

# ---------------------------------------------------------------------------
# Questionnaire form — all inputs in main column, no sidebar
# ---------------------------------------------------------------------------
with st.form('household_form'):
    household_size = st.number_input(
        'Number of people in household',
        min_value=1, max_value=20,
        value=int(st.session_state.household_size),
        step=1,
        help='Count everyone who lives and eats together.',
    )
    annual_income = st.number_input(
        'Approximate annual gross household income ($)',
        min_value=0.0, max_value=1_000_000.0,
        value=float(st.session_state.annual_income),
        step=500.0,
        help='Combined pre-tax income for all household members.',
    )

    st.markdown('**Current program participation** *(check all that apply)*')
    snap             = st.checkbox('SNAP / food assistance',
                                   value=bool(st.session_state.snap))
    medicaid         = st.checkbox('Medicaid',
                                   value=bool(st.session_state.medicaid))
    ssi              = st.checkbox('Supplemental Security Income (SSI)',
                                   value=bool(st.session_state.ssi))
    public_housing   = st.checkbox('Federal Public Housing Assistance',
                                   value=bool(st.session_state.public_housing))
    veterans_pension = st.checkbox('Veterans / Survivors Pension',
                                   value=bool(st.session_state.veterans_pension))
    lifeline_already = st.checkbox('I already receive Lifeline',
                                   value=bool(st.session_state.lifeline_already))
    utility_emergency = st.checkbox(
        'Active energy emergency or shutoff risk',
        value=bool(st.session_state.utility_emergency),
    )

    submitted = st.form_submit_button('Screen my household', use_container_width=True)

# ---------------------------------------------------------------------------
# Validation and screening
# ---------------------------------------------------------------------------
if submitted:
    st.session_state.household_size    = int(household_size)
    st.session_state.annual_income     = float(annual_income)
    st.session_state.snap              = snap
    st.session_state.medicaid          = medicaid
    st.session_state.ssi               = ssi
    st.session_state.public_housing    = public_housing
    st.session_state.veterans_pension  = veterans_pension
    st.session_state.lifeline_already  = lifeline_already
    st.session_state.utility_emergency = utility_emergency
    st.session_state.demo_loaded       = False

    if int(household_size) < 1:
        st.error('Household size must be at least 1.')
        st.stop()
    if float(annual_income) < 0:
        st.error('Annual income cannot be negative.')
        st.stop()

    h = Household(
        state='Michigan',
        size=int(household_size),
        annual_income=float(annual_income),
        snap=snap,
        medicaid=medicaid,
        ssi=ssi,
        public_housing=public_housing,
        veterans_pension=veterans_pension,
        utility_emergency=utility_emergency,
        lifeline_already=lifeline_already,
    )

    try:
        results = screen(h)
    except ValueError as e:
        st.error('Please check your inputs: ' + str(e))
        st.stop()

    # ------------------------------------------------------------------
    # Summary metrics
    # ------------------------------------------------------------------
    st.markdown('---')
    st.subheader('Screening Results')

    # Separate Lifeline qualification pathways from SER emergency referrals
    lifeline_result = results[0]
    ser_result      = results[2]
    has_lifeline_pathway = lifeline_result.status in (
        LifelineStatus.LIKELY_QUALIFIES_INCOME,
        LifelineStatus.LIKELY_QUALIFIES_PROGRAM,
    )
    has_ser_emergency = (ser_result.status == 'urgent_referral')
    lifeline_pathway_count = 1 if has_lifeline_pathway else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Programs Reviewed', 3)
    col2.metric(
        'Lifeline Pathways',
        str(lifeline_pathway_count),
        help='Potential Lifeline qualification pathways based on income or program participation.',
    )
    col3.metric(
        'SER Emergency',
        'Referred' if has_ser_emergency else 'Not triggered',
        help='Whether an active energy emergency referral was identified. Counted separately from Lifeline pathways.',
    )
    if has_lifeline_pathway and lifeline_result.savings_range:
        col4.metric(
            'Lifeline Discount',
            'Up to $' + '{:.0f}'.format(lifeline_result.savings_range.annual_max) + '/yr',
            help='Illustrative annual Lifeline discount — standard benefit only. Actual discount depends on provider.',
        )
    else:
        col4.metric('Lifeline Discount', '—')

    st.caption(
        'Emergency referrals are shown separately from Lifeline qualification pathways. '
        'All results are preliminary screening indicators only. '
        'No SNAP or SER dollar amounts are estimated.'
    )

    # ------------------------------------------------------------------
    # A4 — Program cards with icons and fixed status key
    # ------------------------------------------------------------------
    for result in results:
        with st.container(border=True):
            raw = result.status
            status_key = raw.value if hasattr(raw, 'value') else str(raw)
            status_label = STATUS_LABELS.get(status_key, status_key)
            icon = STATUS_ICONS.get(status_key, '⚪')

            st.subheader(result.rule.name)
            st.markdown(icon + ' **' + status_label + '**')
            _safe_write(result.explanation)

            if result.savings_range is not None:
                # Use st.metric (renders plain text, not Markdown) to avoid
                # dollar signs being parsed as LaTeX math delimiters
                st.metric(
                    label='Illustrative savings',
                    value=format_savings(result.savings_range),
                    help='This is an illustrative figure only. Actual discounts depend on your service provider and program rules.',
                )

            st.markdown('**Suggested next steps**')
            for i, step in enumerate(result.steps, 1):
                _safe_write(str(i) + '. ' + step)

            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.link_button('Official program information ↗', result.rule.source_url)
            with col_b:
                st.caption('Policy review: ' + result.rule.policy_review_date)

    # ------------------------------------------------------------------
    # Benefit graph
    # ------------------------------------------------------------------
    st.markdown('---')
    st.subheader('Benefit Domino Effect')
    fig = render_benefit_graph(h, results)
    st.plotly_chart(fig, use_container_width=True)
    _safe_write(_domino_explanation(h, results))

    # Footer disclaimer
    st.markdown('---')
    st.caption(FOOTER_DISCLAIMER)

else:
    st.markdown('---')
    st.markdown(
        '#### How to use this tool\n\n'
        'Enter your household information above and select **Screen my household** '
        'to see which benefit programs may have pathways worth exploring. '
        'Or select **Try sample household** to see an example.\n\n'
        '*All results are preliminary screening only — not official eligibility decisions.*'
    )

# ---------------------------------------------------------------------------
# Official resources — always visible
# ---------------------------------------------------------------------------
st.markdown('---')
st.markdown('#### Official resources')
st.markdown(
    '- [USAC Lifeline eligibility](https://www.usac.org/lifeline/consumer-eligibility/)\n'
    '- [Michigan SNAP eligibility](https://www.michigan.gov/mdhhs/assistance-programs/food/eligibility)\n'
    '- [Michigan State Emergency Relief](https://www.michigan.gov/mdhhs/assistance-programs/emergency-relief/eligibility)\n'
    '- [MI Bridges — official Michigan application portal](https://newmibridges.michigan.gov/)'
)
st.caption(
    'Last policy review: 2026-11-22. '
    'This tool is not affiliated with USAC or Michigan MDHHS.'
)
