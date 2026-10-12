from pathlib import Path
import tempfile

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


VECTOR_STORE_FOLDER = "vector_store"


def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def add_pdf_to_knowledge_base(uploaded_file):

    embeddings = get_embeddings()

    # Save uploaded PDF temporarily
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:

        temp_file.write(
            uploaded_file.getbuffer()
        )

        temp_pdf_path = temp_file.name


    try:

        # Load PDF
        loader = PyPDFLoader(
            temp_pdf_path
        )

        documents = loader.load()


        # Add uploaded filename to metadata
        for document in documents:

            document.metadata["source"] = (
                uploaded_file.name
            )


        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = text_splitter.split_documents(
            documents
        )


        # Create embeddings
        new_vector_store = FAISS.from_documents(
            chunks,
            embeddings
        )


        # If existing vector store exists,
        # merge the new documents
        vector_store_path = Path(
            VECTOR_STORE_FOLDER
        )

        if vector_store_path.exists():

            existing_vector_store = FAISS.load_local(
                VECTOR_STORE_FOLDER,
                embeddings,
                allow_dangerous_deserialization=True
            )

            existing_vector_store.merge_from(
                new_vector_store
            )

            existing_vector_store.save_local(
                VECTOR_STORE_FOLDER
            )

        else:

            new_vector_store.save_local(
                VECTOR_STORE_FOLDER
            )


        return len(chunks)


    finally:

        # Delete temporary PDF
        Path(temp_pdf_path).unlink(
            missing_ok=True
        )