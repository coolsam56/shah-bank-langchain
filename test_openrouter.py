from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter


# Load variables from .env
load_dotenv()


# Create the OpenRouter LLM
llm = ChatOpenRouter(
    model="openrouter/free",
    temperature=0
)


# Send a test question
response = llm.invoke(
    "What is EMI? Explain it in simple words."
)


# Print the answer
print("\nAI RESPONSE:")
print(response.content)