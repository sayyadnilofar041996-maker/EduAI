import os
import fitz  # PyMuPDF
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

# ============================================================
# SETUP
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

VECTORSTORE_DIR = "vectorstore"

# Embedding model — converts text to vectors
embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# ============================================================
# STEP 1 — INDEX PDF (called when admin uploads a book)
# ============================================================

def index_pdf(pdf_path: str, book_id: int):
    """
    Reads PDF, splits into chunks, stores in ChromaDB.
    Called once when admin uploads a PDF.
    """

    # 1. Extract full text from PDF using PyMuPDF
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    # 2. Split text into small chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(full_text)

    # 3. Store chunks in ChromaDB
    collection_name = f"book_{book_id}"
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=VECTORSTORE_DIR
    )
    vectorstore.persist()

    print(f"✅ Indexed {len(chunks)} chunks for book {book_id}")


# ============================================================
# STEP 2 — RETRIEVE RELEVANT CHUNKS (called when student asks)
# ============================================================

def get_relevant_chunks(question: str, book_id: int) -> str:
    """
    Searches ChromaDB for chunks most relevant to the question.
    Returns them as a single string.
    """

    collection_name = f"book_{book_id}"

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=VECTORSTORE_DIR
    )

    # Find top 4 most relevant chunks
    results = vectorstore.similarity_search(question, k=4)

    # Join all chunks into one string
    context = "\n\n".join([doc.page_content for doc in results])

    return context


# ============================================================
# STEP 3 — DETECT DOUBT
# ============================================================

def detect_doubt(question: str) -> bool:
    """
    Returns True if student is confused.
    """
    doubt_phrases = [
        "didn't understand", "did not understand",
        "not understand", "confused", "samajh nahi aaya",
        "samajh nahi aya", "nahi samjha", "समझ नहीं",
        "don't understand", "explain again",
        "what do you mean", "not clear"
    ]
    question_lower = question.lower()
    return any(phrase in question_lower for phrase in doubt_phrases)


# ============================================================
# STEP 4 — BUILD SYSTEM PROMPT
# ============================================================

def build_system_prompt(grade: int, language: str,
                         doubt: bool, style: str) -> str:
    """
    Builds dynamic system prompt based on student profile.
    """

    # Grade based tone
    if grade <= 3:
        tone = "Use very simple words. Short sentences. Like talking to a 6 year old. Use emojis."
    elif grade <= 6:
        tone = "Use simple language. Give real life examples. Be friendly and encouraging."
    else:
        tone = "Use proper academic language. Give detailed explanations. Include formulas if needed."

    # Language
    if language == "hindi":
        lang_instruction = "Respond in Hindi language."
    elif language == "marathi":
        lang_instruction = "Respond in Marathi language."
    else:
        lang_instruction = "Respond in English language."

    # Doubt style
    if doubt:
        style_instruction = """
The student did not understand the previous explanation.
Change your explanation style COMPLETELY.
Use a story, a real life example, or a simple analogy.
Break it into very small steps.
Ask the student questions to check understanding.
"""
    else:
        style_instruction = """
Teach step by step.
After explaining, give a small exercise or question.
Encourage the student.
"""

    prompt = f"""
You are EduAI — a friendly AI teacher for school students.
You are teaching a Grade {grade} student.

{lang_instruction}
{tone}
{style_instruction}

Use ONLY the textbook content provided to you.
Do not add information from outside the textbook.
If the answer is not in the textbook content, say:
"This topic is not covered in your current textbook."
"""

    return prompt


# ============================================================
# STEP 5 — MAIN AI FUNCTION (called from chat.py)
# ============================================================

def get_ai_response(
    question: str,
    book_id: int,
    grade: int,
    language: str = "english",
    explanation_style: str = "normal"
) -> dict:
    """
    Main function called by chat.py
    Returns AI answer + doubt status + style used
    """

    # Detect if student is confused
    doubt = detect_doubt(question)
    style = "story" if doubt else explanation_style

    # Get relevant chunks from ChromaDB
    context = get_relevant_chunks(question, book_id)

    # Build system prompt
    system_prompt = build_system_prompt(grade, language, doubt, style)

    # Build final message to Groq
    user_message = f"""
Textbook Content:
{context}

Student Question:
{question}
"""

    # Call Groq API
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        max_tokens=1024
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "doubt_detected": doubt,
        "explanation_style": style,
        "chunks_used": len(context)
    }