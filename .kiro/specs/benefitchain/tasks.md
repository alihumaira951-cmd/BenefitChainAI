# Implementation Plan: BenefitChain AI

## Overview

This plan extends the existing `engine.py`, `app.py`, `tests/test_engine.py`, and `requirements.txt` files to match the approved design. Tasks are ordered so each step builds on the previous: dependencies first, then engine data models, then screening logic, then the graph module, then the UI, then tests. No existing file is rewritten from scratch; all changes are additive or targeted replacements.

## Tasks

- [x] 1. Python dependencies and project setup
  - Add `networkx>=3.3` and `plotly>=5.22` to `requirements.txt` (append after existing lines).
  - Create `graph.py` in the project root as a new module containing only a module-level docstring: `"""Benefit Domino Effect graph — NetworkX + Plotly. No Streamlit imports."""`
  - Verify `python -c "import graph"` succeeds without errors.
  - _Requirements: 5.1, 9.1_

- [x] 2. Household data models and validation
  - [x] 2.1 Define data model classes and alias in `engine.py`
    - Replace the existing `@dataclass(frozen=True) class Household` definition with `HouseholdInput` (identical fields: `state`, `size`, `annual_income`, `snap`, `medicaid`, `ssi`, `public_housing`, `veterans_pension`, `utility_emergency`, `lifeline_already` — all with the same defaults as today).
    - Add backward-compatibility alias immediately after: `Household = HouseholdInput`.
    - Add `LifelineStatus(str, Enum)` with exactly five members: `LIKELY_QUALIFIES_INCOME`, `LIKELY_QUALIFIES_PROGRAM`, `ALREADY_RECEIVING`, `NOT_INDICATED`, `INCOMPLETE_DATA`.
    - Add `ProgramRule` frozen dataclass with fields: `name: str`, `source_url: str`, `effective_year: int`, `policy_review_date: str`.
    - Add `SavingsRange` frozen dataclass with fields: `monthly_max: float`, `annual_max: float`, `note: str`.
    - Add `ScreeningResult` frozen dataclass with fields: `rule: ProgramRule`, `status: LifelineStatus | str`, `explanation: str`, `steps: list[str]`, `savings_range: Optional[SavingsRange] = None`.
    - _Requirements: 2.3, 2.8, 2.10_

  - [x] 2.2 Add `validate_household()` function to `engine.py`
    - Implement `validate_household(h: HouseholdInput) -> None` that raises `ValueError("Household size must be a positive integer")` when `h.size < 1` or `not isinstance(h.size, int)`, and raises `ValueError("Annual income must be non-negative")` when `h.annual_income < 0`.
    - Call `validate_household(h)` as the first statement inside `screen()`.
    - _Requirements: 2.8_

  - [ ]* 2.3 Write unit tests for data model validation
    - Add temporary sanity assertions (or run interactively) confirming: `HouseholdInput('Michigan', 2, 30000)` constructs without error; `Household` alias resolves to `HouseholdInput`; `LifelineStatus.LIKELY_QUALIFIES_INCOME` has string value `"LIKELY_QUALIFIES_INCOME"`.
    - _Requirements: 2.3, 2.8_

