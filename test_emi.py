from tools import calculate_emi


result = calculate_emi.invoke({
    "loan_amount": 500000,
    "annual_interest_rate": 10.5,
    "tenure_years": 5
})


print(result)