"""BenefitChain AI — Streamlit application entry point."""
import streamlit as st
import html
import re
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
    layout='wide',
)

# ---------------------------------------------------------------------------
# Design system — navy / teal / white civic-tech palette
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ── Global typography & background ─────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}
.stApp {
    background: #f4f7fb;
}

/* ── Hero header ─────────────────────────────────────────────────────────── */
.hero-banner {
    background: linear-gradient(135deg, #0d2b55 0%, #0e5f7a 60%, #0a9396 100%);
    border-radius: 16px;
    padding: 2.4rem 2rem 2rem 2rem;
    margin-bottom: 1.6rem;
    color: white;
}
.hero-banner h1 {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0 0 0.3rem 0;
    color: white !important;
}
.hero-banner .hero-sub {
    font-size: 1.0rem;
    opacity: 0.88;
    margin: 0;
    color: #cce8ed;
}
.hero-banner .hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #d0f0f5;
    margin-bottom: 0.7rem;
}

/* ── Section cards ───────────────────────────────────────────────────────── */
.section-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem 1.6rem 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 10px rgba(13,43,85,0.07);
    border: 1px solid #e3eaf4;
}
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0d2b55;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Privacy notice ──────────────────────────────────────────────────────── */
.privacy-box {
    background: #eaf4fb;
    border-left: 4px solid #0e5f7a;
    border-radius: 0 10px 10px 0;
    padding: 0.85rem 1.1rem;
    margin-bottom: 1.2rem;
    font-size: 0.88rem;
    color: #1a3a4a;
    line-height: 1.55;
}

/* ── Demo banner ─────────────────────────────────────────────────────────── */
.demo-banner {
    background: #fff8e1;
    border: 1px solid #ffe082;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    font-size: 0.88rem;
    color: #5a4000;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Form elements ───────────────────────────────────────────────────────── */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #0d2b55 0%, #0e5f7a 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 1.0rem !important;
    font-weight: 600 !important;
    padding: 0.65em 1.4em !important;
    box-shadow: 0 3px 10px rgba(13,43,85,0.22) !important;
    transition: opacity 0.15s !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    opacity: 0.9 !important;
}
/* Sample household button */
button[kind="secondary"] {
    border-radius: 8px !important;
    border: 1.5px solid #0e5f7a !important;
    color: #0e5f7a !important;
}