- [x] 3. Lifeline screening logic and program rule constants
  - [x] 3.1 Add engine constants to `engine.py`
    - Replace the existing `LIFELINE_2026` dict with the same values (no change needed if already correct: `{1: 21546, …, 8: 75222}`).
    - Add `LIFELINE_PER_ADDITIONAL_PERSON: int = 7668`.
    - Add `LIFELINE_STANDARD_MONTHLY_MAX: float = 9.25`.
    - Add `LIFELINE_STANDARD_ANNUAL_MAX: float = 111.0`.
    - Add `LIFELINE_SAVINGS_NOTE: str = "actual discount depends on service provider and program rules"`.
    - Add `LIFELINE_RULE`, `SNAP_RULE`, `SER_RULE` as `ProgramRule` instances with `name`, `source_url`, `effective_year=2026`, `policy_review_date="2026-11-22"` as specified in `design.md`.
    - _Requirements: 2.1, 2.10, 6.6, 9.4_

  - [x] 3.2 Update `lifeline_income_limit()` in `engine.py`
    - Keep the existing function signature `lifeline_income_limit(size: int) -> int`.
    - Replace the body to use `LIFELINE_PER_ADDITIONAL_PERSON` for the extrapolation: `return LIFELINE_2026[8] + (size - 8) * LIFELINE_PER_ADDITIONAL_PERSON` for `size > 8`.
    - _Requirements: 2.1_

  - [x] 3.3 Implement `screen_lifeline()` in `engine.py`
    - Add `screen_lifeline(h: HouseholdInput) -> ScreeningResult`.
    - Apply the decision table from `design.md` in order: `lifeline_already` → `ALREADY_RECEIVING` (explanation must contain "one benefit per household", `savings_range=None`); any qualifying program flag → `LIKELY_QUALIFIES_PROGRAM` (`savings_range=SavingsRange(9.25, 111.0, LIFELINE_SAVINGS_NOTE)`); income at or below threshold → `LIKELY_QUALIFIES_INCOME` (same `SavingsRange`); otherwise → `NOT_INDICATED` (`savings_range=None`).
    - Use `LIFELINE_RULE` as the `rule` field.
    - Explanation strings must never contain "eligible", "approved", or "guaranteed".
    - _Requirements: 2.2, 2.4, 2.5, 2.6, 2.7, 2.9_

  - [ ]* 3.4 Write property test for income threshold formula (Property 1)
    - **Property 1: Income threshold formula is universal**
    - **Validates: Requirements 2.1**
    - In `tests/test_engine.py`, add an optional Hypothesis test using `from hypothesis import given, settings` and `from hypothesis import strategies as hst`. Decorate with `@given(size=hst.integers(min_value=1, max_value=50))` and `@settings(max_examples=100)`. Assert `lifeline_income_limit(size) == 21546 + (size - 1) * 7668`. Do not add `hypothesis` to `requirements.txt`.

  - [ ]* 3.5 Write property test for program-based qualification (Property 2)
    - **Property 2: Any single qualifying program triggers LIKELY_QUALIFIES_PROGRAM regardless of income**
    - **Validates: Requirements 2.2, 2.6**
    - Use Hypothesis to generate incomes above threshold and each individual qualifying program flag. Assert `screen(h)[0].status == LifelineStatus.LIKELY_QUALIFIES_PROGRAM`.

- [x] 4. SNAP and Michigan SER referral logic
  - [x] 4.1 Implement `screen_snap()` in `engine.py`
    - Add `screen_snap(h: HouseholdInput) -> ScreeningResult`.
    - Status: `"already_receiving"` if `h.snap` is `True`, else `"needs_review"`.
    - `savings_range` is always `None`.
    - Explanation must include the Requirement 3.5 disclaimer: "SNAP eligibility involves Michigan-specific income deductions, household composition rules, and other criteria not evaluated by this tool."
    - Explanation must not contain any pattern matching `\$\d+`.
    - Steps must include MI Bridges URL `https://newmibridges.michigan.gov`.
    - Use `SNAP_RULE` as the `rule` field.
    - _Requirements: 3.1, 3.3, 3.4, 3.5_

  - [x] 4.2 Implement `screen_ser()` in `engine.py`
    - Add `screen_ser(h: HouseholdInput) -> ScreeningResult`.
    - Status: `"urgent_referral"` if `h.utility_emergency` is `True`, else `"needs_review"`.
    - `savings_range` is always `None`.
    - Explanation must not contain "approved", "guaranteed", or "will receive".
    - When `utility_emergency=True`, explanation must surface SER as an emergency referral (use wording such as "Contact MDHHS via MI Bridges promptly").
    - Use `SER_RULE` as the `rule` field.
    - _Requirements: 4.1, 4.2, 4.4, 4.5, 4.6_

  - [x] 4.3 Update `screen()` in `engine.py` to return `list[ScreeningResult]`
    - Replace the body of the existing `screen()` function to: call `validate_household(h)`, handle non-Michigan state by returning a single `ScreeningResult` with `status="out_of_scope"`, then call `screen_lifeline(h)`, `screen_snap(h)`, `screen_ser(h)` and return them as `[lifeline_result, snap_result, ser_result]`.
    - Remove the old dict-based return logic.
    - _Requirements: 2.3, 3.1, 4.1_

  - [ ]* 4.4 Write property test for SER status (Property 7)
    - **Property 7: SER status reflects utility_emergency flag universally**
    - **Validates: Requirements 4.1, 4.2**
    - Use Hypothesis to generate arbitrary valid `HouseholdInput` values. Assert: when `utility_emergency=True`, `screen(h)[2].status == "urgent_referral"`; when `utility_emergency=False`, `screen(h)[2].status != "urgent_referral"`.

  - [ ]* 4.5 Write property test for SNAP no-dollar guarantee (Property 8)
    - **Property 8: SNAP result never contains a numeric dollar estimate**
    - **Validates: Requirements 3.3**
    - Use Hypothesis. Assert `screen(h)[1].savings_range is None` and `screen(h)[1].explanation` does not match `\$\d+`.

