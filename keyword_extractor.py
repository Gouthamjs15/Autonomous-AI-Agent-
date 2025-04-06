from keybert import KeyBERT
import json

def extract_keywords(summary_path, output_path="keywords.json"):
    kw_model = KeyBERT()
    
    with open(summary_path, "r", encoding="utf-8") as f:
        summaries = json.load(f)
    
    results = {}
    for entry in summaries:
        url = entry.get("url")
        summary = entry.get("summary", "")
        keywords = [kw[0] for kw in kw_model.extract_keywords(summary, top_n=5)]
        results[url] = keywords

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"[✓] Keywords saved to {output_path}")
    return output_path  # 🛠️ THIS LINE WAS MISSING
