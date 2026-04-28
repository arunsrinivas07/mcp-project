import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    

def generate_quiz_tool(content):
    prompt = f"""
Generate 5 Multiple Choice Questions (MCQs) based on the following content.
Format:
1. [Question]
A) [Option]
B) [Option]
C) [Option]
D) [Option]
Correct: [Letter]

Content: {content}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content