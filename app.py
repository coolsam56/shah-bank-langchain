import os

import streamlit as st
from dotenv import load_dotenv

from langchain_openrouter import ChatOpenRouter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage

from streamlit.errors import StreamlitSecretNotFoundError

from tools import calculate_emi
from knowledge_base import add_pdf_to_knowledge_base


# -----------------------------------
# Load environment variables
# -----------------------------------

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]
    except (KeyError, StreamlitSecretNotFoundError):
        api_key = None

if not api_key:
    st.error(
        "Missing OPENROUTER_API_KEY. Add it to your local .env file "
        "or configure it in the Streamlit app's Secrets settings."
    )
    st.stop()


# -----------------------------------
# Page configuration
# -----------------------------------

st.set_page_config(
    page_title="Sambank AI Banking Assistant",
    page_icon="🏦",
    layout="wide"
)


# -----------------------------------
# Load components
# -----------------------------------

@st.cache_resource
def load_components(api_key):

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.load_local(
        "vector_store",
        embeddings,
        allow_dangerous_deserialization=True
    )

    llm = ChatOpenRouter(
        model="openrouter/free",
        temperature=0,
        api_key=api_key
    )

    llm_with_tools = llm.bind_tools(
        [calculate_emi]
    )

    return vector_store, llm, llm_with_tools


vector_store, llm, llm_with_tools = load_components(api_key)


# -----------------------------------
# Final answer prompt
# -----------------------------------

answer_prompt = ChatPromptTemplate.from_template(
    """
You are NovaBank's AI Banking Assistant.

Answer the user's question using ONLY the banking context provided.

IMPORTANT RULES:

1. Never mix information from different banking products.

2. If the question is about a home loan, use only home-loan information.

3. If the question is about a personal loan, use only personal-loan information.

4. If the question is about debit cards, use only debit-card information.

5. Never invent rates, fees, eligibility criteria, documents, or policies.

6. If information is unavailable, say:
   "I don't have enough information in the available banking documents."

7. If the user asks for an EMI calculation, use the calculate_emi tool.

8. Do not manually calculate EMI when the calculator tool is available.

9. Keep the answer clear and concise.

10. Use the conversation history to understand follow-up questions such as:
    "what about its tenure?"
    "how can I block it?"
    "what happens after that?"

Conversation history:
{history}

Banking context:
{context}

User question:
{question}
"""
)


# -----------------------------------
# Conversation history
# -----------------------------------

def format_history(messages):

    if not messages:
        return "No previous conversation."

    history = []

    for message in messages:

        role = message["role"].upper()
        content = message["content"]

        history.append(
            f"{role}: {content}"
        )

    return "\n".join(history)


# -----------------------------------
# EMI question detection
# -----------------------------------

def is_emi_question(query):

    query_lower = query.lower()

    emi_keywords = [
        "calculate emi",
        "emi calculator",
        "calculate the emi",
        "monthly emi",
        "emi for",
        "emi of"
    ]

    return any(
        keyword in query_lower
        for keyword in emi_keywords
    )


# -----------------------------------
# Document selection
# -----------------------------------

def get_document_filter(query):

    query_lower = query.lower()

    if (
        "personal loan" in query_lower
        or "personal-loan" in query_lower
    ):
        return "documents/personal_loan.pdf"

    if (
        "home loan" in query_lower
        or "home-loan" in query_lower
        or "housing loan" in query_lower
        or "house loan" in query_lower
    ):
        return "documents/home_loan.pdf"

    if (
        "debit card" in query_lower
        or "debit-card" in query_lower
        or "atm card" in query_lower
        or "atm" in query_lower
    ):
        return "documents/debit_card_policy.pdf"

    if (
        "minimum balance" in query_lower
        or "miss an emi" in query_lower
        or "missed emi" in query_lower
        or "account balance" in query_lower
        or "unauthorized transaction" in query_lower
        or "unauthorised transaction" in query_lower
        or "internet banking" in query_lower
        or "password" in query_lower
    ):
        return "documents/banking_faq.pdf"

    return None


# -----------------------------------
# Retrieve documents
# -----------------------------------

def retrieve_documents(query):

    document_filter = get_document_filter(
        query
    )

    if document_filter:

        documents = vector_store.similarity_search(
            query,
            k=3,
            filter={
                "source": document_filter
            }
        )

    else:

        documents = vector_store.similarity_search(
            query,
            k=5
        )

    return documents


# -----------------------------------
# Run EMI tool
# -----------------------------------

def run_emi_tool(tool_call):

    return calculate_emi.invoke(
        tool_call["args"]
    )


# -----------------------------------
# Ask question
# -----------------------------------