/* ── Metric tiles ────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: white;
    border-radius: 12px;
    padding: 14px 16px !important;
    border: 1px solid #dde6f0;
    box-shadow: 0 1px 6px rgba(13,43,85,0.07);
}
[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #546e8a !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    color: #0d2b55 !important;
}

/* ── Program cards ───────────────────────────────────────────────────────── */
.program-card {
    background: white;
    border-radius: 14px;
    padding: 1.4rem 1.5rem 1.2rem 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid #dde6f0;
    box-shadow: 0 2px 8px rgba(13,43,85,0.07);
}
.program-card-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0d2b55;
    margin-bottom: 0.4rem;
}
.status-pill {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    margin-bottom: 0.75rem;
}
.status-green  { background: #e6f9ef; color: #1a6b3c; border: 1px solid #a8e6c3; }
.status-blue   { background: #e8f0fb; color: #1a4080; border: 1px solid #a8c4f0; }
.status-orange { background: #fff3e0; color: #b35a00; border: 1px solid #ffc980; }
.status-gray   { background: #f1f3f6; color: #546e8a; border: 1px solid #c8d2de; }
.status-yellow { background: #fffde7; color: #7a6000; border: 1px solid #ffe57a; }
.card-explanation {
    font-size: 0.93rem;
    color: #2c3e50;
    line-height: 1.6;
    margin-bottom: 0.9rem;
}
.savings-box {
    background: linear-gradient(90deg, #e8f7f0 0%, #e3f2fd 100%);
    border-radius: 10px;
    padding: 0.65rem 1rem;
    margin-bottom: 0.9rem;
    border: 1px solid #b2dfdb;
    font-size: 0.9rem;
    font-weight: 600;
    color: #0d4f3c;
}
.steps-list {
    padding-left: 0;
    margin: 0 0 0.9rem 0;
}
.steps-list li {
    list-style: none;
    padding: 0.3rem 0 0.3rem 1.6rem;
    position: relative;
    font-size: 0.9rem;
    color: #2c3e50;
    line-height: 1.5;
}
.steps-list li::before {
    content: counter(step-counter);
    counter-increment: step-counter;
    position: absolute;
    left: 0;
    top: 0.3rem;
    width: 1.2rem;
    height: 1.2rem;
    background: #0e5f7a;
    color: white;
    border-radius: 50%;
    font-size: 0.7rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    line-height: 1.2rem;
}
ol.steps-list { counter-reset: step-counter; }
.card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
    padding-top: 0.6rem;
    border-top: 1px solid #eef1f6;
    margin-top: 0.3rem;
    font-size: 0.78rem;
    color: #7a8fa6;
}

/* ── Results summary banner ──────────────────────────────────────────────── */
.results-banner {
    background: linear-gradient(90deg, #0d2b55 0%, #0e5f7a 100%);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
    color: white;
}
.results-banner h3 {
    color: white !important;
    margin: 0 0 0.25rem 0;
    font-size: 1.15rem;
    font-weight: 700;
}
.results-banner p {
    color: #cce8ed;
    margin: 0;
    font-size: 0.88rem;
}

/* ── Graph section ───────────────────────────────────────────────────────── */
.graph-explanation {
    background: #f0f7fb;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    font-size: 0.9rem;
    color: #1a3a4a;
    line-height: 1.6;
    margin-top: 0.6rem;
    border: 1px solid #c8dded;
}

/* ── Disclaimer footer ───────────────────────────────────────────────────── */
.disclaimer-footer {
    background: #f8f9fb;
    border: 1px solid #dde6f0;
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    font-size: 0.82rem;
    color: #546e8a;
    line-height: 1.55;
    text-align: center;
    margin-top: 1rem;
}

/* ── Resources section ───────────────────────────────────────────────────── */
.resources-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
    margin-top: 0.5rem;
}
.resource-link {
    background: white;
    border: 1px solid #dde6f0;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    font-size: 0.88rem;
    color: #0e5f7a;
    text-decoration: none;
    font-weight: 500;
    transition: background 0.15s;
}
.resource-link:hover { background: #eaf4fb; }

/* ── Intro / how-to panel ────────────────────────────────────────────────── */
.how-to-panel {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    border: 1px solid #dde6f0;
    box-shadow: 0 2px 8px rgba(13,43,85,0.06);
    margin-top: 0.5rem;
}
.how-to-step {
    display: flex;
    gap: 0.9rem;
    margin-bottom: 0.9rem;
    align-items: flex-start;
}
.how-to-num {
    width: 2rem;
    height: 2rem;
    min-width: 2rem;
    background: linear-gradient(135deg, #0d2b55, #0e5f7a);
    color: white;
    border-radius: 50%;
    font-weight: 800;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    justify-content: center;
}
.how-to-text strong { color: #0d2b55; display: block; margin-bottom: 0.1rem; }
.how-to-text span   { font-size: 0.88rem; color: #546e8a; }

/* ── Mobile responsiveness ───────────────────────────────────────────────── */
@media (max-width: 600px) {
    .hero-banner h1 { font-size: 1.5rem; }
    .resources-grid { grid-template-columns: 1fr; }
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
}

/* Presentation-ready refinements */
:root { --ink:#102947; --teal:#0d9488; --sky:#e9f6f9; }
[data-testid="stAppViewContainer"] { background: linear-gradient(150deg,#f0f8fa 0%,#f8fbff 46%,#f1f5fb 100%); }
[data-testid="stMainBlockContainer"] { max-width: 1120px; padding-top: 2.2rem; padding-bottom: 4rem; }
[data-testid="stHeader"] { background: transparent; }
.hero-banner { position:relative; overflow:hidden; border-radius:24px; padding:3.2rem 2.7rem; box-shadow:0 16px 40px rgba(12,48,86,.15); background:radial-gradient(circle at 89% 18%,rgba(111,234,222,.24) 0 13%,transparent 34%), linear-gradient(115deg,#0b2343 0%,#124d70 57%,#087e80 100%); }
.hero-banner:after {content:""; position:absolute; width:250px;height:250px;border:1px solid rgba(255,255,255,.18);border-radius:50%;right:-55px;bottom:-155px;pointer-events:none;}
.hero-banner h1 { font-size:clamp(2.3rem,4.2vw,3.6rem); letter-spacing:-.045em; line-height:1.1; }
.hero-banner .hero-sub { font-size:1.09rem; line-height:1.65; color:#e0f8fc; max-width:690px; opacity:1; }
.hero-banner .hero-badge { letter-spacing:.09em; padding:7px 13px; margin-bottom:1.25rem; }
.hero-chips {display:flex;flex-wrap:wrap;gap:.55rem;margin-top:1.65rem;}
.hero-chips span {border:1px solid rgba(255,255,255,.26);background:rgba(255,255,255,.12);padding:.42rem .78rem;border-radius:100px;color:#effcff;font-size:.81rem;font-weight:600;}
.section-title {font-size:1.04rem; letter-spacing:.045em; color:#12345a; margin-top:1.3rem; margin-bottom:.9rem;}
[data-testid="stForm"] {background:#fff;border:1px solid #e0eaf1; border-radius:18px; padding:1.4rem 1.6rem 1.1rem; box-shadow:0 7px 25px rgba(14,51,81,.06);}
[data-testid="stNumberInput"] input {border-radius:9px;}
[data-testid="stMetric"] {min-height:116px; border-radius:16px; padding:18px !important; box-shadow:0 6px 18px rgba(11,39,66,.07);border-top:3px solid #24a79b;}
[data-testid="stMetricValue"] {font-size:clamp(1.15rem,2.1vw,1.65rem) !important;}
.program-card {border-left:5px solid #0a9c94; border-radius:17px; padding:1.55rem 1.65rem; box-shadow:0 8px 23px rgba(13,43,85,.065);margin-bottom:.6rem;}
.program-card-name {font-size:1.2rem;margin-bottom:.7rem;letter-spacing:-.02em;}
.card-explanation {font-size:.96rem;line-height:1.73;}
.status-pill {font-size:.79rem;white-space:normal;line-height:1.5;}
.savings-box {padding:1rem 1.05rem;font-size:.94rem;}
.results-banner {border-radius:18px; padding:1.5rem 1.7rem; background:linear-gradient(120deg,#102d51,#0a747f);box-shadow:0 7px 25px rgba(13,43,85,.12);}
.results-banner h3 {font-size:1.4rem;}
.results-banner p {font-size:.94rem;line-height:1.6;}
.privacy-box {border-radius:12px;border:1px solid #cbdfea;border-left:4px solid #0e7f83;background:#ecf7fb;}
.how-to-panel {border-radius:18px; padding:1.5rem 1.7rem;}
.how-to-step {padding:.7rem .2rem; border-bottom:1px solid #edf2f6; margin-bottom:0;}
.how-to-step:last-of-type {border-bottom:0;}
.how-to-num {flex-shrink:0;}
.how-to-text strong {font-size:.97rem;}
.how-to-text span {line-height:1.5;display:block;}
.resource-link {padding:1rem 1.1rem; display:block; border-radius:13px; box-shadow:0 3px 10px rgba(13,43,85,.035);}
.resource-link:hover {transform:translateY(-1px);border-color:#76babd;}
[data-testid="stLinkButton"] a {border-radius:10px;}
[data-testid="stPlotlyChart"] {border:1px solid #e4ebf2;background:white;border-radius:16px;padding:.45rem;}
@media(max-width:750px) { [data-testid="stMainBlockContainer"] {padding:1rem .9rem 3rem;} .hero-banner {padding:2rem 1.3rem;border-radius:17px;} .hero-banner h1 {font-size:2.15rem;} .hero-banner .hero-sub {font-size:.96rem;} [data-testid="stForm"] {padding:1rem;} .program-card {padding:1.15rem;} .hero-chips {gap:.35rem;} .hero-chips span{font-size:.75rem;} }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# UI constants  (unchanged from approved logic)
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

STATUS_LABELS = {
    'LIKELY_QUALIFIES_INCOME':  'Potential Lifeline Pathway',
    'LIKELY_QUALIFIES_PROGRAM': 'Potential Lifeline Pathway',
    'ALREADY_RECEIVING':        'Already Receiving Lifeline',
    'NOT_INDICATED':            'Not Indicated by Current Inputs',
    'INCOMPLETE_DATA':          'Please Complete All Fields',
    'needs_review':             'Preliminary Screening — Visit MI Bridges to Apply',
    'urgent_referral':          'Emergency Referral — Contact MDHHS Promptly',
    'already_receiving':        'Already Receiving This Benefit',
    'out_of_scope':             'Outside Coverage Area',
}

# CSS class + accessible text prefix per status (not color-only)
STATUS_STYLE = {
    'LIKELY_QUALIFIES_INCOME':  ('status-green',  '✓ Pathway Found'),
    'LIKELY_QUALIFIES_PROGRAM': ('status-green',  '✓ Pathway Found'),
    'ALREADY_RECEIVING':        ('status-blue',   'ℹ Already Receiving'),
    'NOT_INDICATED':            ('status-gray',   '— Not Indicated'),
    'INCOMPLETE_DATA':          ('status-yellow', '⚠ Incomplete Data'),
    'needs_review':             ('status-yellow', '⚠ Refer to MI Bridges'),
    'urgent_referral':          ('status-orange', '⚡ Emergency Referral'),
    'already_receiving':        ('status-blue',   'ℹ Already Receiving'),
    'out_of_scope':             ('status-gray',   '— Outside Coverage'),
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
# Helpers  (logic unchanged)
# ---------------------------------------------------------------------------
def format_savings(sr):
    return (
        'Up to $' + '{:.2f}'.format(sr.monthly_max) + ' per month'
        + ' ($' + '{:.0f}'.format(sr.annual_max) + ' per year)'
        + ' — ' + sr.note
    )

def _safe(text):
    """Escape dynamic text for insertion into HTML, including dollar signs."""
    return html.escape(str(text)).replace('$', '&#36;')


def _render_html(markup):
    """Render HTML as a single line to prevent Markdown treating indents as code."""
    markup = re.sub(r'>\s+<', '><', markup.strip())
    st.markdown(markup, unsafe_allow_html=True)

def _domino_explanation(h, results):
    lifeline_status = results[0].status if results else None
    has_snap      = getattr(h, 'snap', False)
    has_medicaid  = getattr(h, 'medicaid', False)
    has_emergency = getattr(h, 'utility_emergency', False)
    active_programs = []
    if has_snap:     active_programs.append('SNAP')
    if has_medicaid: active_programs.append('Medicaid')
    lines = []
    if lifeline_status == LifelineStatus.LIKELY_QUALIFIES_PROGRAM and active_programs:
        prog_list = ' and '.join(active_programs)
        lines.append(
            'Your reported ' + prog_list + ' participation activates a Lifeline '
            'program-based pathway for this household. Documentation of participation '
            'in a qualifying program may be required. A separate Lifeline '
            'application is still required — this is not automatic enrollment.'
        )
    elif lifeline_status == LifelineStatus.LIKELY_QUALIFIES_INCOME:
        lines.append(
            "Your household's reported income falls at or below the 2026 Lifeline "
            'income guideline, suggesting a potential income-based Lifeline pathway. '
            'Income verification will be required when you apply.'
        )
    elif lifeline_status == LifelineStatus.ALREADY_RECEIVING:
        lines.append(
            'Your household already receives Lifeline. Generally only one Lifeline '
            'benefit is permitted per household.'
        )
    else:
        lines.append(
            'No Lifeline pathway was identified for this household based on the '
            'current inputs.'
        )
        if not has_snap and not has_medicaid:
            lines.append(
                'The SNAP and Medicaid connections shown in the graph are general '
                'examples of how those programs can open a Lifeline pathway. They '
                'are not active pathways for this household because neither SNAP '
                'nor Medicaid participation was reported.'
            )
    if has_emergency:
        lines.append(
            'An active energy emergency was reported. The SER card above provides '
            'an emergency referral to MDHHS — contact them promptly via MI Bridges.'
        )
    if active_programs and lifeline_status not in (
        LifelineStatus.LIKELY_QUALIFIES_PROGRAM,
        LifelineStatus.LIKELY_QUALIFIES_INCOME,
    ):
        prog_list = ' and '.join(active_programs)
        lines.append(
            'In general, ' + prog_list + ' participation is a recognized Lifeline '
            'qualification pathway, though it was not the primary finding for this '
            'household based on the current inputs.'
        )
    lines.append(
        'Each program connection shown in the graph requires a separate application '
        'and official verification. No automatic enrollment occurs.'
    )
    return ' '.join(lines)

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
# Page — hero header
# ---------------------------------------------------------------------------
_init_session_state()

_render_html("""
<div class="hero-banner">
  <div class="hero-badge">MICHIGAN • BENEFIT DISCOVERY</div>
  <h1>🔗 BenefitChain AI</h1>
  <p class="hero-sub">One benefit can lead to another. Discover potential assistance pathways, see how programs connect, and find official next steps.</p>
  <div class="hero-chips"><span>✓ No account required</span><span>◇ Michigan-focused</span><span>↗ Official program resources</span></div>
</div>
""")

# ---------------------------------------------------------------------------
# Privacy notice
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="privacy-box">🔒 <strong>Privacy:</strong> ' + PRIVACY_NOTICE + '</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Demo banner + button
# ---------------------------------------------------------------------------
col_demo, col_space = st.columns([1, 2])
with col_demo:
    if st.button('🧪 Try sample household', use_container_width=True,
                 help='Load a fictional household to explore the tool'):
        for k, v in DEMO_HOUSEHOLD.items():
            st.session_state[k] = v
        st.rerun()

if st.session_state.get('demo_loaded'):
    st.markdown(
        '<div class="demo-banner">🧪 <strong>Demo mode:</strong> '
        'This is a fictional household for illustration. '
        'Results shown are not real recommendations.</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Questionnaire
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">📋 Your Household Information</div>',
            unsafe_allow_html=True)

with st.form('household_form'):
    c1, c2 = st.columns(2)
    with c1:
        household_size = st.number_input(
            'People in household',
            min_value=1, max_value=20,
            value=int(st.session_state.household_size),
            step=1,
            help='Count everyone who lives and eats together.',
        )
    with c2:
        annual_income = st.number_input(
            'Approximate annual gross income ($)',
            min_value=0.0, max_value=1_000_000.0,
            value=float(st.session_state.annual_income),
            step=500.0,
            help='Combined pre-tax income for all household members.',
        )

    st.markdown('**Current program participation** — check all that apply')
    cb1, cb2 = st.columns(2)
    with cb1:
        snap     = st.checkbox('SNAP / food assistance',
                               value=bool(st.session_state.snap))
        ssi      = st.checkbox('Supplemental Security Income (SSI)',
                               value=bool(st.session_state.ssi))
        veterans_pension = st.checkbox('Veterans / Survivors Pension',
                                       value=bool(st.session_state.veterans_pension))
        lifeline_already = st.checkbox('I already receive Lifeline',
                                       value=bool(st.session_state.lifeline_already))
    with cb2:
        medicaid      = st.checkbox('Medicaid',
                                    value=bool(st.session_state.medicaid))
        public_housing = st.checkbox('Federal Public Housing Assistance',
                                     value=bool(st.session_state.public_housing))
        utility_emergency = st.checkbox(
            '⚡ Active energy emergency / shutoff risk',
            value=bool(st.session_state.utility_emergency),
        )

    submitted = st.form_submit_button(
        '🔍 Screen my household',
        use_container_width=True,
    )

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
    # Results summary banner + metrics
    # ------------------------------------------------------------------
    lifeline_result = results[0]
    ser_result      = results[2]
    has_lifeline_pathway = lifeline_result.status in (
        LifelineStatus.LIKELY_QUALIFIES_INCOME,
        LifelineStatus.LIKELY_QUALIFIES_PROGRAM,
    )
    has_ser_emergency    = (ser_result.status == 'urgent_referral')
    lifeline_count       = 1 if has_lifeline_pathway else 0

    if has_lifeline_pathway:
        banner_msg = 'A potential Lifeline pathway was identified. Review the details below.'
    elif has_ser_emergency:
        banner_msg = 'An energy emergency referral was triggered. See the SER card below.'
    else:
        banner_msg = 'No Lifeline pathway was identified for the current inputs. See details below.'

    st.markdown(
        '<div class="results-banner">'
        '<h3>📊 Screening Results</h3>'
        '<p>' + banner_msg + '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    mc1, mc2 = st.columns(2)
    mc1.metric('Programs Reviewed', 3)
    mc2.metric(
        'Lifeline Pathways', str(lifeline_count),
        help='Potential Lifeline qualification pathways based on income or program participation.',
    )
    mc3, mc4 = st.columns(2)
    mc3.metric(
        'SER Emergency',
        'Referred' if has_ser_emergency else 'Not triggered',
        help='Whether an active energy emergency referral was identified.',
    )
    if has_lifeline_pathway and lifeline_result.savings_range:
        mc4.metric(
            'Lifeline Discount',
            'Up to $' + '{:.0f}'.format(lifeline_result.savings_range.annual_max) + '/yr',
            help='Illustrative annual Lifeline discount — standard benefit only.',
        )
    else:
        mc4.metric('Lifeline Discount', '—')

    st.caption(
        'Emergency referrals are shown separately from Lifeline qualification pathways. '
        'All results are preliminary screening indicators only. '
        'No SNAP or SER dollar amounts are estimated.'
    )

    # ------------------------------------------------------------------
    # Program cards
    # ------------------------------------------------------------------
    st.markdown('<div class="section-title" style="margin-top:1.4rem">📋 Program Details</div>',
                unsafe_allow_html=True)

    for result in results:
        raw        = result.status
        status_key = raw.value if hasattr(raw, 'value') else str(raw)
        label      = STATUS_LABELS.get(status_key, status_key)
        css_cls, pill_prefix = STATUS_STYLE.get(status_key, ('status-gray', '—'))

        # Build steps HTML safely (escape $ signs)
        steps_html = '<ol class="steps-list">'
        for step in result.steps:
            steps_html += '<li>' + _safe(step) + '</li>'
        steps_html += '</ol>'

        savings_html = ''
        if result.savings_range is not None:
            savings_html = (
                '<div class="savings-box">💰 Illustrative savings: '
                + _safe(format_savings(result.savings_range))
                + '</div>'
            )

        card_html = (
            '<div class="program-card">'
            '<div class="program-card-name">' + result.rule.name + '</div>'
            '<span class="status-pill ' + css_cls + '">'
            + pill_prefix + ' &nbsp;' + label
            + '</span>'
            '<div class="card-explanation">' + _safe(result.explanation) + '</div>'
            + savings_html
            + '<div style="font-weight:700;font-size:0.88rem;color:#0d2b55;margin-bottom:0.4rem">'
            'Suggested next steps</div>'
            + steps_html
            + '<div class="card-footer">'
            '<span>Policy review: ' + result.rule.policy_review_date + '</span>'
            '</div>'
            '</div>'
        )
        _render_html(card_html)
        # Official link button — rendered via Streamlit (not HTML) for keyboard/accessibility
        st.link_button(
            'Official program information ↗  — ' + result.rule.name,
            result.rule.source_url,
        )

    # ------------------------------------------------------------------
    # Benefit Domino Effect graph
    # ------------------------------------------------------------------
    st.markdown(
        '<div class="section-title" style="margin-top:1.4rem">🔗 Benefit Domino Effect</div>',
        unsafe_allow_html=True,
    )
    fig = render_benefit_graph(h, results)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        '<div class="graph-explanation">'
        + _safe(_domino_explanation(h, results))
        + '</div>',
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # Footer disclaimer
    # ------------------------------------------------------------------
    st.markdown(
        '<div class="disclaimer-footer">⚠️ ' + FOOTER_DISCLAIMER + '</div>',
        unsafe_allow_html=True,
    )

else:
    # How-to intro panel
    _render_html("""
<div class="how-to-panel">
  <div class="section-title">How it works</div>
  <div class="how-to-step">
    <div class="how-to-num">1</div>
    <div class="how-to-text">
      <strong>Enter your household details</strong>
      <span>Household size, approximate income, and any programs you currently receive.</span>
    </div>
  </div>
  <div class="how-to-step">
    <div class="how-to-num">2</div>
    <div class="how-to-text">
      <strong>Get preliminary screening results</strong>
      <span>See which programs may have pathways worth exploring, with plain-English explanations.</span>
    </div>
  </div>
  <div class="how-to-step">
    <div class="how-to-num">3</div>
    <div class="how-to-text">
      <strong>Explore the Benefit Domino Effect</strong>
      <span>See how qualifying for one program can open pathways to others.</span>
    </div>
  </div>
  <div class="how-to-step" style="margin-bottom:0">
    <div class="how-to-num">4</div>
    <div class="how-to-text">
      <strong>Follow official links to apply</strong>
      <span>Every result includes an official government source and a suggested next-steps checklist.</span>
    </div>
  </div>
  <p style="margin-top:1rem;font-size:0.82rem;color:#7a8fa6">
    All results are preliminary screening only — not official eligibility decisions.
    Contact the program directly to apply.
  </p>
</div>
""")

# ---------------------------------------------------------------------------
# Official resources — always visible
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-title" style="margin-top:1.6rem">🔗 Official Resources</div>',
    unsafe_allow_html=True,
)
_render_html("""
<div class="resources-grid">
  <a class="resource-link" href="https://www.usac.org/lifeline/consumer-eligibility/" target="_blank">
    📶 USAC Lifeline Eligibility
  </a>
  <a class="resource-link" href="https://www.michigan.gov/mdhhs/assistance-programs/food/eligibility" target="_blank">
    🌽 Michigan SNAP Eligibility
  </a>
  <a class="resource-link" href="https://www.michigan.gov/mdhhs/assistance-programs/emergency-relief/eligibility" target="_blank">
    ⚡ Michigan State Emergency Relief
  </a>
  <a class="resource-link" href="https://newmibridges.michigan.gov/" target="_blank">
    🌉 MI Bridges — Apply Online
  </a>
</div>
""")

st.markdown(
    '<p style="font-size:0.78rem;color:#7a8fa6;text-align:center;margin-top:0.8rem">'
    'Last policy review: 2026-11-22. '
    'BenefitChain AI is not affiliated with USAC or Michigan MDHHS.</p>',
    unsafe_allow_html=True,
)

