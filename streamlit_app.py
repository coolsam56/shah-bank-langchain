import streamlit as st
from langchain.messages import HumanMessage, AIMessage
from agent import build_agent

st.set_page_config(
    page_title="Smart Banking Support Agent",
    page_icon="🏦",
    layout="centered",
)

st.title("🏦 Smart Banking Support Agent")
st.caption("Agentic AI demo | LangChain · FastAPI · SQLite")
st.info(
    "Training simulation only. All customer information is fictional. "
    "This is not a real banking service or lending decision."
)

if "agent" not in st.session_state:
    st.session_state.agent = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_error" not in st.session_state:
    st.session_state.agent_error = None

with st.sidebar:
    st.header("Demo information")
    st.write("**Demo customer ID:** `CUST1001`")
    st.write("**Illustrative annual interest rate:** 10.5%")
    st.write("**Eligibility rule:** Total EMI must not exceed 40% of salary.")
    st.divider()
    st.write("**Available features**")
    st.write("- EMI calculation")
    st.write("- Loan eligibility check")
    st.write("- Mock account information")
    st.write("- Confirmed demo loan submission")
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.agent = None
        st.session_state.agent_error = None
        st.rerun()

if st.session_state.agent is None and st.session_state.agent_error is None:
    try:
        with st.spinner("Connecting to the AI agent..."):
            st.session_state.agent = build_agent()
    except Exception as exc:
        st.session_state.agent_error = str(exc)

if st.session_state.agent_error:
    st.error(
        "The AI agent could not start. Check the server configuration "
        "and the deployment secrets."
    )
    with st.expander("Technical details"):
        st.code(st.session_state.agent_error)
    st.stop()

for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            content = message.content
            if isinstance(content, str):
                st.markdown(content)
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("text"):
                        st.markdown(part["text"])
                    else:
                        st.write(part)
            else:
                st.write(content)

user_input = st.chat_input("Ask about EMI, eligibility, or your demo account...")

if user_input:
    user_message = HumanMessage(content=user_input)
    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            with st.spinner("The banking agent is working..."):
                result = st.session_state.agent.invoke(
                    {"messages": st.session_state.messages}
                )
                st.session_state.messages = result["messages"]
                last_message = st.session_state.messages[-1]
                content = last_message.content

            if isinstance(content, str):
                st.markdown(content)
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("text"):
                        st.markdown(part["text"])
                    else:
                        st.write(part)
            else:
                st.write(content)

        except Exception:
            st.error(
                "The request failed. Check API availability and model "
                "configuration, then try again."
            )
            st.session_state.messages.pop()
