from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


VECTOR_STORE_FOLDER = "vector_store"


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = FAISS.load_local(
    VECTOR_STORE_FOLDER,
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)


question = "What documents are required for a home loan?"

documents = retriever.invoke(question)

print("\nRETRIEVED DOCUMENTS:\n")

for i, document in enumerate(documents, start=1):

    print(f"--- Document {i} ---")
    print(document.page_content)
    print("Source:", document.metadata.get("source"))
    print("Page:", document.metadata.get("page"))
    print()