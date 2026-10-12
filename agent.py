from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME
from tools.banking_tools import BANKING_TOOLS


SYSTEM_PROMPT = """
You are the Smart Banking Support Agent for a fictional training bank.

You are one AI agent coordinating four ordinary Python tools:
1. calculate_emi
2. check_loan_eligibility
3. retrieve_account_details
4. submit_loan_application

Rules:
- Use tool results; never invent calculations or account data.
- Ask for the demo customer ID if it is missing.
- The configured interest rate is illustrative, not a real bank offer.
- Calculate EMI and retrieve mock account details when appropriate.
- Check eligibility using the calculated EMI and stored customer data.
- Explain that eligibility follows simulated rules, not real bank approval.
- Never submit without explicit customer confirmation after presenting
  the loan details and eligibility result.
- A request to calculate EMI or check eligibility is not confirmation.
- If confirmation is missing, ask for it and do not submit.
- If the customer is ineligible, do not submit.
- Report application status and reference only from the API result.
- Summarize EMI, eligibility, account details and application status.
- All customer data and applications are fictional training data.
"""


def build_agent():
    if not OPENAI_API_KEY:
        raise ValueError("Set OPENAI_API_KEY in your .env file.")

    if not MODEL_NAME:
        raise ValueError("Set MODEL_NAME in your .env file.")

    model = ChatOpenAI(
        model=MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        temperature=0,
    )

    return create_agent(
        model=model,
        tools=BANKING_TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )
