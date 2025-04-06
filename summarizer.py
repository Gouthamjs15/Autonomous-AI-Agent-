from transformers import pipeline

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_text(text, max_len=1024):
    try:
        chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]
        results = summarizer(chunks[:3], max_length=150, min_length=40, do_sample=False)
        return " ".join([res["summary_text"] for res in results])
    except Exception as e:
        return f"[Summarization failed: {e}]"
