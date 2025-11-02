import json

def load_tools():
    with open("tools.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_tools(tools):
    with open("tools.json", "w", encoding="utf-8") as f:
        json.dump(tools, f, indent=2)

def get_matching_tools(prompt):
    tools = load_tools()
    prompt_lower = prompt.lower()

    matches = []
    for tool in tools:
        name = tool.get("name", "").lower()
        desc = tool.get("description", "").lower()
        tags = " ".join(tool.get("tags", [])).lower()
        full_text = f"{name} {desc} {tags}"

        if prompt_lower in full_text:
            matches.append(tool)
    return matches
{
    "name": "ToolName",
    "description": "Some AI tool",
    "tags": ["design", "productivity"],
    "rating": 4.5,
    "pricing": "Free",
    "url": "https://example.com"
}


import json

def load_tools():
    with open("tools.json", "r") as f:
        return json.load(f)
