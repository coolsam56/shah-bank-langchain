from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter

from tools import calculate_emi


load_dotenv()


llm = ChatOpenRouter(
    model="openrouter/free",
    temperature=0
)


llm_with_tools = llm.bind_tools(
    [calculate_emi]
)


response = llm_with_tools.invoke(
    "Calculate the EMI for a loan of ₹5,00,000 "
    "at 10.5% annual interest for 5 years."
)


print("\nAI RESPONSE:")
print(response.content)

print("\nTOOL CALLS:")
print(response.tool_calls)