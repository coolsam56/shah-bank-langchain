from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import BANK_NAME, PERSONAL_LOAN_ANNUAL_RATE
from database import get_connection, init_db
from tools.banking_tools import calculate_emi

app = FastAPI(
    title="Smart Banking Support API",
    description="Mock REST API for the Smart Banking Agent project",
    version="1.0.0",
)


class LoanApplicationRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    loan_amount: float = Field(gt=0, le=10_000_000)
    tenure_months: int = Field(gt=0, le=360)
    customer_confirmed: bool


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Smart Banking Support API",
        "bank": BANK_NAME,
    }


@app.post("/applications", status_code=201)
def create_application(request: LoanApplicationRequest):
    if request.customer_confirmed is not True:
        raise HTTPException(
            status_code=400,
            detail="Explicit customer confirmation is required.",
        )

    with get_connection() as conn:
        customer = conn.execute(
            """SELECT customer_id, monthly_salary, existing_emi
               FROM customers WHERE customer_id = ?""",
            (request.customer_id,),
        ).fetchone()

        if customer is None:
            raise HTTPException(
                status_code=404,
                detail="Demo customer not found.",
            )

        emi_result = calculate_emi.invoke({
            "loan_amount": request.loan_amount,
            "tenure_months": request.tenure_months,
            "annual_interest_rate": PERSONAL_LOAN_ANNUAL_RATE,
        })

        if "error" in emi_result:
            raise HTTPException(status_code=400, detail=emi_result["error"])

        monthly_emi = emi_result["monthly_emi"]
        salary = float(customer["monthly_salary"])
        existing_emi = float(customer["existing_emi"])
        total_emi = existing_emi + monthly_emi

        eligible = salary > 0 and total_emi / salary <= 0.40

        if not eligible:
            raise HTTPException(
                status_code=403,
                detail="Customer does not meet the demo eligibility rule.",
            )

        cursor = conn.execute(
            """INSERT INTO loan_applications
               (customer_id, loan_amount, tenure_months,
                annual_interest_rate, monthly_emi, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                request.customer_id,
                request.loan_amount,
                request.tenure_months,
                PERSONAL_LOAN_ANNUAL_RATE,
                monthly_emi,
                "SUBMITTED",
            ),
        )

        application_id = cursor.lastrowid

    return {
        "submitted": True,
        "status": "SUBMITTED",
        "application_id": f"DEMO-LOAN-{application_id:06d}",
        "customer_id": request.customer_id,
        "loan_amount": request.loan_amount,
        "tenure_months": request.tenure_months,
        "monthly_emi": monthly_emi,
        "annual_interest_rate_percent": PERSONAL_LOAN_ANNUAL_RATE,
        "message": "Demo application recorded successfully.",
        "note": "Training simulation only; not a real bank application.",
    }
