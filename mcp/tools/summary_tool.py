from core.llm import ask_llm

def summarize(content):
    return ask_llm(content, "Summarize clearly in bullet points")