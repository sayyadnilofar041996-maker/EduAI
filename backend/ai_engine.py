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

embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# ============================================================
# STEP 1 — INDEX PDF
# ============================================================

def index_pdf(pdf_path: str, book_id: int):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(full_text)

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
# STEP 2 — RETRIEVE RELEVANT CHUNKS
# ============================================================

def get_relevant_chunks(question: str, book_id: int) -> str:
    collection_name = f"book_{book_id}"

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=VECTORSTORE_DIR
    )

    results = vectorstore.similarity_search(question, k=4)
    context = "\n\n".join([doc.page_content for doc in results])

    return context


# ============================================================
# STEP 3 — DETECT DOUBT
# ============================================================

def detect_doubt(question: str) -> bool:
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

def build_system_prompt(
    grade: int,
    language: str,
    doubt: bool,
    style: str,
    subject: str = "your subject"
) -> str:

    # Grade based tone
    if grade <= 4:
        tone = f"""
You are teaching a very young child in Grade {grade}.
ALWAYS use one of these styles:
- Tell a fun story to explain the topic
- Use simple real life examples (toys, food, animals, family)
- Draw simple text diagrams like:
    🌱 Seed → 💧 Water + ☀️ Sunlight → 🌿 Plant grows!
- Use LOTS of emojis to make it fun
- Very short sentences. One idea at a time.
- Never use difficult words. If you must, explain it immediately.
- Always end with a fun question like "Can you tell me one thing you learned? 😊"
"""
    elif grade <= 6:
        tone = f"""
You are teaching a middle school student in Grade {grade}.
- Use simple language with real life examples
- Add short text diagrams when helpful
- Be friendly, warm and encouraging
- Give one example from daily life for every concept
- End with a small question or exercise
"""
    else:
        tone = f"""
You are teaching a senior school student in Grade {grade}.
- Use proper academic language
- Give detailed step by step explanations
- Include formulas, definitions and diagrams where needed
- Challenge the student with follow up questions
- Be encouraging but academic in tone
"""

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
- Use a story or fun analogy this time
- Break into very tiny baby steps
- Use emojis and simple diagrams
- Ask the student questions to check understanding
"""
    else:
        style_instruction = """
- Teach step by step clearly
- After explaining, give a small exercise or question
- Be warm and encouraging throughout
"""

    prompt = f"""
You are EduAI — a friendly, fun and caring AI teacher for school students.
You are teaching a Grade {grade} student.
The student's selected subject is: {subject}

{lang_instruction}
{tone}
{style_instruction}

TEACHING INSTRUCTIONS:
1. First use the textbook content provided to explain the topic.
2. If the textbook content is incomplete, add your own knowledge to make the explanation full and clear.
3. If the textbook has no diagram or analogy, create one yourself using simple text diagrams and emojis.
4. Always make the student fully understand — textbook first, then supplement with extra knowledge.
5. Never say "this is not in your textbook" — always teach completely.
6. If the student is just greeting (hi, hello) — respond warmly and ask what they want to learn in {subject} today.

SUBJECT BOUNDARY INSTRUCTIONS:
7. The student has selected the subject: {subject}.
   If the student asks about a COMPLETELY DIFFERENT subject
   (example: asks about Science when they selected Math),
   respond politely like this:
   "I am your {subject} teacher today! 😊 I can only help you with {subject} topics.
   For other subjects, please go back to the dashboard and select that book.
   Now shall we continue with {subject}? 📚"
   Always redirect gently and kindly.
8. If the question is loosely related to {subject} — answer briefly
   and bring focus back to the textbook topic.

MOTIVATION INSTRUCTIONS — VERY IMPORTANT:
9. If the student answers a question CORRECTLY — celebrate enthusiastically!
   Use different messages each time:
   - "🌟 Excellent! You got it right! You are so smart!"
   - "🎉 Wow! Perfect answer! I am so proud of you!"
   - "⭐ Amazing! You remembered that so well!"
   - "🏆 Champion! That is 100% correct!"
10. If the student answers PARTIALLY correct — encourage and guide:
    - "Good try! You got part of it right! Let me help with the rest..."
11. If the student answers INCORRECTLY — be gentle and kind:
    - "Good effort! Let's try again together..."
    - Never make the student feel bad or stupid.

DIAGRAM STYLE — use simple text art like:
   ☀️ Sunlight
      ↓
   🌿 Leaf absorbs light
      ↓
   💧 Water + CO2
      ↓
   🍬 Glucose (food) + O2 released

