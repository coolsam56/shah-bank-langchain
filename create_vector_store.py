from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


DOCUMENTS_FOLDER = Path("documents")
VECTOR_STORE_FOLDER = Path("vector_store")


# 1. Load all PDFs
pdf_files = list(DOCUMENTS_FOLDER.glob("*.pdf"))

all_documents = []

for pdf_file in pdf_files:
    loader = PyPDFLoader(str(pdf_file))
    documents = loader.load()
    all_documents.extend(documents)

print(f"Loaded {len(all_documents)} pages.")


# 2. Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = text_splitter.split_documents(all_documents)

print(f"Created {len(chunks)} chunks.")


# 3. Create local embeddings
print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# 4. Create FAISS vector store
print("Creating FAISS vector store...")

vector_store = FAISS.from_documents(
    chunks,
    embeddings
)

# 5. Save vector store
vector_store.save_local(str(VECTOR_STORE_FOLDER))

print("\nFAISS vector store created successfully!")
print(f"Saved to: {VECTOR_STORE_FOLDER}")