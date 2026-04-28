import fitz
from core.ocr import ocr_from_pdf
from core.retriever import create_index, set_active_index
from core.database import cursor, conn
import re

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def split_into_topics(text):
    topics = re.split(r'\n[A-Z][^\n]{3,}\n', text)
    return [t.strip() for t in topics if len(t.strip()) > 100]

def process_pdf(path):
    text = extract_text_from_pdf(path)

    if len(text.strip()) < 100:
        text = ocr_from_pdf(path)

    # 🔹 store topics
    topics = split_into_topics(text)

    cursor.execute("DELETE FROM topics")

    for t in topics:
        cursor.execute(
            "INSERT INTO topics (content, used) VALUES (?, 0)",
            (t,)
        )

    conn.commit()

    print("Topics stored:", len(topics))

    # 🔹 create chunks for RAG
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    index, _ = create_index(chunks)
    
    # store globally
    set_active_index(chunks, index)

    return chunks, index