from mcp.tools.retrieval_tool import search_notes
from mcp.tools.quiz_tool import generate_quiz_tool
from mcp.tools.summary_tool import summarize
from mcp.tools.fallback_tool import no_pdf_tool

TOOLS = [
    {
        "name": "search_notes",
        "description": "Retrieve relevant content from uploaded PDF",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        },
        "function": search_notes
    },
    {
        "name": "summarize",
        "description": "Summarize given content",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"}
            },
            "required": ["content"]
        },
        "function": summarize
    },
    {
        "name": "generate_quiz",
        "description": "Generate quiz from given content",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"}
            },
            "required": ["content"]
        },
        "function": generate_quiz_tool
    },
    {
    "name": "no_pdf_tool",
    "description": "Use when no PDF content is available",
    "input_schema": {
        "type": "object",
        "properties": {}
    },
    "function": no_pdf_tool
}
]