- [x] 5. Benefit Domino Effect graph
  - [x] 5.1 Implement `build_benefit_graph()` in `graph.py`
    - Import `networkx as nx` and engine types (`HouseholdInput`, `ScreeningResult`, `LifelineStatus`).
    - Add four nodes: `"SNAP"`, `"Medicaid"`, `"Lifeline"`, `"SER"`.
    - Add two directed edges: `"SNAP" → "Lifeline"` with attribute `label="Proof of SNAP participation required"` and `pathway=True`; `"Medicaid" → "Lifeline"` with attribute `label="Proof of Medicaid enrollment required"` and `pathway=True`.
    - Assign node attribute `state` per the node state table in `design.md`: SNAP/Medicaid from `household.snap`/`household.medicaid`; Lifeline from `results[0].status`; SER from `results[2].status`.
    - Return the populated `nx.DiGraph`.
    - _Requirements: 5.1, 5.2, 5.3, 5.5_

  - [x] 5.2 Implement `render_benefit_graph()` in `graph.py`
    - Import `plotly.graph_objects as go`.
    - Call `build_benefit_graph()` to get the graph.
    - Compute node positions (use a fixed layout dict: SNAP top-left, Medicaid bottom-left, Lifeline center-right, SER bottom-right; e.g., `{"SNAP": (0, 1), "Medicaid": (0, 0), "Lifeline": (1, 0.5), "SER": (2, 0)}`).
    - Map each node `state` to both a marker color and a text label suffix — `"qualifies"` → green / `"(Potential Pathway)"`; `"already_receiving"` → `"#4a90d9"` (blue) / `"(Already Receiving)"`; `"not_indicated"` → `"#aaaaaa"` (gray) / `"(Not Indicated)"`.
    - Build edge traces as `go.Scatter` with `mode="lines"`, and node traces as `go.Scatter` with `mode="markers+text"` where `text` is `"{node_name}\n{state_suffix}"`.
    - Return a `go.Figure` with a plain white background and no axis lines.
    - If `results` is empty, return an empty `go.Figure` without raising.
    - _Requirements: 5.1, 5.3, 5.4, 5.5_

  - [ ]* 5.3 Write unit tests for graph node states
    - Confirm that a household with `snap=True` produces a SNAP node with `state="already_receiving"`.
    - Confirm that a household producing `LIKELY_QUALIFIES_PROGRAM` Lifeline status gets a Lifeline node with `state="qualifies"`.
    - Confirm that both directed edges are present in the returned DiGraph.
    - _Requirements: 5.2, 5.4_

- [x] 6. Streamlit questionnaire and sample household
  - [x] 6.1 Rewrite `app.py` page config and layout constants
    - Change `st.set_page_config` to `layout="centered"` (not `"wide"`).
    - Remove all `st.sidebar` and `with st.sidebar:` blocks entirely.
    - Define module-level constants: `PRIVACY_NOTICE` (verbatim text from `design.md`) and `FOOTER_DISCLAIMER` (verbatim text from `design.md`).
    - _Requirements: 1.7, 8.3_

  - [x] 6.2 Implement the questionnaire form in `app.py`
    - After the page title and caption, render `st.info(PRIVACY_NOTICE)`.
    - Build a `st.form("household_form")` containing: `st.number_input` for household size (integer, min 1); `st.number_input` for annual income (float, min 0); seven `st.checkbox` widgets for `snap`, `medicaid`, `ssi`, `public_housing`, `veterans_pension`, `utility_emergency`, `lifeline_already`.
    - Outside (above) the form, add a `st.button("Try sample household")` that sets `st.session_state` keys to: `household_size=3`, `annual_income=28000`, `snap=True`, `medicaid=True`, all others `False`, then calls `st.rerun()`. Display `st.info("Demo data loaded — this is a fictional household for illustration.")` when demo data is active.
    - Inside the form, add `st.form_submit_button("Screen my household")` as the submission control.
    - _Requirements: 1.1, 1.2, 1.3, 1.6, 1.8_

  - [x] 6.3 Add inline validation and `screen()` call in `app.py`
    - On form submit: if `household_size < 1` or not a positive integer → `st.error(...)` and stop.
    - If `annual_income < 0` → `st.error(...)` and stop.
    - Otherwise construct `HouseholdInput('Michigan', household_size, annual_income, …)` and call `screen(h)`.
    - Store results in a local variable for use by the dashboard section below.
    - _Requirements: 1.4, 1.5_

