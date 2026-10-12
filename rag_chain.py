from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


VECTOR_STORE_FOLDER = "vector_store"


# Load embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Load FAISS vector store
vector_store = FAISS.load_local(
    VECTOR_STORE_FOLDER,
    embeddings,
    allow_dangerous_deserialization=True
)


# Create retriever
retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)


# Create LLM
llm = ChatOpenRouter(
    model="openrouter/free",
    temperature=0
)


# Prompt
prompt = ChatPromptTemplate.from_template(
    """
You are NovaBank's AI Banking Assistant.

Answer the user's question using ONLY the information provided
in the context below.

If the answer is not available in the context, say:
"I don't have enough information in the available banking documents."

Do not invent banking policies, rates, fees, eligibility criteria,
or procedures.

Context:
{context}

User Question:
{question}

Answer:
"""
)


def format_documents(documents):
    return "\n\n".join(
        document.page_content
        for document in documents
    )


def ask_question(question):

    documents = retriever.invoke(question)

    context = format_documents(documents)

    messages = prompt.format_messages(
        context=context,
        question=question
    )

    response = llm.invoke(messages)

    return response.content, documents


if __name__ == "__main__":

    question = "What documents are required for a home loan?"

    answer, documents = ask_question(question)

    print("\nANSWER:")
    print(answer)

    print("\nSOURCES:")

    for document in documents:
        print(
            f"- {document.metadata.get('source')} "
            f"(Page {document.metadata.get('page', 0) + 1})"
        )