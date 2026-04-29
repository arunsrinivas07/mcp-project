from mcp.tools.registry import tool_registry
from mcp.agents.llm_client import llm_client

@tool_registry.register("generate_mindmap")
def generate_mindmap(context: str):
    """
    Generates a structured hierarchical overview (mindmap) of the content.
    """
    prompt = (
        "Create a structured hierarchical mind map of the following content.\n"
        "Use Markdown-style indentation (e.g., # Main Topic, ## Sub Topic, - Detail) to show relationships.\n\n"
        f"Content:\n{context}"
    )
    messages = [{"role": "user", "content": prompt}]
    return llm_client.complete(messages)