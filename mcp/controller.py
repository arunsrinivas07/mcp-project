from core.llm import client
from mcp.tools.registry import TOOLS
import json


def get_tool(name):
    """
    Retrieves a tool function from the registry by its name.
    
    Args:
        name (str): The name of the tool to find.
        
    Returns:
        callable or None: The function associated with the tool name.
    """
    for t in TOOLS:
        if t["name"] == name:
            return t["function"]
    return None


def mcp_handle(query):
    """
    The main controller for handling user queries using the MCP architecture.
    It follows a fixed workflow: Retrieval -> Intent Classification -> Tool Execution.
    
    Args:
        query (str): The user's input question or command.
        
    Returns:
        str: The AI's response or tool output.
    """

    # 🔥 ALWAYS start with retrieval
    search_fn = get_tool("search_notes")
    summarize_fn = get_tool("summarize")
    quiz_fn = get_tool("generate_quiz")

    if not search_fn:
        return "Error: search tool missing"

    # STEP 1 → SEARCH
    content = search_fn(query)

    if not content:
        return "Please upload a PDF first."

    # STEP 2 → decide action (LLM only decides THIS)
    decision = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "Decide intent: return ONLY one word: summarize OR quiz"
            },
            {
                "role": "user",
                "content": query
            }
        ]
    )

    intent = decision.choices[0].message.content.lower().strip()

    # 🔥 STEP 3 → EXECUTE TOOL (NO MCP CHAOS)
    if "quiz" in intent:
        return quiz_fn(content)

    return summarize_fn(content)