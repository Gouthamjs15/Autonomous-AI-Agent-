# Autonomous-AI-Agent-



This project is an automated pipeline that performs browser-driven web searches, extracts relevant content, summarizes it using AI, and generates a clean PDF report.

key compomets used :

- **Browser Automation**: Used Playwright to automate the browser
- **Information Extraction**: Scrapy is used to visit the url and scrape the data from the relevant website
- **Summarization Engine**: Converts raw content into concise summaries using a local/external summarizer.
- **Keyword Extraction**: Identifies core keywords for each source using KeyBERT/spaCy.
- **PDF Generation**: Formats scraped and summarized content into a well-structured PDF (no Unicode errors, no emojis, images + tables supported).
- **File System Execution Layer**: Manages file creation, reading, and organization from the pipeline.

## Folder Structure

```
search_scrape_summarize/
├── search_urls.json          # URL list extracted from search
├── scraped_output.json       # Raw scraped + summarized output
├── final_summary.json        # Cleaned and structured final output
├── file_system_handler.py    # PDF generation + file ops
├── keyword_extractor.py      # Extracts keywords from summary
├── search_scrape_summarize.py# Main driver pipeline
├── summarizer.py             # Summary logic (external/local)
├── scrapy_project/
│   └── spiders/
│       └── search_spider.py  # Scrapy spider for URL crawling
```

## tools used 

| Purpose              | Tool/Library         |
|----------------------|----------------------|
| Browser Automation   | `Playwright`         |
| Web Scraping         | `Scrapy`, `BeautifulSoup` |
| Summarization        | External or Local LLM |
| Keyword Extraction   | `KeyBERT`, `spaCy`   |
| PDF Report Generator | `fpdf`               |


## Working  (End-to-End)

1. **Instruction Parsing**: Receives a command like:  
   _“Search smartphone reviews, extract pros/cons, generate PDF.”_

2. **Intent Detection**: Classifier tags the instruction as:  
   `web + summarization + file_handler`

3. **Pipeline Triggered**:
   - `Browser_automation.py` handles the flow
   - Scrapes URLs via `search_spider.py`
   - Extracts + summarizes content
   - Stores structured output in JSON
   - Generates PDF via `file_system_handler.py`

4. **PDF Output**:
   - Title
   - Source URLs
   - Summaries
   - Pros/Cons
   - Embedded images and tables
   - Clean keyword section

```bash
# Activate virtualenv
source venv/bin/activate  # or venv\Scripts\activate

# to run
python main.py

# Output PDF will be at:
# final_report.pdf
```
