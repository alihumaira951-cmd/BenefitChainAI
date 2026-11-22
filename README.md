# BenefitChain AI — Michigan public assistance discovery prototype

Built November 22, 2026 as a hackathon *starter prototype*. **Not yet a Devpost submission, deployed service, or verified Kiro-built deliverable.**

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

In another terminal run tests: `python -m pytest -q`.

## What works
- Michigan household questionnaire using non-identifying inputs
- Lifeline program-participation/income pathway screening using USAC 2026 rules
- Benefit Domino Effect: SNAP/Medicaid -> Lifeline
- Referral-only screening for Michigan SNAP and State Emergency Relief
- Official source links, next steps, no invented SNAP or emergency relief payouts

## Not yet done
- Official integration, validation across dozens of programs, live funding status, AI-generated explanations, full accessibility testing, public deployment, professional legal review or privacy/security audit.
- Kiroween requires meaningful real use of Kiro, a public GitHub repo with authentic `.kiro` project artifacts, an open-source license, a deployed app URL and a public demo video. Finish these before submission.
- License has intentionally NOT been selected; the entrant must select an appropriate OSI-approved license in Kiro/GitHub before publishing.

## Sources (reviewed November 22, 2026)
- https://www.usac.org/lifeline/consumer-eligibility/
- https://www.usac.org/lifeline/
- https://www.michigan.gov/mdhhs/assistance-programs/food/eligibility
- https://www.michigan.gov/mdhhs/assistance-programs/emergency-relief/eligibility
- https://kiroween.devpost.com/rules

## Privacy and safety
Educational screening only. No collected names, SSNs, addresses or uploaded documents; Streamlit hosting and other infrastructure may still log technical data. Do not input sensitive details into a public prototype. The official agencies are the only source of binding decisions.
