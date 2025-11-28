"""News ingestion service for periodic polling."""
import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)


class NewsIngestionService:
    """Service for ingesting news from various sources."""
    
    def __init__(self):
        self.sources = {
            'nse': 'https://www.nseindia.com/rss',
            'bse': 'https://www.bseindia.com/rss',
            'rbi': 'https://www.rbi.org.in/rss'
        }
    
    def fetch_from_rss(self, rss_url: str, source_name: str) -> List[Dict]:
        """Fetch news from RSS feed."""
        articles = []
        
        try:
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:10]:  # Limit to 10 most recent
                article = {
                    'id': f"{source_name.upper()}_{entry.get('id', entry.get('link', ''))}",
                    'title': entry.get('title', ''),
                    'content': entry.get('summary', entry.get('description', '')),
                    'source': source_name.upper(),
                    'published_at': self._parse_date(entry.get('published', '')),
                    'url': entry.get('link', '')
                }
                articles.append(article)
        
        except Exception as e:
            logger.error(f"Error fetching from RSS {rss_url}: {e}")
        
        return articles
    
    def fetch_from_mock_data(self, file_path: str) -> List[Dict]:
        """Fetch news from mock JSON file."""
        import json
        
        try:
            with open(file_path, 'r') as f:
                articles = json.load(f)
            return articles
        except Exception as e:
            logger.error(f"Error loading mock data: {e}")
            return []
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format."""
        try:
            # Try parsing with feedparser's date parser
            import feedparser
            parsed = feedparser._parse_date(date_str)
            if parsed:
                return datetime(*parsed[:6]).isoformat()
        except:
            pass
        
        return datetime.utcnow().isoformat()
    
    def poll_sources(self, use_mock: bool = True) -> List[Dict]:
        """Poll all sources for new articles."""
        all_articles = []
        
        if use_mock:
            # Use mock data for demo
            mock_path = "data/mock_news.json"
            articles = self.fetch_from_mock_data(mock_path)
            all_articles.extend(articles)
        else:
            # Poll real RSS feeds
            for source_name, rss_url in self.sources.items():
                articles = self.fetch_from_rss(rss_url, source_name)
                all_articles.extend(articles)
                time.sleep(1)  # Rate limiting
        
        return all_articles
    
    def start_periodic_polling(
        self,
        interval_seconds: int = 3600,
        callback=None,
        use_mock: bool = True
    ):
        """Start periodic polling of news sources."""
        import threading
        
        def poll_loop():
            while True:
                try:
                    articles = self.poll_sources(use_mock=use_mock)
                    if callback:
                        callback(articles)
                except Exception as e:
                    logger.error(f"Error in polling loop: {e}")
                
                time.sleep(interval_seconds)
        
        thread = threading.Thread(target=poll_loop, daemon=True)
        thread.start()
        return thread

