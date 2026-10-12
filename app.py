from langchain.messages import HumanMessage

from agent import build_agent


def main():
    print("=" * 60)
    print("       SMART BANKING SUPPORT AGENT")
    print("       Agentic AI Training Project")
    print("=" * 60)
    print("Demo customer ID: CUST1001")
    print("Type 'exit' to quit.")
    print("Use fictional training data only.\n")

    agent = build_agent()
    conversation = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not user_input:
            continue

        conversation.append(HumanMessage(content=user_input))

        try:
            result = agent.invoke({"messages": conversation})
            conversation = result["messages"]

            last_message = conversation[-1]
            content = getattr(last_message, "content", str(last_message))

            if isinstance(content, list):
                content = "\n".join(
                    str(part.get("text", part))
                    if isinstance(part, dict)
                    else str(part)
                    for part in content
                )

            print(f"\nBanking Agent: {content}\n")

        except Exception as exc:
            print(f"\nAgent error: {exc}")
            print("Check your API key, model name and API server.\n")


if __name__ == "__main__":
    main()