- [x] 7. Results dashboard, savings display, and official links
  - [x] 7.1 Add summary metrics section to `app.py`
    - After a successful `screen()` call, display `st.metric("Programs Reviewed", 3)`.
    - Compute `pathway_count` = count of results where status is `LIKELY_QUALIFIES_INCOME` or `LIKELY_QUALIFIES_PROGRAM`.
    - Display `st.metric("Potential Pathways Identified", pathway_count)`.
    - _Requirements: 6.1_

  - [x] 7.2 Render program cards in `app.py`
    - Add `format_savings(sr: SavingsRange) -> str` function: returns `f"Up to ${sr.monthly_max:.2f}/month (${sr.annual_max:.0f}/year) — {sr.note}"`.
    - For each `ScreeningResult` in the list from `screen()`, render a `st.container(border=True)` block containing: program name as `st.subheader`; a text status label (not color alone) using a plain-text mapping dict; `result.explanation` as body text; Lifeline card only: `format_savings(result.savings_range)` output when `savings_range` is not `None`; numbered action checklist from `result.steps`; `st.link_button("Official program information", result.rule.source_url)`; Policy Review Date shown as `st.caption(f"Policy Review Date: {result.rule.policy_review_date}")`.
    - SNAP and SER cards must not display any dollar estimate.
    - _Requirements: 6.2, 6.3, 6.4, 6.5, 6.6_

  - [x] 7.3 Add benefit graph and footer to `app.py`
    - Import `render_benefit_graph` from `graph`.
    - After program cards, add `st.subheader("Benefit Domino Effect")`.
    - Call `render_benefit_graph(h, results)` and render with `st.plotly_chart(fig, use_container_width=True)`.
    - Below the chart, render the plain-English "Benefit Domino Effect" explanation paragraph from `design.md` (Requirement 5.6).
    - At page bottom, render `st.caption(FOOTER_DISCLAIMER)`.
    - Add official resources links section (four links matching the existing `app.py` footer).
    - _Requirements: 5.1, 5.6, 6.4_

- [x] 8. Accessibility, privacy notices, and mobile usability
  - [x] 8.1 Audit and fix text-only status labels in `app.py`
    - Replace any color-only status indicators with a dict that maps status codes to plain-text labels (e.g., `"LIKELY_QUALIFIES_INCOME"` → `"Potential Qualification Pathway (income-based)"`, `"LIKELY_QUALIFIES_PROGRAM"` → `"Potential Qualification Pathway (program-based)"`, `"ALREADY_RECEIVING"` → `"Already Receiving"`, `"NOT_INDICATED"` → `"Not Indicated"`, `"needs_review"` → `"Preliminary Screening — Refer to MI Bridges"`, `"urgent_referral"` → `"Emergency Referral"`, `"already_receiving"` → `"Already Receiving"`, `"out_of_scope"` → `"Outside Coverage Area"`).
    - Confirm no SNAP card shows "Eligible" or "Approved" per Requirements 3.2.
    - _Requirements: 5.4, 3.2, 4.1, 4.2_

  - [x] 8.2 Confirm keyboard navigation and viewport in `app.py`
    - Ensure no `st.sidebar` controls remain (all inputs in main column).
    - Confirm form submit is `st.form_submit_button`, reachable by Enter key.
    - Confirm `layout="centered"` is set so narrow viewports (320px+) render correctly.
    - _Requirements: 1.7, 1.8_

