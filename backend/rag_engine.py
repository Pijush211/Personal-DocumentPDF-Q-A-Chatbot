import os
import tempfile
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def load_and_split_document(file_bytes: bytes, file_name: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Parses PDF or TXT file bytes and splits text into chunks.
    """
    ext = os.path.splitext(file_name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        if ext == ".pdf":
            loader = PyPDFLoader(temp_path)
            documents = loader.load()
        elif ext in [".txt", ".md"]:
            loader = TextLoader(temp_path, encoding="utf-8")
            documents = loader.load()
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        for doc in documents:
            doc.metadata["source"] = file_name

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        return text_splitter.split_documents(documents)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def create_vector_store(chunks: List[Any], embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> FAISS:
    """
    Generates dense embeddings and builds local FAISS index.
    """
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
    return FAISS.from_documents(documents=chunks, embedding=embeddings)


def query_rag_system(vector_store: FAISS, question: str, groq_api_key: str, model_name: str = "llama-3.3-70b-versatile") -> Dict[str, Any]:
    """
    Retrieves context and queries Groq LLM using standard LangChain Expression Language (LCEL).
    """
    # 1. Retrieve top-4 relevant chunks
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    retrieved_docs = retriever.invoke(question)
    
    # 2. Format context text
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    
    # 3. Setup Groq LLM
    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name=model_name,
        temperature=0.2
    )

    # 4. Prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an intelligent document assistant. Use the following retrieved context "
            "from the user's document to answer the question concisely and accurately.\n"
            "If the document does not contain enough information, state clearly that it is not mentioned.\n\n"
            "Context:\n{context}"
        )),
        ("human", "{question}")
    ])

    # 5. Build LCEL Chain
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context_text, "question": question})

    # 6. Format sources
    sources = []
    for doc in retrieved_docs:
        sources.append({
            "content": doc.page_content,
            "page": doc.metadata.get("page", 1),
            "source": doc.metadata.get("source", "Document")
        })

    return {
        "answer": answer,
        "sources": sources
    }