Always make learning FUN, SAFE and ENCOURAGING! 🎓
"""

    return prompt


# ============================================================
# STEP 5 — MAIN AI FUNCTION
# ============================================================

def get_ai_response(
    question: str,
    book_id: int,
    grade: int,
    language: str = "english",
    explanation_style: str = "normal",
    subject: str = "your subject"
) -> dict:

    # Detect doubt
    doubt = detect_doubt(question)
    style = "story" if doubt else explanation_style

    # Get relevant chunks from ChromaDB
    context = get_relevant_chunks(question, book_id)

    # Build system prompt
    system_prompt = build_system_prompt(
        grade=grade,
        language=language,
        doubt=doubt,
        style=style,
        subject=subject
    )

    # Build user message
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
        "answer":           answer,
        "doubt_detected":   doubt,
        "explanation_style": style,
        "chunks_used":      len(context)
    }


# ============================================================
# STEP 6 — EXTRACT CHAPTERS FROM PDF — 3 LAYER SYSTEM
# ============================================================

def extract_chapters_from_pdf(pdf_path: str, book_id: int) -> list:
    print(f"📖 Extracting chapters from: {pdf_path}")

    # LAYER 1 — PyMuPDF built-in TOC
    try:
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()
        doc.close()

        if toc and len(toc) > 2:
            print("✅ Layer 1 — TOC found in PDF")
            return _parse_toc(toc)

    except Exception as e:
        print(f"⚠️ Layer 1 failed: {e}")

    # LAYER 2 — Scan first 10 pages for patterns
    try:
        doc = fitz.open(pdf_path)
        scan_text = ""
        for i in range(min(10, len(doc))):
            scan_text += doc[i].get_text()
        doc.close()

        result = _parse_text_patterns(scan_text)
        if result and len(result) > 2:
            print("✅ Layer 2 — Pattern found in first 10 pages")
            return result

    except Exception as e:
        print(f"⚠️ Layer 2 failed: {e}")

    # LAYER 3 — Groq AI reads the index page
    try:
        doc = fitz.open(pdf_path)
        index_text = ""
        for i in range(min(8, len(doc))):
            index_text += f"\n--- Page {i+1} ---\n"
            index_text += doc[i].get_text()
        doc.close()

        result = _extract_with_groq(index_text)
        if result:
            print("✅ Layer 3 — Groq AI extracted chapters")
            return result

    except Exception as e:
        print(f"⚠️ Layer 3 failed: {e}")

    # ALL LAYERS FAILED
    print("❌ No chapters found — student can ask freely")
    return []


# ============================================================
# LAYER 1 HELPER — Parse PyMuPDF TOC
# ============================================================

def _parse_toc(toc: list) -> list:
    chapters = []
    current_unit_number = 0
    current_unit_name = "Unit 1"
    chapter_order = 0

    for item in toc:
        level, title, page = item

        if level == 1:
            current_unit_number += 1
            current_unit_name = title
            chapter_order = 0

        elif level == 2:
            chapter_order += 1
            chapters.append({
                "unit_number":   current_unit_number,
                "unit_name":     current_unit_name,
                "chapter_name":  title,
                "chapter_order": chapter_order
            })

    return chapters


# ============================================================
# LAYER 2 HELPER — Parse text patterns
# ============================================================

def _parse_text_patterns(text: str) -> list:
    import re

    chapters = []
    lines = text.split('\n')
    lines = [l.strip() for l in lines if l.strip()]

    current_unit_number = 0
    current_unit_name = ""
    chapter_order = 0

    word_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8,
        "nine": 9, "ten": 10
    }

    unit_pattern = re.compile(
        r'^(unit|chapter|section)\s+(\w+)$',
        re.IGNORECASE
    )

    for line in lines:
        match = unit_pattern.match(line)
        if match:
            num_word = match.group(2).lower()
            current_unit_number = word_to_num.get(
                num_word,
                current_unit_number + 1
            )
            current_unit_name = line.title()
            chapter_order = 0

        elif current_unit_name and len(line) > 3 and len(line) < 60:
            if not line.isdigit():
                chapter_order += 1
                chapters.append({
                    "unit_number":   current_unit_number,
                    "unit_name":     current_unit_name,
                    "chapter_name":  line,
                    "chapter_order": chapter_order
                })

    return chapters


# ============================================================
# LAYER 3 HELPER — Groq AI extraction
# ============================================================

def _extract_with_groq(index_text: str) -> list:
    import json

    prompt = """
You are a textbook parser.
Look at this textbook index/contents page text.
Extract all units and their chapters/lessons.

Return ONLY a JSON array like this — no explanation, no extra text:
[
    {
        "unit_number": 1,
        "unit_name": "Unit One",
        "chapter_name": "A Happy Song",
        "chapter_order": 1
    },
    {
        "unit_number": 1,
        "unit_name": "Unit One",
        "chapter_name": "Nature",
        "chapter_order": 2
    }
]

Rules:
- If there are no units, use unit_number=1 and unit_name="Chapters"
- Each individual lesson or topic = one chapter entry
- Keep chapter names exactly as they appear in the text
- Return ONLY the JSON array, nothing else
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": f"Textbook index text:\n{index_text}"}
        ],
        max_tokens=2000
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    chapters = json.loads(raw)
    return chapters