- [x] 9. Automated test suite
  - [x] 9.1 Rewrite `tests/test_engine.py` with Requirement 7 test functions
    - Replace the current dict-based access (`result['status']`, `result['annual_max']`) with dataclass attribute access (`result.status`, `result.savings_range.annual_max`).
    - Keep `from engine import Household, screen, lifeline_income_limit` working (alias must hold).
    - Also import `HouseholdInput, LifelineStatus, ScreeningResult` for new assertions.
    - Implement the following ten test functions:
      - `test_income_at_threshold_qualifies`: `size=1, income=21546` → `result.status == LifelineStatus.LIKELY_QUALIFIES_INCOME`.
      - `test_income_one_above_threshold`: `size=1, income=21547` → `result.status == LifelineStatus.NOT_INDICATED`.
      - `test_size_zero_invalid`: `size=0` → raises `ValueError` or returns `LifelineStatus.INCOMPLETE_DATA`.
      - `test_size_negative_invalid`: `size=-1` → raises `ValueError` or returns `LifelineStatus.INCOMPLETE_DATA`.
      - `test_non_integer_size_invalid`: `size=2.5` → raises `ValueError` or returns `LifelineStatus.INCOMPLETE_DATA`.
      - `test_already_receiving_lifeline`: `lifeline_already=True` → `result.status == LifelineStatus.ALREADY_RECEIVING` and `"one benefit per household"` in `result.explanation`.
      - `test_snap_participation_above_threshold`: `income=60000, snap=True` → `result.status == LifelineStatus.LIKELY_QUALIFIES_PROGRAM`.
      - `test_snap_result_no_dollar_estimate`: for any household, `screen(h)[1].savings_range is None` and `screen(h)[1].explanation` does not match `\$\d+`.
      - `test_ser_result_no_forbidden_words`: `screen(h)[2].explanation` contains none of "approved", "guaranteed", "will receive".
      - `test_no_streamlit_import`: `import engine` does not cause `import streamlit` to execute.
    - _Requirements: 7.1–7.10_

  - [ ]* 9.2 Add optional Hypothesis property tests to `tests/test_engine.py`
    - Import with `from hypothesis import given, settings` and `from hypothesis import strategies as hst` (not `as st`, to avoid collision with Streamlit's `st`).
    - Guard the entire block with `try: import hypothesis; HAS_HYPOTHESIS = True except ImportError: HAS_HYPOTHESIS = False` and skip if not installed.
    - Property 1 test: `@given(size=hst.integers(min_value=1, max_value=50))` with `@settings(max_examples=100)` asserting `lifeline_income_limit(size) == 21546 + (size - 1) * 7668`.
    - Property 4 test: `@given(...)` with `lifeline_already=True` asserting `screen(h)[0].status == LifelineStatus.ALREADY_RECEIVING`.
    - Do NOT add `hypothesis` to `requirements.txt`.
    - _Requirements: 7.1 (property extension)_

- [-] 10. Final checkpoint — verify tests pass and app runs
  - Run `pytest tests/ -v` and confirm all 10 required test functions pass with no Streamlit import errors.
  - Launch `streamlit run app.py` manually and walk through: blank form load → "Try sample household" → verify "Demo data loaded" message → submit → review three program cards → review benefit graph → verify no forbidden words → verify Policy Review Date visible → verify disclaimer footer visible.
  - Confirm end-to-end `screen()` call completes in under 3 seconds on a standard laptop.
  - Confirm no SNAP or SER card shows a dollar estimate.
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP iteration.
- Each task references specific requirements for traceability.
- The `Household = HouseholdInput` alias in `engine.py` must remain intact so existing imports in `tests/test_engine.py` and the existing `app.py` continue to work during migration.
- When writing Hypothesis tests, always import strategies as `hst` (not `st`) to avoid shadowing Streamlit's `st` module in any file that also imports Streamlit.
- Hypothesis is optional; do not add it to `requirements.txt`.
- SER is never presented as a confirmed qualification — always use "Emergency Referral" label in the UI.
- SNAP and SER `savings_range` must always be `None`; no dollar amounts are estimated for those programs.
- Property-based tests validate universal correctness properties; unit tests validate specific examples and edge cases. Both are complementary.
- Checkpoints ensure incremental validation at natural breaks between engine work, graph work, UI work, and final testing.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2"] },
    { "id": 3, "tasks": ["2.3", "3.1"] },
    { "id": 4, "tasks": ["3.2"] },
    { "id": 5, "tasks": ["3.3"] },
    { "id": 6, "tasks": ["3.4", "3.5", "4.1", "4.2"] },
    { "id": 7, "tasks": ["4.3"] },
    { "id": 8, "tasks": ["4.4", "4.5", "5.1"] },
    { "id": 9, "tasks": ["5.2"] },
    { "id": 10, "tasks": ["5.3", "6.1"] },
    { "id": 11, "tasks": ["6.2"] },
    { "id": 12, "tasks": ["6.3"] },
    { "id": 13, "tasks": ["7.1"] },
    { "id": 14, "tasks": ["7.2"] },
    { "id": 15, "tasks": ["7.3"] },
    { "id": 16, "tasks": ["8.1"] },
    { "id": 17, "tasks": ["8.2"] },
    { "id": 18, "tasks": ["9.1"] },
    { "id": 19, "tasks": ["9.2"] },
    { "id": 20, "tasks": ["10"] }
  ]
}
```
