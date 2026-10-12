import httpx
from langchain.tools import tool
from config import PERSONAL_LOAN_ANNUAL_RATE, API_BASE_URL
from database import get_connection


@tool
def calculate_emi(
    loan_amount: float,
    tenure_months: int,
    annual_interest_rate: float = PERSONAL_LOAN_ANNUAL_RATE,
) -> dict:
    """Calculate monthly EMI, total repayment and total interest."""
    if loan_amount <= 0 or tenure_months <= 0:
        return {"error": "Loan amount and tenure must be positive."}
    if annual_interest_rate < 0:
        return {"error": "Interest rate cannot be negative."}

    monthly_rate = annual_interest_rate / 1200

    if monthly_rate == 0:
        emi = loan_amount / tenure_months
    else:
        factor = (1 + monthly_rate) ** tenure_months
        emi = loan_amount * monthly_rate * factor / (factor - 1)

    total_repayment = emi * tenure_months

    return {
        "loan_amount": loan_amount,
        "tenure_months": tenure_months,
        "annual_interest_rate_percent": annual_interest_rate,
        "monthly_emi": round(emi, 2),
        "total_interest": round(total_repayment - loan_amount, 2),
        "total_repayment": round(total_repayment, 2),
    }


@tool
def check_loan_eligibility(customer_id: str, proposed_emi: float) -> dict:
    """Check demo eligibility using salary and existing EMI.
    The training rule requires total EMI to be at most 40% of salary.
    """
    if proposed_emi <= 0:
        return {"error": "Proposed EMI must be positive."}

    with get_connection() as conn:
        customer = conn.execute(
            """SELECT monthly_salary, existing_emi
               FROM customers WHERE customer_id = ?""",
            (customer_id,),
        ).fetchone()

    if customer is None:
        return {"eligible": False, "reason": "Demo customer not found."}

    salary = float(customer["monthly_salary"])
    existing_emi = float(customer["existing_emi"])
    total_emi = existing_emi + proposed_emi
    ratio = total_emi / salary if salary > 0 else float("inf")
    eligible = salary > 0 and ratio <= 0.40

    return {
        "customer_id": customer_id,
        "eligible": eligible,
        "monthly_salary": salary,
        "existing_emi": existing_emi,
        "proposed_emi": round(proposed_emi, 2),
        "total_monthly_emi": round(total_emi, 2),
        "emi_to_income_ratio_percent": round(ratio * 100, 2),
        "reason": (
            "Passes the simulated eligibility rule."
            if eligible
            else "Does not pass the simulated eligibility rule."
        ),
        "note": "Training simulation only; not a real lending decision.",
    }


@tool
def retrieve_account_details(customer_id: str) -> dict:
    """Retrieve fictional account details for a demo customer ID."""
    with get_connection() as conn:
        customer = conn.execute(
            """SELECT customer_id, full_name, account_number, account_type,
                      balance, monthly_salary, existing_emi
               FROM customers WHERE customer_id = ?""",
            (customer_id,),
        ).fetchone()

    if customer is None:
        return {"found": False, "message": "Demo customer not found."}

    return {
        "found": True,
        "customer_id": customer["customer_id"],
        "full_name": customer["full_name"],
        "account_number": customer["account_number"],
        "account_type": customer["account_type"],
        "balance": float(customer["balance"]),
        "monthly_salary": float(customer["monthly_salary"]),
        "existing_emi": float(customer["existing_emi"]),
        "note": "Fictional training data.",
    }


@tool
def submit_loan_application(
    customer_id: str,
    loan_amount: float,
    tenure_months: int,
    monthly_emi: float,
    eligible: bool,
    customer_confirmed: bool,
) -> dict:
    """Submit through the mock API only after explicit customer confirmation
    and a positive eligibility result. Never assume customer confirmation.
    """
    if not customer_confirmed:
        return {
            "submitted": False,
            "status": "CONFIRMATION_REQUIRED",
            "message": "Ask the customer to explicitly confirm submission.",
        }

    if not eligible:
        return {
            "submitted": False,
            "status": "NOT_SUBMITTED",
            "message": "The customer is not eligible under demo rules.",
        }

    try:
        response = httpx.post(
            f"{API_BASE_URL}/applications",
            json={
                "customer_id": customer_id,
                "loan_amount": loan_amount,
                "tenure_months": tenure_months,
                "customer_confirmed": True,
            },
            timeout=10.0,
        )

        if response.status_code == 201:
            return response.json()

        return {
            "submitted": False,
            "status": "REJECTED",
            "details": response.json(),
        }

    except httpx.RequestError:
        return {
            "submitted": False,
            "status": "API_UNAVAILABLE",
            "message": "The FastAPI service is unavailable.",
        }


BANKING_TOOLS = [
    calculate_emi,
    check_loan_eligibility,
    retrieve_account_details,
    submit_loan_application,
]
