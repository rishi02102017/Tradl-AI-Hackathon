"""Script to load mock news data into the database."""
import json
from datetime import datetime
from src.database.init_db import init_database
from src.database.db_session import get_db
from src.database.models import NewsArticle, Entity, StockImpact
from src.agents.orchestrator import NewsProcessingOrchestrator

def _parse_datetime(date_str):
    """Parse datetime string, handling Z suffix."""
    if not date_str:
        return datetime.utcnow()
    # Replace Z with +00:00 for ISO format
    date_str = date_str.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(date_str)
    except:
        return datetime.utcnow()

def load_mock_data():
    """Load mock news data and process it."""
    print("Initializing database...")
    init_database()
    
    print("Loading mock news data...")
    with open("data/mock_news.json", "r") as f:
        articles = json.load(f)
    
    print(f"Processing {len(articles)} articles through the pipeline...")
    orchestrator = NewsProcessingOrchestrator()
    result = orchestrator.process_articles(articles)
    
    print(f"\nProcessing Results:")
    print(f"  - Unique stories: {len(result.get('unique_stories', {}))}")
    print(f"  - Duplicate groups: {len(result.get('duplicates', {}))}")
    print(f"  - Articles with entities: {len(result.get('extracted_entities', {}))}")
    print(f"  - Articles with stock impacts: {len(result.get('stock_impacts', {}))}")
    
    print("\nSaving to database...")
    with get_db() as db:
        # Save unique stories
        for story_id, story_data in result.get('unique_stories', {}).items():
            existing = db.query(NewsArticle).filter(
                NewsArticle.article_id == story_id
            ).first()
            
            if not existing:
                story = NewsArticle(
                    article_id=story_id,
                    title=story_data.get('consolidated_title', ''),
                    content=story_data.get('consolidated_content', ''),
                    source=','.join(story_data.get('sources', [])),
                    published_at=_parse_datetime(story_data.get('published_at', datetime.utcnow().isoformat())),
                    url=story_data.get('url'),
                    is_duplicate=0
                )
                db.add(story)
        
        # Save all articles
        for article in articles:
            # Check if article already exists
            existing = db.query(NewsArticle).filter(
                NewsArticle.article_id == article['id']
            ).first()
            
            if existing:
                news_article = existing
            else:
                # Check if this is a duplicate
                is_duplicate = 0
                duplicate_of = None
                
                for unique_id, duplicate_ids in result.get('duplicates', {}).items():
                    if article['id'] in duplicate_ids and article['id'] != unique_id:
                        is_duplicate = 1
                        # Find the unique article
                        unique_article = db.query(NewsArticle).filter(
                            NewsArticle.article_id == unique_id
                        ).first()
                        if unique_article:
                            duplicate_of = unique_article.id
                        break
                
                # Save article
                news_article = NewsArticle(
                    article_id=article['id'],
                    title=article.get('title', ''),
                    content=article.get('content', ''),
                    source=article.get('source'),
                    published_at=_parse_datetime(article.get('published_at', datetime.utcnow().isoformat())),
                    url=article.get('url'),
                    is_duplicate=is_duplicate,
                    duplicate_of=duplicate_of
                )
                db.add(news_article)
                db.flush()
            
            # Save entities (only if not already saved)
            if not existing:
                entities = result.get('extracted_entities', {}).get(article['id'], {})
                for entity_type, entity_list in entities.items():
                    for entity in entity_list:
                        entity_obj = Entity(
                            article_id=news_article.id,
                            entity_type=entity_type,
                            entity_name=entity.get('name', ''),
                            confidence=entity.get('confidence', 1.0)
                        )
                        db.add(entity_obj)
                
                # Save stock impacts
                impacts = result.get('stock_impacts', {}).get(article['id'], [])
                for impact in impacts:
                    impact_obj = StockImpact(
                        article_id=news_article.id,
                        symbol=impact.get('symbol', ''),
                        confidence=impact.get('confidence', 0.0),
                        impact_type=impact.get('impact_type', ''),
                        reasoning=impact.get('reasoning', '')
                    )
                    db.add(impact_obj)
        
        db.commit()
    
    print("\n✅ Mock data loaded successfully!")
    print(f"\nSummary:")
    print(f"  - Total articles: {len(articles)}")
    print(f"  - Unique stories: {len(result.get('unique_stories', {}))}")
    
    # Count entities and impacts
    with get_db() as db:
        entity_count = db.query(Entity).count()
        impact_count = db.query(StockImpact).count()
        print(f"  - Total entities extracted: {entity_count}")
        print(f"  - Total stock impacts: {impact_count}")

if __name__ == "__main__":
    load_mock_data()

