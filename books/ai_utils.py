import os
from google import genai
from django.conf import settings

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# ==============================
# 🔑 GEMINI SETUP
# ==============================
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ==============================
# 📁 VECTOR DB PATH
# ==============================
CHROMA_PATH = os.path.join(settings.BASE_DIR, "vector_db")
os.makedirs(CHROMA_PATH, exist_ok=True)


# ==============================
# 📌 EMBEDDINGS (FREE LOCAL)
# ==============================
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )


# ==============================
# 🤖 GEMINI CALL
# ==============================


from transformers import pipeline

# Load once (global)
generator = pipeline(
    "text-generation",
    model="gpt2",
    max_new_tokens=200,
    pad_token_id=50256
)

def ask_gemini(prompt):
    result = generator(prompt)
    return result[0]["generated_text"]
##def ask_gemini(prompt):
##    try:
##        response = client.models.generate_content(
##            model="gemini-2.0-flash",   # ✅ WORKING MODEL
##            contents=prompt
##        )
##
##        return response.text if response.text else "No response from AI."
##
##    except Exception as e:
##        print(f"Gemini Error: {e}")
##        return "AI error occurred."

# ==============================
# 📚 INDEX BOOK (RUN ONCE)
# ==============================
def index_book(book_id, book_path):
    embeddings = get_embeddings()
    persist_db_path = os.path.join(CHROMA_PATH, f"book_{book_id}")

    if os.path.exists(persist_db_path):
        print(f"Book {book_id} already indexed.")
        return

    print(f"--- Indexing book: {book_path} ---")

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

    print(f"--- Indexing completed for book {book_id} ---")


# ==============================
# 🤖 MAIN AI FUNCTION
# ==============================
def get_ai_response(question, book_id, book_path):
    try:
        embeddings = get_embeddings()
        persist_db_path = os.path.join(CHROMA_PATH, f"book_{book_id}")

        # Ensure indexing
        if not os.path.exists(persist_db_path):
            index_book(book_id, book_path)

        db = Chroma(
            persist_directory=persist_db_path,
            embedding_function=embeddings
        )

        # 🔍 Search relevant chunks
        docs = db.similarity_search(question, k=3)

        if not docs:
            return "No relevant content found in the book."

        context = "\n\n".join([doc.page_content[:300] for doc in docs])

        # ✨ Prompt
        prompt = f"""
You are an intelligent assistant that helps users understand a book.

STRICT RULES:
- Answer ONLY using the provided context
- If answer is not in context, say: "This is not covered in the book"
- Keep answers clear and simple
- Use bullet points if helpful

---------------------
BOOK CONTEXT:
{context}
---------------------

QUESTION:
{question}

ANSWER:
"""

        # 🤖 Gemini response
        return ask_gemini(prompt)

    except Exception as e:
        print(f"AI ERROR: {e}")
        return "Something went wrong while processing your request."


def summarize_book(book_id, book_path):
    try:
        embeddings = get_embeddings()
        persist_db_path = os.path.join(CHROMA_PATH, f"book_{book_id}")

        # Ensure indexed
        if not os.path.exists(persist_db_path):
            index_book(book_id, book_path)

        db = Chroma(
            persist_directory=persist_db_path,
            embedding_function=embeddings
        )

        # Get multiple chunks
        docs = db.similarity_search("", k=8)

        summaries = []

        # 🔹 Step 1: Summarize each chunk
        for doc in docs:
            chunk = doc.page_content[:500]

            prompt = f"""
Summarize the following text into short bullet points:

{chunk}
"""

            summary = ask_gemini(prompt)  # ✅ USE SAME FUNCTION
            summaries.append(summary)

        # 🔹 Step 2: Combine summaries
        clean_summaries = "\n\n".join(summaries)

        final_prompt = f"""

CONTENT:
{clean_summaries}

FINAL SUMMARY:
"""

        final_summary = ask_gemini(final_prompt)  # ✅ FIXED

        return final_summary

    except Exception as e:
        print(e)
        return "Failed to summarize book."