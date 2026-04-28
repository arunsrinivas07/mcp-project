import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_llm(context, question):
    prompt = f"""
    You are a helpful study assistant.

    Use the content below to answer clearly.

    Content:
    {context}

    Question:
    {question}

    Answer in simple bullet points if possible.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content