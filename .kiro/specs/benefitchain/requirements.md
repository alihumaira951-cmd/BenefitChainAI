equirements Document

## Introduction

BenefitChain AI is a Python + Streamlit hackathon MVP that helps Michigan residents screen for three government assistance programs: the Lifeline phone/internet discount, the SNAP Food Assistance Program, and Michigan State Emergency Relief (SER) for energy emergencies. The application collects minimal household information, runs transparent rule-based screening logic, and presents results as preliminary pathways — never as official eligibility determinations. A benefit-graph visualization shows how qualifying for one program can open pathways to others ("domino effect"). All program rules are stored in-process; no external APIs, databases, or authentication are required.

## Glossary

- **Application**: The BenefitChain AI Streamlit web application.
- **Engine**: The pure-Python screening module (`engine.py`) with no Streamlit dependency.
- **Household**: The set of people whose combined income and program participation is being evaluated.
- **Lifeline**: The federally administered telephone and internet discount program administered by USAC.
- **SNAP**: The Supplemental Nutrition Assistance Program, administered in Michigan by MDHHS via MI Bridges.
- **SER**: Michigan State Emergency Relief, administered by MDHHS; covers energy and utility emergencies.
- **FPHA**: Federal Public Housing Assistance.
- **USAC**: Universal Service Administrative Company, the administrator of the Lifeline program.
- **MDHHS**: Michigan Department of Health and Human Services.
- **MI Bridges**: The official Michigan online portal for applying to state assistance programs (https://newmibridges.michigan.gov).
- **FPG**: Federal Poverty Guideline; the Lifeline income threshold is set at 135% FPG.
- **Session State**: Streamlit's in-memory per-session data store, which persists only for the duration of a browser session.
- **Status Code**: One of five string values the Engine returns for a Lifeline screening result: `LIKELY_QUALIFIES_INCOME`, `LIKELY_QUALIFIES_PROGRAM`, `ALREADY_RECEIVING`, `NOT_INDICATED`, or `INCOMPLETE_DATA`.
- **Pathway**: A route by which a household may qualify for a program, requiring a separate official application; never an approval.
- **Policy Review Date**: The date on which the program rules embedded in the Application were last verified against official sources.

---

## Requirements

### Requirement 1: Household Questionnaire

**User Story:** As a Michigan resident, I want to enter basic household information through a simple form, so that I can receive preliminary benefit screening without providing sensitive personal data.

#### Acceptance Criteria

1. WHEN the Application loads for a new session, THE Application SHALL display all form fields in a blank or neutral default state with no benefit participation checkboxes pre-selected.
2. THE Application SHALL provide a clearly labeled "Try sample household" button that, when activated, populates all fields with synthetic demo data and displays a visible notice reading "Demo data loaded — this is a fictional household for illustration."
3. WHEN the "Try sample household" button is activated, THE Application SHALL populate the form with a household of size 3, annual income of $28,000, SNAP and Medicaid checkboxes selected, all other checkboxes cleared, and energy emergency set to No.
4. WHEN a user enters a household size that is not a positive integer, THE Application SHALL display an inline validation error and SHALL NOT submit the form for screening.
5. WHEN a user enters an income value that is negative, THE Application SHALL display an inline validation error and SHALL NOT submit the form for screening.
6. THE Application SHALL display the following privacy notice at the top of the questionnaire: "BenefitChain AI uses the information you enter to provide preliminary benefit screening. Your responses are processed by the application server during your session. We do not ask for names, Social Security numbers, or case numbers, and the application is designed not to save household profiles to a permanent database. Please do not enter sensitive identifying information."
7. THE Application SHALL render all questionnaire fields correctly on viewports as narrow as 320 pixels wide.
8. THE Application SHALL be fully operable using keyboard navigation alone, with no mouse required to complete and submit the form.

---

### Requirement 2: Lifeline Eligibility Screening Engine

**User Story:** As a Michigan resident, I want the application to check whether my household may qualify for the Lifeline discount, so that I can understand whether it is worth applying.

#### Acceptance Criteria

1. THE Engine SHALL calculate the Lifeline income threshold as $21,546 for a household of one person, plus $7,668 for each additional person, based on USAC 2026 guidelines (source: https://www.usac.org/lifeline/).
2. THE Engine SHALL recognize each of the following as an independent program-based qualification pathway: SNAP, Medicaid, SSI, FPHA, and Veterans Pension/Survivor Benefit.
3. THE Engine SHALL return exactly one of five Status Codes for every Lifeline screening result: `LIKELY_QUALIFIES_INCOME`, `LIKELY_QUALIFIES_PROGRAM`, `ALREADY_RECEIVING`, `NOT_INDICATED`, or `INCOMPLETE_DATA`.
4. WHEN the household indicates they already receive Lifeline, THE Engine SHALL return the Status Code `ALREADY_RECEIVING` and THE Application SHALL display a plain-English explanation of the one-benefit-per-household rule.
5. WHEN the household income is at or below the calculated threshold and no program-based pathway applies, THE Engine SHALL return the Status Code `LIKELY_QUALIFIES_INCOME`.
6. WHEN the household participates in at least one qualifying program regardless of income, THE Engine SHALL return the Status Code `LIKELY_QUALIFIES_PROGRAM`.
7. WHEN the household income exceeds the calculated threshold and no qualifying program participation is reported, THE Engine SHALL return the Status Code `NOT_INDICATED`.
8. WHEN household size is less than one or income is negative, THE Engine SHALL return the Status Code `INCOMPLETE_DATA` or raise a `ValueError`.
9. THE Application SHALL label all Lifeline results as "Potential Qualification Pathway" and SHALL NOT use the words "eligible," "approved," or "guaranteed" in any Lifeline result.
10. THE Engine SHALL store each program rule record with the fields: program name, official source URL, and effective year.
11. THE Engine SHALL be implemented as pure Python functions with no import of any Streamlit module, so that it can be executed in a plain pytest environment.

---

### Requirement 3: SNAP Screening (Referral Only)

**User Story:** As a Michigan resident, I want to know whether my household might qualify for SNAP, so that I can decide whether to apply through MI Bridges.

#### Acceptance Criteria

1. THE Engine SHALL evaluate potential SNAP eligibility using household size and gross annual income as rough indicators only, without applying Michigan-specific deductions or categorical rules.
2. THE Application SHALL label all SNAP results as "Preliminary Screening — Refer to MI Bridges" and SHALL NOT display the words "Eligible" or "Approved" in any SNAP result.
3. THE Application SHALL NOT display an estimated monthly or annual SNAP benefit dollar amount derived from household income alone.
4. THE Application SHALL display a direct link to MI Bridges (https://newmibridges.michigan.gov) as the official application channel for SNAP.
5. THE Application SHALL display the disclaimer: "SNAP eligibility involves Michigan-specific income deductions, household composition rules, and other criteria not evaluated by this tool."

---

### Requirement 4: Michigan SER Screening (Emergency Referral Only)

**User Story:** As a Michigan resident facing an energy emergency, I want to be referred to State Emergency Relief quickly, so that I can contact the right agency before a shutoff occurs.

#### Acceptance Criteria

1. WHEN the household indicates an active energy emergency, THE Application SHALL surface the SER program card with the status label "Emergency Referral."
2. WHEN the household does not indicate an energy emergency, THE Application SHALL display SER with a status label indicating it was not triggered and SHALL NOT present it as an active recommendation.
3. THE Application SHALL include the official MDHHS SER program link (https://www.michigan.gov/mdhhs/assistance-programs/emergency-relief/eligibility) in the SER program card.
4. THE Application SHALL NOT display an estimated dollar assistance amount for SER.
5. THE Application SHALL NOT use the words "approved," "guaranteed," or "will receive" in any SER result.
6. THE Application SHALL display the disclaimer: "SER assistance requires a caseworker review by MDHHS. This tool cannot replicate that review or guarantee assistance."

---

### Requirement 5: Benefit Graph (Domino Effect Visualization)

**User Story:** As a Michigan resident, I want to see a visual map of how my current benefits connect to other programs, so that I understand why qualifying for one benefit can open a pathway to another.

#### Acceptance Criteria

1. THE Application SHALL render an interactive Plotly figure, built using NetworkX for graph construction, embedded in the Streamlit page.
2. THE Application SHALL display directed edges from SNAP to Lifeline and from Medicaid to Lifeline, each explicitly labeled as a qualification pathway.
3. WHEN a directed edge is displayed, THE Application SHALL include an edge label stating the verification step required (e.g., "Proof of SNAP participation required").
4. THE Application SHALL distinguish node visual states using both a color and a text label (not color alone) for: programs the household likely qualifies for, programs already receiving, and programs not indicated by the household's inputs.
5. THE Application SHALL label every graph edge as a "pathway requiring a separate application" and SHALL NOT imply automatic enrollment.
6. THE Application SHALL display a plain-English "Benefit Domino Effect" explanation beneath the graph describing how qualifying for one program can open pathways to others.

---

### Requirement 6: Dashboard and Program Cards

**User Story:** As a Michigan resident, I want a clear results dashboard with one card per program, so that I know exactly what my next steps are for each benefit.

#### Acceptance Criteria

1. THE Application SHALL display a summary section showing the count of programs for which a potential pathway was identified.
2. THE Application SHALL display one card per program, each containing: a status label, a plain-English explanation, an official source link button, and a numbered action checklist.
3. THE Application SHALL phrase each action checklist item in the imperative (e.g., "Visit MI Bridges to begin your SNAP application").
4. THE Application SHALL display a persistent disclaimer footer reading: "This tool provides preliminary screening only. Results are not an official eligibility determination. Contact the program directly to apply."
5. THE Application SHALL display an estimated Lifeline savings range based on the fixed monthly USAC telecom discount and SHALL NOT display estimated dollar amounts for SNAP or SER.
6. THE Application SHALL display the Policy Review Date for each program rule record within the corresponding program card.

---

### Requirement 7: Automated Test Suite

**User Story:** As a developer, I want a pytest suite covering key screening scenarios, so that I can verify the Engine behaves correctly without manual testing.

#### Acceptance Criteria

1. THE Test_Suite SHALL include a test that provides a household whose income equals the Lifeline threshold for a given size and asserts the Engine returns `LIKELY_QUALIFIES_INCOME`.
2. THE Test_Suite SHALL include a test that provides a household whose income is exactly $1 above the Lifeline threshold and asserts the Engine returns `NOT_INDICATED` for the income pathway.
3. THE Test_Suite SHALL include a test that provides household size = 0 and asserts the Engine raises `ValueError` or returns `INCOMPLETE_DATA`.
4. THE Test_Suite SHALL include a test that provides household size = -1 and asserts the Engine raises `ValueError` or returns `INCOMPLETE_DATA`.
5. THE Test_Suite SHALL include a test that provides a non-integer household size (e.g., 2.5) and asserts the Engine raises `ValueError` or returns `INCOMPLETE_DATA`.
6. THE Test_Suite SHALL include a test that provides a household already receiving Lifeline and asserts the Engine returns `ALREADY_RECEIVING` with a result that contains one-benefit-per-household explanation text.
7. THE Test_Suite SHALL include a test that provides income above the Lifeline threshold with SNAP participation checked and asserts the Engine returns `LIKELY_QUALIFIES_PROGRAM`.
8. THE Test_Suite SHALL include a test that asserts no SNAP result returned by the Engine contains a numeric dollar benefit estimate.
9. THE Test_Suite SHALL include a test that asserts no SER result returned by the Engine contains the words "approved," "guaranteed," or "will receive."
10. THE Test_Suite SHALL execute using plain pytest with no network calls and no import of any Streamlit module.

---

### Requirement 8: Privacy and Data Handling

**User Story:** As a Michigan resident, I want to understand exactly how my household information is handled, so that I can decide whether to use the tool without fear of data exposure.

#### Acceptance Criteria

1. THE Application SHALL NOT collect names, Social Security numbers, case numbers, addresses, phone numbers, or email addresses.
2. THE Application SHALL store household data exclusively in Streamlit Session State during the active session and SHALL NOT write household data to any file, database, or external service.
3. THE Application SHALL display the exact privacy notice text specified in Requirement 1, Acceptance Criterion 6 within the household questionnaire.
4. THE Application SHALL NOT display any claim that household data is deleted immediately upon tab close, because Streamlit Session State is held on the application server.
5. THE Application SHALL NOT make any data-handling claim that cannot be verified from the application's actual Streamlit session behavior.

---

### Requirement 9: Hackathon MVP Scope and Constraints

**User Story:** As a developer and judge, I want the application to be a self-contained, demonstrable Streamlit MVP, so that it can be run and evaluated without external infrastructure.

#### Acceptance Criteria

1. THE Application SHALL operate without any paid external API, external database, authentication system, or persistent backend storage.
2. THE Engine SHALL store all program rules and income thresholds as in-process Python data structures (dicts or dataclasses) with no external configuration files required at runtime.
3. WHEN a user submits the household form, THE Application SHALL complete screening and render the full results dashboard within 3 seconds on a standard laptop under no load.
4. THE Application SHALL display the Policy Review Date for each program rule record in the UI so that users and judges can verify how current the rules are.
5. THE Application SHALL be demonstrable end-to-end — from form entry through results and benefit graph — within three minutes.
