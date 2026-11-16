
import os
from functools import lru_cache

from django.conf import settings
from google import genai

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma


# ==========================================
# CONFIGURATION
# ==========================================

CHROMA_PATH = os.path.join(settings.BASE_DIR, "vector_db")


# ==========================================
# GEMINI CLIENT - LAZY INITIALIZATION
# ==========================================

@lru_cache(maxsize=1)
def get_gemini_client():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    return genai.Client(api_key=api_key)


# ==========================================
# HUGGING FACE EMBEDDINGS - LAZY LOADING
# ==========================================

@lru_cache(maxsize=1)
def get_embeddings():

    print("Loading embedding model for AI operation...")

    from langchain_huggingface import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    print("Embedding model loaded successfully.")

    return embeddings


# ==========================================
# GEMINI AI RESPONSE
# ==========================================

def ask_gemini(prompt):

    try:

        client = get_gemini_client()

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return response.text or "No response from AI."

    except Exception as e:

        print(f"Gemini Error: {e}")

        return "AI service is currently unavailable."


# ==========================================
# INDEX BOOK
# ==========================================

def index_book(book_id, book_path):

    persist_db_path = os.path.join(
        CHROMA_PATH,
        f"book_{book_id}"
    )

    if os.path.exists(persist_db_path):
        print(f"Book {book_id} already indexed.")
        return

    print(f"Indexing book: {book_path}")

    embeddings = get_embeddings()

    loader = PyPDFLoader(book_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(pages)

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_db_path
    )

    print(f"Book {book_id} indexed successfully.")


# ==========================================
# MAIN AI QUESTION ANSWERING
# ==========================================

def get_ai_response(question, book_id, book_path):

    try:

        embeddings = get_embeddings()

        persist_db_path = os.path.join(
            CHROMA_PATH,
            f"book_{book_id}"
        )

        if not os.path.exists(persist_db_path):
            index_book(book_id, book_path)

        db = Chroma(
            persist_directory=persist_db_path,
            embedding_function=embeddings
        )

        docs = db.similarity_search(
            question,
            k=3
        )

        if not docs:
            return "No relevant content found in the book."

        context = "\n\n".join(
            [doc.page_content[:300] for doc in docs]
        )

        prompt = f"""
You are an intelligent assistant that helps users understand a book.

STRICT RULES:
- Answer ONLY using the provided context.
- If the answer is not in context, say:
  "This is not covered in the book".
- Keep answers clear and simple.
- Use bullet points if helpful.

BOOK CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

        return ask_gemini(prompt)

    except Exception as e:

        print(f"AI ERROR: {e}")

        return "Something went wrong while processing your request."


# ==========================================
# BOOK SUMMARIZATION
# ==========================================

def summarize_book(book_id, book_path):

    try:

        embeddings = get_embeddings()

        persist_db_path = os.path.join(
            CHROMA_PATH,
            f"book_{book_id}"
        )

        if not os.path.exists(persist_db_path):
            index_book(book_id, book_path)

        db = Chroma(
            persist_directory=persist_db_path,
            embedding_function=embeddings
        )

        docs = db.similarity_search(
            "",
            k=8
        )

        summaries = []

        for doc in docs:

            prompt = f"""
Summarize the following text into short bullet points:

{doc.page_content[:500]}
"""

            summaries.append(ask_gemini(prompt))

        clean_summaries = "\n\n".join(summaries)

        final_prompt = f"""
Create a clear and organized final summary.

CONTENT:
{clean_summaries}

FINAL SUMMARY:
"""

        return ask_gemini(final_prompt)

    except Exception as e:

        print(f"Summarization error: {e}")

        return "Failed to summarize book."
