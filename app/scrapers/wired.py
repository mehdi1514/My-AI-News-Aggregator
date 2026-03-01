from datetime import datetime, timezone, timedelta
import feedparser
from typing import List, Optional
from docling.document_converter import DocumentConverter
from pydantic import BaseModel



class WiredArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None
    markdown: Optional[str] = None

class WiredScraper:
    FEED_URL = "https://www.wired.com/feed/tag/ai/latest/rss"
    
    def __init__(self):
        self.converter = DocumentConverter()

    def get_articles(self, hours: int = 24) -> List[WiredArticle]:
        feed = feedparser.parse(self.FEED_URL)
        articles: List[WiredArticle] = []
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        for entry in feed.entries:
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                # published_parsed is a time.struct_time in UTC
                dt = datetime(*entry.published_parsed[:6])
                published_at = dt.replace(tzinfo=timezone.utc)
            else:
                published_at = datetime.now(timezone.utc)
            
            if published_at < cutoff_time:
                continue

            # category might be a list of tags in feedparser
            category = "AI"
            if hasattr(entry, 'tags') and entry.tags:
                # Use the first tag as category
                category = entry.tags[0].term
            elif hasattr(entry, 'category'):
                category = entry.category
            
            articles.append({
                "title": entry.title,
                "url": entry.link,
                "published_at": published_at,
                "description": entry.description,
                "category": category
            })
            
        return articles

    def url_to_markdown(self, url: str) -> Optional[str]:
        try:
            result = self.converter.convert(url)
            return result.document.export_to_markdown()
        except Exception as e:
            print(f"Error converting URL to markdown: {e}")
            return None

if __name__ == "__main__":
    scraper = WiredScraper()
    articles = scraper.get_articles()
    print(f"Found {len(articles)} articles")
    for a in articles[:3]:
        print(f"- {a['title']} ({a['published_at']})")
    print(scraper.url_to_markdown(articles[0]['url']))
