from groq import Groq
import fitz  # PyMuPDF
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Configure Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"  # free, fast, very capable


# ─────────────────────────────────────────────
# EXTRACT TEXT FROM PDF
# ─────────────────────────────────────────────
def extract_pdf_text(file_path: str, max_pages: int = 10) -> str:
    try:
        doc = fitz.open(file_path)
        text = ""
        for i, page in enumerate(doc):
            if i >= max_pages:
                break
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        return f"Could not read PDF: {str(e)}"


# ─────────────────────────────────────────────
# DETECT DOUBT IN STUDENT MESSAGE
# ─────────────────────────────────────────────
def detect_doubt(question: str) -> bool:
    doubt_phrases = [
        "didn't understand", "did not understand",
        "samajh nahi aaya", "samajh nahi aya",
        "not clear", "confusing", "confused",
        "explain again", "samjhao", "dobara batao",
        "समझ नहीं आया", "फिर से बताओ",
        "समजले नाही", "परत सांग"
    ]
    question_lower = question.lower()
    return any(phrase in question_lower for phrase in doubt_phrases)


# ─────────────────────────────────────────────
# BUILD SYSTEM PROMPT
# ─────────────────────────────────────────────
def build_system_prompt(
    grade: int,
    language: str,
    doubt_detected: bool,
    explanation_style: str
) -> str:

    if grade <= 3:
        tone = "Use very simple words, short sentences, and fun examples like toys or animals. Be very encouraging and friendly like a kind parent."
    elif grade <= 6:
        tone = "Use simple but complete explanations. Use relatable examples from daily life. Be friendly and encouraging like a supportive teacher."
    elif grade <= 8:
        tone = "Use clear explanations with proper terms. Include examples and analogies. Be like a knowledgeable but approachable teacher."
    else:
        tone = "Use detailed, thorough explanations with proper academic language. Include examples, and connect concepts. Be like a subject expert teacher."

    if language == "hindi":
        lang_instruction = "Respond completely in Hindi language using Devanagari script."
    elif language == "marathi":
        lang_instruction = "Respond completely in Marathi language using Devanagari script."
    else:
        lang_instruction = "Respond in clear English."

    if doubt_detected:
        if explanation_style == "story":
            style_instruction = "The student did not understand. Explain using a short interesting story that makes the concept clear."
        elif explanation_style == "example":
            style_instruction = "The student did not understand. Use a very simple real-life example. Start from scratch."
        else:
            style_instruction = "The student did not understand. Use an analogy or comparison to something familiar."
    else:
        style_instruction = "Teach step by step. After explaining, ask the student one simple question to check understanding."

    return f"""You are EduAI — a friendly AI teacher for grade {grade} students.
    
{tone}
{lang_instruction}
{style_instruction}

Always follow this structure:
1. Explain the concept clearly
2. Give a real example
3. If appropriate, describe a simple diagram in text
4. Ask one follow-up question to check understanding
5. Suggest one practice exercise"""


# ─────────────────────────────────────────────
# MAIN FUNCTION — Ask Groq
# ─────────────────────────────────────────────
def ask_gemini(
    question: str,
    pdf_text: str,
    grade: int,
    language: str,
    doubt_detected: bool,
    explanation_style: str
) -> str:
    """We keep the function name ask_gemini so chat.py doesn't need changes."""

    system_prompt = build_system_prompt(
        grade, language, doubt_detected, explanation_style
    )

    pdf_context = pdf_text[:3000] if len(pdf_text) > 3000 else pdf_text

    user_message = f"""--- TEXTBOOK CONTENT ---
{pdf_context}
--- END OF TEXTBOOK ---

Student's question: {question}

Answer the student's question based on the textbook content above."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI could not respond at this time: {str(e)}"