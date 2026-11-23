# BenefitChain AI — Product Steering

## Project Mission
BenefitChain AI helps Michigan residents discover potential connections between public assistance programs through transparent preliminary screening and interactive visualizations. It is not an official eligibility determination system.

## Accuracy and Trust
- Use official government sources for benefit rules.
- Never invent eligibility criteria, payment amounts, or enrollment guarantees.
- Distinguish potential pathways from official eligibility decisions.
- Preserve official source links and policy review dates.
- Never imply automatic enrollment in another program.

## Privacy
- Do not request names, Social Security numbers, addresses, or case numbers.
- Process household information during the Streamlit session.
- Do not introduce permanent household storage without explicit review.
- Keep privacy notices visible and accurate.

## Screening Rules
- Keep screening logic in engine.py and independent of Streamlit.
- Maintain transparent, rule-based calculations.
- Treat SNAP and State Emergency Relief as preliminary referrals.
- Clearly identify What-If scenarios as hypothetical.

## Design
- Use plain English.
- Keep the interface accessible and mobile-friendly.
- Explain benefit connections and required verification steps.
- Do not rely on color alone to explain results.

## Testing
- Preserve existing automated tests.
- Add tests for new features and edge cases.
- Test changes locally before publishing.
- Avoid unnecessary dependencies.

## Kiro Development Process
1. Define requirements and acceptance criteria.
2. Update the technical design.
3. Create implementation tasks.
4. Implement changes.
5. Run automated tests.
6. Review privacy, accuracy, and accessibility.
7. Test before deployment.

## Guiding Principle
Make public assistance easier to understand without creating false confidence about eligibility or enrollment.
