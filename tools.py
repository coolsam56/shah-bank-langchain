from langchain_core.tools import tool


@tool
def calculate_emi(
    loan_amount: float,
    annual_interest_rate: float,
    tenure_years: int
) -> str:
    """
    Calculate monthly EMI, total interest, and total repayment
    for a loan.
    """

    monthly_rate = annual_interest_rate / 12 / 100
    number_of_payments = tenure_years * 12

    if monthly_rate == 0:
        emi = loan_amount / number_of_payments
    else:
        emi = (
            loan_amount
            * monthly_rate
            * (1 + monthly_rate) ** number_of_payments
        ) / (
            (1 + monthly_rate) ** number_of_payments - 1
        )

    total_payment = emi * number_of_payments
    total_interest = total_payment - loan_amount

    return (
        f"Monthly EMI: ₹{emi:,.2f}\n"
        f"Total Interest: ₹{total_interest:,.2f}\n"
        f"Total Repayment: ₹{total_payment:,.2f}"
    )