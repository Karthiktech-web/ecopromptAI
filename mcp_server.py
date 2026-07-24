from mcp.server.fastmcp import FastMCP
import json

# Initialize FastMCP server
mcp = FastMCP("EcoPrompt Data Server")

# 1. Load an open-source dataset or local JSON file (e.g., prompt optimization rules)
PROMPT_RULES = [
    {"category": "Clarity", "rule": "Avoid conversational filler like 'please' or 'um' to save context window tokens."},
    {"category": "Role", "rule": "Define a clear persona for the model immediately (e.g., 'Act as an expert Python developer')."},
    {"category": "Format", "rule": "Specify output constraints, such as 'Return only JSON format'."}
]

@mcp.tool()
def get_optimization_guidelines(category: str = None) -> list:
    """Retrieve open-source prompt engineering guidelines from the server's dataset."""
    if category:
        return [rule for rule in PROMPT_RULES if rule["category"].lower() == category.lower()]
    return PROMPT_RULES

@mcp.tool()
def calculate_prompt_efficiency(prompt_text: str) -> dict:
    """Analyze prompt length, filler words, and calculate estimated token efficiency score."""
    words = prompt_text.split()
    word_count = len(words)
    fillers = ["um", "uh", "like", "just", "please", "kindly", "can you"]
    filler_count = sum(1 for w in words if w.lower() in fillers)
    
    score = max(0, 100 - (filler_count * 15) - max(0, (word_count - 50) // 2))
    
    return {
        "word_count": word_count,
        "filler_words_detected": filler_count,
        "efficiency_score": score,
        "recommendation": "Prompt is concise and efficient." if score > 75 else "Consider removing conversational filler to save tokens."
    }

if __name__ == "__main__":
    mcp.run()