import asyncio
import json
from playwright.async_api import async_playwright
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from summarizer import summarize_text
from search_spider import SearchSpider
from keyword_extractor import extract_keywords
from file_system_handler import generate_pdf
from content_scraper import extract_structured_content

import logging
logging.getLogger("pdfminer").setLevel(logging.WARNING)

# -------------------- Search URLs using Playwright --------------------
async def get_top_search_urls(query, num_results=5):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.bing.com/")
        await page.wait_for_selector("input[name=q]", timeout=10000)
        await page.fill("input[name=q]", query)
        await page.keyboard.press("Enter")
        await page.wait_for_selector("li.b_algo h2 a", timeout=10000)

        urls = await page.eval_on_selector_all(
            "li.b_algo h2 a", "elements => elements.map(el => el.href)"
        )

        # Scrape images/tables from search page
        page_html = await page.content()
        structured_data = extract_structured_content(page_html, page.url)
        images, tables = structured_data['images'], structured_data['tables']
        print(f"[+] Extracted from search page: Images: {len(images)}, Tables: {len(tables)}")

        await browser.close()
        return urls[:num_results] if urls else []

# -------------------- Scrape URLs using Scrapy --------------------
def run_scrapy_spider(urls):
    settings = get_project_settings()
    settings.set("FEEDS", {
        "scraped_output.json": {
            "format": "json",
            "overwrite": True
        }
    })
    process = CrawlerProcess(settings)
    process.crawl(SearchSpider, urls=urls)
    process.start()

# -------------------- Main Execution Logic --------------------
async def main(query, intents=None, commands=None):
    intents = intents or []
    commands = commands or []

    print("[+] Starting search...")
    urls = await get_top_search_urls(query)

    if not urls:
        print("[❌] No URLs found. Aborting pipeline.")
        return

    print("[+] URLs found:", urls)
    with open("search_urls.json", "w") as f:
        json.dump(urls, f, indent=2)

    if any(cmd in commands for cmd in ["scrape", "summarize", "headlines"]):
        print("[+] Running Scrapy spider...")
        run_scrapy_spider(urls)

    try:
        with open("scraped_output.json", "r") as f:
            scraped_data = json.load(f)
    except FileNotFoundError:
        print("[❌] Scraped output not found. Skipping downstream tasks.")
        return

    if "summarize" in commands:
        print("[+] Summarizing scraped data...")
        summaries = []
        for entry in scraped_data:
            summary = summarize_text(entry["text"])
            summaries.append({"url": entry["url"], "summary": summary})

        with open("final_summary.json", "w") as f:
            json.dump(summaries, f, indent=2)
        print("[✓] Summaries saved in final_summary.json")

    if "headlines" in commands:
        print("[+] Extracting just headlines...")
        headlines = [{"url": entry["url"], "headline": entry["text"].split('\n')[0]} for entry in scraped_data]

        with open("headlines.json", "w") as f:
            json.dump(headlines, f, indent=2)
        print("[✓] Headlines saved in headlines.json")

    keyword_file = None
    if "extract_keywords" in commands:
        print("[+] Extracting keywords...")
        keyword_file = extract_keywords("final_summary.json", "keywords.json")
        print("[✓] Keywords saved in", keyword_file)

    if "export_to_pdf" in commands or "save_to_file" in commands:
        print("[+] Generating PDF report...")
        summary_file = "final_summary.json"
        if summary_file and (not keyword_file or keyword_file.endswith(".json")):
            generate_pdf(summary_file, keyword_file)
        else:
            print("[❌] Cannot generate PDF. Summary or keyword file missing.")

    print("[🏁] Pipeline complete.")

# -------------------- Entrypoint for Router --------------------
def run_pipeline(instruction, intents, commands):
    print(f"[🚀] Running web pipeline for: {instruction}")
    asyncio.run(main(instruction, intents, commands))

# -------------------- Standalone Debug/Test --------------------
if __name__ == "__main__":
    test_query = input("🔍 Enter your search query: ")
    dummy_intents = ["web", "file_handler"]
    dummy_commands = ["scrape", "summarize", "extract_keywords", "export_to_pdf"]
    asyncio.run(main(test_query, dummy_intents, dummy_commands))
