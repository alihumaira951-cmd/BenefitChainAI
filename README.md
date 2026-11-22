# 🔗 BenefitChain AI
### Discover Hidden Connections Between Michigan Public Assistance Programs

**Built with Kiro | Kiroween 2026 Hackathon | Python + Streamlit**

**🌐 [Try BenefitChain AI Live](https://benefitchain-ai-michigan.streamlit.app/)**

## The Problem

Millions of households navigate separate government assistance programs without knowing how those programs connect.

For example, someone receiving SNAP food assistance may not realize that their participation provides a recognized qualification pathway for Lifeline, a federal program offering discounted phone or internet service.

This lack of awareness can prevent households from exploring assistance that may be available to them.

## Our Solution

**BenefitChain AI** is a Michigan-focused public assistance discovery application that helps residents identify potential benefit pathways, understand how programs are connected, and learn what steps to take next.

Rather than simply listing assistance programs, BenefitChain AI demonstrates the **Benefit Domino Effect**: how participating in one benefit program can create a pathway to another.

The application uses transparent, rule-based screening with official government sources. It does not make official eligibility decisions.

## Key Features

### 1. Household Screening
Users enter basic household information, including household size, approximate income, current assistance program participation, and energy emergency status.

No names, Social Security numbers, case numbers, or addresses are requested.

### 2. Lifeline Qualification Pathways
Screens potential Lifeline pathways using published 2026 income guidelines and participation in qualifying assistance programs.

Displays an illustrative standard discount of up to **$9.25 per month ($111 annually)**, subject to program and provider rules.

### 3. Benefit Domino Effect
An interactive graph built with NetworkX and Plotly illustrates relationships such as:

- SNAP → Lifeline
- Medicaid → Lifeline

The graph distinguishes existing participation from potential pathways. Connections do not mean automatic enrollment.

### 4. Michigan Assistance Referrals
Provides official next steps for:

- Michigan SNAP Food Assistance
- Michigan State Emergency Relief (SER)

Emergency utility situations are highlighted separately from Lifeline screening pathways.

### 5. Explainable Results
Every program result includes a plain-English explanation, status, suggested next steps, official program link, and policy review date.

### 6. Accessible Demonstration
Includes a fictional sample household so visitors can explore the application without entering their own information.

The interface uses a mobile-friendly layout and text-based status explanations.

## Technology Stack

- **Python** — screening logic
- **Streamlit** — interactive web application
- **NetworkX** — benefit relationship graph
- **Plotly** — interactive visualization
- **pytest** — automated testing
- **Kiro IDE** — specification-driven AI-assisted development
- **GitHub** — source code hosting
- **Streamlit Community Cloud** — public deployment

## How Kiro Was Used

Kiro played a central role in developing BenefitChain AI.

Development followed a structured, specification-driven process:

1. Generated and refined project requirements.
2. Developed a technical architecture and data models.
3. Created an ordered implementation task plan.
4. Implemented the screening engine, interactive benefit graph, and Streamlit interface.
5. Generated automated tests for eligibility thresholds, benefit pathways, referrals, and validation.
6. Helped identify and correct dashboard formatting, graph visualization, and status-label issues.
7. Refined household-specific explanations and separated emergency referrals from qualification pathways.

Kiro's project specifications are maintained in the local `.kiro/specs/benefitchain/` development directory and will be added to this repository.

## Testing

Kiro reported **22 passing automated tests** during development, including tests for:

- Income-threshold calculations
- Program-based Lifeline pathways
- Invalid household inputs
- Households already receiving Lifeline
- Emergency assistance referrals
- Screening result structure
- Government URL formatting

The application was also manually tested locally and after public deployment using fictional household scenarios.

## Run Locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

To run the automated tests after obtaining the test suite:

```bash
python -m pytest tests/ -v
```

## Official Sources

- [USAC Lifeline Eligibility](https://www.usac.org/lifeline/consumer-eligibility/)
- [Michigan SNAP Eligibility](https://www.michigan.gov/mdhhs/assistance-programs/food/eligibility)
- [Michigan State Emergency Relief](https://www.michigan.gov/mdhhs/assistance-programs/emergency-relief/eligibility)
- [MI Bridges Application Portal](https://newmibridges.michigan.gov/)

**Policy review date:** November 22, 2026.

## Privacy and Important Limitations

BenefitChain AI is an educational screening prototype, not a government eligibility system.

- Results are preliminary and do not guarantee assistance.
- Official program agencies make all eligibility and enrollment decisions.
- Household information is processed by the Streamlit application server during a session.
- The application is designed not to persist household profiles in a database.
- Hosting infrastructure may process or log technical information.
- Users should not provide identifying or sensitive information.

The MVP does not include real-time funding checks, live agency integrations, comprehensive eligibility determinations, or a completed independent security and accessibility audit.

## Future Vision

BenefitChain AI could eventually expand to additional assistance programs, more states, multilingual guidance, and more sophisticated benefit discovery.

Our goal is to make public assistance easier to understand and navigate, one connection at a time.

---

**Developed for the Kiroween 2026 Hackathon.**

**[Launch BenefitChain AI](https://benefitchain-ai-michigan.streamlit.app/)**
