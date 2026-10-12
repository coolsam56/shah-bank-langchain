from tools.banking_tools import (
    calculate_emi,
    check_loan_eligibility,
    retrieve_account_details,
    submit_loan_application,
)


def test_emi_calculation():
    result = calculate_emi.invoke({
        "loan_amount": 500000,
        "tenure_months": 36,
        "annual_interest_rate": 10.5,
    })

    assert "error" not in result
    assert result["monthly_emi"] > 0
    assert result["total_repayment"] > 500000
    assert result["total_interest"] > 0


def test_loan_eligibility():
    emi = calculate_emi.invoke({
        "loan_amount": 500000,
        "tenure_months": 36,
        "annual_interest_rate": 10.5,
    })["monthly_emi"]

    result = check_loan_eligibility.invoke({
        "customer_id": "CUST1001",
        "proposed_emi": emi,
    })

    assert result["eligible"] is True
    assert result["monthly_salary"] == 60000
    assert result["existing_emi"] == 5000


def test_account_retrieval():
    result = retrieve_account_details.invoke({
        "customer_id": "CUST1001",
    })

    assert result["found"] is True
    assert result["account_number"] == "XXXXXX1234"
    assert result["balance"] == 125000.00


def test_submission_requires_confirmation():
    result = submit_loan_application.invoke({
        "customer_id": "CUST1001",
        "loan_amount": 500000,
        "tenure_months": 36,
        "monthly_emi": 16300,
        "eligible": True,
        "customer_confirmed": False,
    })

    assert result["submitted"] is False
    assert result["status"] == "CONFIRMATION_REQUIRED"


def test_ineligible_customer_cannot_submit():
    result = submit_loan_application.invoke({
        "customer_id": "CUST1001",
        "loan_amount": 500000,
        "tenure_months": 36,
        "monthly_emi": 16300,
        "eligible": False,
        "customer_confirmed": True,
    })

    assert result["submitted"] is False
    assert result["status"] == "NOT_SUBMITTED"
