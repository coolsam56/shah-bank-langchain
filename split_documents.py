from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


documents_folder = Path("documents")

pdf_files = list(documents_folder.glob("*.pdf"))


# Load all PDF pages
all_documents = []

for pdf_file in pdf_files:

    loader = PyPDFLoader(str(pdf_file))

    documents = loader.load()

    all_documents.extend(documents)


print("Total pages loaded:", len(all_documents))


# Create the text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)


# Split documents into chunks
chunks = text_splitter.split_documents(all_documents)


print("Total chunks created:", len(chunks))


print("\n-----------------------------------")
print("FIRST CHUNK")
print("-----------------------------------")

print(chunks[0].page_content)


print("\n-----------------------------------")
print("FIRST CHUNK METADATA")
print("-----------------------------------")

print(chunks[0].metadata)