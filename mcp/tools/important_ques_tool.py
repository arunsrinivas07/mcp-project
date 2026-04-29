from mcp.tools.registry import tool_registry
from mcp.agents.llm_client import llm_client

@tool_registry.register("generate_important_questions")
def generate_important_questions(context: str):
    """
    Generates important exam-style questions from the content.
    """
    prompt = (
        "Identify and list 5 most important questions that could be asked in an exam based on this content.\n"
        "Provide a brief answer or reference for each question.\n\n"
        f"Content:\n{context}"
    )
    messages = [{"role": "user", "content": prompt}]
    return llm_client.complete(messages)
