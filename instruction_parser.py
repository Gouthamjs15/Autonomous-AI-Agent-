# instruction_parser.py

import os
from transformers import pipeline
from Browser_automation import run_pipeline  # Entry point for web task execution

# Zero-shot model for future extension (currently not used in logic)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Intent mappings
INTENT_TYPES = {
    "list files": "terminal",
    "list pdf files": "terminal",
    "show current directory": "terminal",
    "show python files": "terminal",
    "remove temp files": "terminal",
    "search web": "web",
    "search and summarize": "web",
    "search and save to file": "web",
    "summarize content": "web",
    "headlines only": "web",
    "extract keywords": "file_handler",
    "generate pdf report": "file_handler",
    "generate pdf report from last search": "file_handler",
    "save final report": "file_handler",
    "export to pdf": "file_handler",
    "file operations": "file_handler",
    "file_handler": "file_handler",
    "unknown": "unknown"
}

# Terminal and pipeline command maps
COMMAND_MAP = {
    "list files": "dir" if os.name == "nt" else "ls",
    "list pdf files": "dir *.pdf" if os.name == "nt" else "ls *.pdf",
    "show current directory": "cd",
    "show python files": "dir *.py" if os.name == "nt" else "ls *.py",
    "remove temp files": "del *.tmp" if os.name == "nt" else "rm *.tmp",
    "search web": ["scrape"],
    "search and save to file": ["scrape"],
    "search and summarize": ["scrape", "summarize"],
    "summarize content": ["summarize"],
    "headlines only": ["scrape", "headlines"],
    "extract keywords": ["extract_keywords"],
    "generate pdf report": ["export_to_pdf"],
    "save final report": ["export_to_pdf"],
    "export to pdf": ["export_to_pdf"],
    "generate pdf report from last search": ["extract_keywords", "export_to_pdf"]
}

INTENT_LABELS = list(INTENT_TYPES.keys())

def parse_instruction(instruction: str) -> dict:
    instruction = instruction.lower()
    commands = set()
    intent = "unknown"

    # 🔍 Multi-intent classification via keywords
    web_keywords = ["search", "find", "extract", "research"]
    terminal_keywords = ["bash", "shell", "terminal"]
    file_keywords = ["save", "write", "export", "pdf", "create file"]

    if any(k in instruction for k in terminal_keywords):
        intent = "terminal"
    elif any(k in instruction for k in web_keywords):
        intent = "web"
    elif any(k in instruction for k in file_keywords):
        intent = "file_handler"

    # 🧠 Rule-based command detection
    if "headlines" in instruction:
        commands.add("extract_headlines")
    if any(k in instruction for k in ["reviews", "pros", "cons"]):
        commands.add("scrape_reviews")
        commands.add("extract_pros_cons")
    if any(k in instruction for k in ["analyze", "trends"]):
        commands.add("analyze_trends")
    if any(k in instruction for k in ["summarize", "summary"]):
        commands.add("summarize")
    if any(k in instruction for k in ["chart", "graph"]):
        commands.add("generate_charts")
    if any(k in instruction for k in ["save", "pdf", "export"]):
        commands.add("export_to_pdf")

    # ✅ Safe fallback
    if not commands:
        commands.add("general_task")

    # 🧠 Composite instruction label
    if "headlines" in instruction:
        label = "search and extract headlines"
    elif "reviews" in instruction:
        label = "extract pros/cons from reviews"
    elif "energy" in instruction and "trends" in instruction:
        label = "analyze energy trends and generate PDF"
    else:
        label = "general web + file instruction"

    return {
        "intent": intent,
        "commands": list(commands),
        "label": label,
        "score": 0.99  # Hardcoded for now, can be dynamic with classifier later
    }

# 🧪 CLI test
if __name__ == "__main__":
    user_input = input("🔍 Enter your instruction: ")
    result = parse_instruction(user_input)

    print("\n[🧠] Parsed Intent:", result["intent"])
    print("[⚡] Best Match Label:", result["label"])
    print("[📜] Commands:", result["commands"])
    print("[📊] Confidence Score:", result["score"])

    # Trigger pipeline if it's a web intent
    if result["intent"] == "web":
        run_pipeline(user_input, result["intent"], result["commands"])
