import scrapy
from content_scraper import scrape_content

class SearchSpider(scrapy.Spider):
    name = "search_spider"

    def __init__(self, urls=None, *args, **kwargs):
        super(SearchSpider, self).__init__(*args, **kwargs)
        self.start_urls = urls or []

    def parse(self, response):
        url = response.url
        html = response.text

        try:
            entry = scrape_content(html, url)
            self.log(f"[🖼️] Extracted {len(entry['images'])} images, "
                     f"{len(entry['tables'])} tables from {url}")

            yield {
                "url": url,
                "text": entry.get("text", ""),
                "images": entry.get("images", []),
                "tables": entry.get("tables", []),
                "pros": entry.get("pros", []),
                "cons": entry.get("cons", [])
            }

        except Exception as e:
            self.logger.error(f"[❌] Error processing {url}: {e}")
