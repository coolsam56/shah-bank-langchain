from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


documents_folder = Path("documents")

pdf_files = list(documents_folder.glob("*.pdf"))

print(f"Found {len(pdf_files)} PDF files.\n")


all_documents = []


for pdf_file in pdf_files:

    print(f"Loading: {pdf_file.name}")

    loader = PyPDFLoader(str(pdf_file))

    documents = loader.load()

    print(f"Pages loaded: {len(documents)}")

    all_documents.extend(documents)


print("\n-----------------------------------")
print("Total pages loaded:", len(all_documents))
print("-----------------------------------")


print("\nFirst document content:\n")
print(all_documents[0].page_content)


print("\nMetadata:\n")
print(all_documents[0].metadata)