def ask_question(question):

    history = format_history(
        st.session_state.messages
    )

    direct_emi_question = is_emi_question(
        question
    )

    # -----------------------------------
    # Build retrieval query
    # -----------------------------------
    # We no longer use an additional
    # OpenRouter call for query rewriting.
    # This saves API requests.
    # -----------------------------------

    if st.session_state.messages:

        recent_history = "\n".join(
            message["content"]
            for message in st.session_state.messages[-4:]
        )

        retrieval_query = (
            f"Previous conversation:\n"
            f"{recent_history}\n\n"
            f"Latest question:\n"
            f"{question}"
        )

    else:

        retrieval_query = question

    # -----------------------------------
    # Retrieve context
    # -----------------------------------

    if direct_emi_question:

        documents = []

        context = (
            "No banking document context is required "
            "for this calculation. Use the calculate_emi tool."
        )

    else:

        documents = retrieve_documents(
            retrieval_query
        )

        context = "\n\n".join(
            document.page_content
            for document in documents
        )

    # -----------------------------------
    # Create messages
    # -----------------------------------

    messages = answer_prompt.format_messages(
        history=history,
        context=context,
        question=question
    )

    # -----------------------------------
    # LLM call
    # -----------------------------------

    response = llm_with_tools.invoke(
        messages
    )

    # -----------------------------------
    # Tool calling
    # -----------------------------------

    if response.tool_calls:

        tool_messages = []

        for tool_call in response.tool_calls:

            if tool_call["name"] == "calculate_emi":

                tool_result = run_emi_tool(
                    tool_call
                )

                tool_messages.append(
                    ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call["id"]
                    )
                )

        final_messages = (
            messages
            + [response]
            + tool_messages
        )

        final_response = llm_with_tools.invoke(
            final_messages
        )

        return (
            final_response.content,
            documents,
            True
        )

    return (
        response.content,
        documents,
        False
    )


# -----------------------------------
# Sidebar
# -----------------------------------

with st.sidebar:

    st.header("📚 Knowledge Base")

    st.write(
        "Upload a banking PDF to add it to the "
        "assistant's knowledge base."
    )

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button(
            "➕ Add to Knowledge Base"
        ):

            with st.spinner(
                "Processing PDF..."
            ):

                try:

                    chunk_count = add_pdf_to_knowledge_base(
                        uploaded_file
                    )

                    st.cache_resource.clear()

                    st.success(
                        f"Added {uploaded_file.name} "
                        f"successfully. "
                        f"{chunk_count} chunks created."
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Error processing PDF: {error}"
                    )

    st.divider()

    st.header("ℹ️ Assistant")

    st.write(
        "NovaBank AI Banking Assistant"
    )

    st.write(
        "Powered by LangChain, FAISS and OpenRouter."
    )


# -----------------------------------
# Main UI
# -----------------------------------

st.title(
    "🏦 NovaBank AI Banking Assistant"
)

st.write(
    "Ask questions about NovaBank loans, debit cards, "
    "EMI, account services, and banking policies."
)


# -----------------------------------
# Conversation memory
# -----------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


# -----------------------------------
# Display previous messages
# -----------------------------------

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# -----------------------------------
# Chat input
# -----------------------------------

question = st.chat_input(
    "Ask a banking question..."
)


# -----------------------------------
# Process question
# -----------------------------------

if question:

    with st.chat_message("user"):

        st.markdown(
            question
        )

    with st.chat_message("assistant"):

        with st.spinner(
            "Finding the answer..."
        ):

            try:

                answer, documents, tool_used = ask_question(
                    question
                )

                st.markdown(
                    answer
                )

                # -----------------------------------
                # Sources
                # -----------------------------------

                st.markdown(
                    "### 📚 Sources"
                )

                if tool_used:

                    st.write(
                        "🧮 EMI Calculator Tool"
                    )

                elif documents:

                    shown_sources = set()

                    for document in documents:

                        source = document.metadata.get(
                            "source"
                        )

                        page = document.metadata.get(
                            "page",
                            0
                        ) + 1

                        source_name = (
                            f"{source} — Page {page}"
                        )

                        if source_name not in shown_sources:

                            st.write(
                                f"- {source_name}"
                            )

                            shown_sources.add(
                                source_name
                            )

                else:

                    st.write(
                        "No source documents were required."
                    )

            except Exception as error:

                answer = (
                    "Sorry, I am temporarily unable to process "
                    "your request. Please try again later."
                )

                st.error(
                    f"Assistant error: {error}"
                )

    # -----------------------------------
    # Save conversation
    # -----------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


# -----------------------------------
# Clear conversation
# -----------------------------------

if st.session_state.messages:

    if st.button(
        "🗑️ Clear Conversation"
    ):

        st.session_state.messages = []

        st.rerun()