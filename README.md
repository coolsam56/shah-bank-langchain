# Smart Banking Support Agent Using Agentic AI

## 1. Project Overview

The Smart Banking Support Agent is a Python-based Agentic AI application that assists users with common banking queries and personal loan workflows.

It uses LangChain to coordinate an AI agent with four Python tools. The agent selects tools based on the user's request, uses their results, asks for missing information, and requires explicit customer confirmation before submitting a loan application.

**This is a training project. All banking data is fictional, and applications are stored in a local SQLite database. No real bank services or lending decisions are involved.**

## 2. Objectives

- Build an AI agent using LangChain.
- Calculate personal loan EMIs.
- Check loan eligibility using simulated rules.
- Retrieve customer account information from SQLite.
- Submit loan applications through a FastAPI REST API.
- Require explicit customer confirmation before submission.
- Validate inputs and recheck eligibility on the API side.
- Test the banking tools using pytest.

## 3. Technology Stack

- **Language:** Python 3.11
- **Agent framework:** LangChain
- **Language model API:** OpenRouter
- **Backend API:** FastAPI
- **Database:** SQLite
- **Configuration:** python-dotenv
- **Validation:** Pydantic
- **Testing:** pytest
- **Development environment:** Visual Studio Code

## 4. Main Features

### EMI Calculator
Calculates the monthly EMI, total interest, and total repayment using the loan amount, tenure, and annual interest rate.

### Loan Eligibility Checker
Checks whether existing EMI plus proposed EMI is at most 40% of the customer's monthly salary. This is a simulated training rule, not a real bank policy.

### Account Information Retrieval
Retrieves fictional customer information, including account type, masked account number, balance, salary, and existing EMI.

### Loan Application Submission
Submits an application through FastAPI only after explicit confirmation and a successful eligibility check. The API recalculates EMI and independently checks eligibility before saving the application.

### Conversational AI Agent
Coordinates the four tools and consolidates their results into a natural-language response.

## 5. Project Structure

```text
SmartBankingAgent/
├── app.py
├── agent.py
├── api.py
├── config.py
├── database.py
├── requirements.txt
├── README.md
├── .env
├── .env.example
├── .gitignore
├── tools/
│   ├── __init__.py
│   └── banking_tools.py
├── tests/
│   └── test_banking_tools.py
└── data/
    └── banking.db
```

The virtual environment (`venv/`) and local database files should not be committed to Git.

## 6. Prerequisites

- Python 3.11
- Git (optional)
- An OpenRouter account and API key
- Visual Studio Code or another Python IDE

## 7. Installation and Setup

### Step 1: Create and activate a virtual environment

On Windows PowerShell, run these commands from the project directory:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 2: Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure environment variables

Create or update the `.env` file in the project root:

```env
OPENAI_API_KEY=your_openrouter_api_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=openrouter/free
BANK_NAME=DemoBank
PERSONAL_LOAN_ANNUAL_RATE=10.5
```

Replace the placeholder API key with your own key. Never commit `.env` or publish your API key.

The project uses the OpenAI-compatible API interface provided by OpenRouter. A free model may be unavailable or rate-limited at times.

### Step 4: Initialize the database

```powershell
python database.py
```

This creates the SQLite database and inserts the fictional demo customer if the customer does not already exist.

**Demo customer ID:** `CUST1001`

### Step 5: Start the FastAPI service

In the first terminal:

```powershell
uvicorn api:app --reload
```

Useful API URLs:

- Health check: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs

Keep this terminal running while testing application submission.

### Step 6: Start the AI agent

Open a second terminal, activate the same virtual environment, and run:

```powershell
python app.py
```

Enter a banking query in the terminal. Type `exit` to stop the agent.

## 8. Example Workflow

Example request:

> My demo customer ID is CUST1001. I want a personal loan of ₹5,00,000 for 36 months. Calculate the EMI, check eligibility, and retrieve my account details. Do not submit an application yet.

The agent should calculate the EMI, retrieve the customer's fictional account details, and check eligibility. It should then present the results and wait for explicit confirmation.

Only after confirmation should it attempt to submit the application.

## 9. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check API health |
| POST | `/applications` | Validate and record a demo loan application |

The application endpoint validates input, checks the customer's existence, recalculates EMI, independently verifies the simulated eligibility rule, and records eligible confirmed applications in SQLite.

## 10. Testing

Run the automated tests from the project root:

```powershell
python -m pytest tests/test_banking_tools.py -v
```

The tests cover:

1. EMI calculation.
2. Loan eligibility.
3. Account information retrieval.
4. The explicit confirmation requirement.
5. Rejection of ineligible customers.

## 11. Sample Demonstration Result

For a fictional loan of ₹5,00,000 over 36 months at 10.5% annual interest:

- Monthly EMI: approximately ₹16,251.22
- Total interest: approximately ₹85,043.98
- Total repayment: approximately ₹5,85,043.98
- Monthly salary: ₹60,000
- Existing EMI: ₹5,000
- Total EMI-to-income ratio: approximately 35.42%
- Simulated eligibility: Eligible

These figures are illustrative. Eligibility is based solely on the project's mock rule.

## 12. Security and Limitations

- All customer information is fictional.
- No real banking system is connected.
- The application reference is generated by the local training database.
- The confirmation mechanism is designed for this local demonstration; it is not a production-grade identity or transaction authorization system.
- The project does not implement real authentication, authorization, or banking-grade fraud controls.
- The `.env` file must remain private.
- Free language-model endpoints may have rate limits or availability issues.

## 13. Future Enhancements

- Add a web-based chat interface.
- Implement stronger session-bound confirmation and duplicate-submission protection.
- Add authentication and authorization.
- Expand the test suite to cover the FastAPI endpoints.
- Deploy the agent and API to a hosting platform with appropriate secret management.

## 14. Conclusion

The project demonstrates an Agentic AI workflow in which a LangChain agent coordinates Python tools, retrieves mock banking data, performs calculations, applies business rules, and interacts with a REST API to record a confirmed loan application. It combines LLM-based reasoning with deterministic Python logic and database operations.