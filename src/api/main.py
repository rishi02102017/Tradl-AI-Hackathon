"""FastAPI application for financial news intelligence system."""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import os
from datetime import datetime

from src.agents.orchestrator import NewsProcessingOrchestrator
from src.services.query_service import QueryService
from src.database.db_session import get_db
from src.database.models import NewsArticle, Entity, StockImpact, UniqueStory
from src.services.ingestion_service import NewsIngestionService

app = FastAPI(title="Financial News Intelligence System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
orchestrator = NewsProcessingOrchestrator()
query_service = QueryService()
ingestion_service = NewsIngestionService()


# Pydantic models
class NewsArticleInput(BaseModel):
    title: str
    content: str
    source: Optional[str] = None
    published_at: Optional[str] = None
    url: Optional[str] = None


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    query: str
    query_intent: str
    extracted_entities: Dict
    relevant_articles: List[Dict]
    count: int


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Financial News Intelligence System API",
        "version": "1.0.0",
        "endpoints": {
            "ingest": "POST /ingest - Ingest new news articles",
            "query": "GET /query?q=<query> - Query news with natural language",
            "news": "GET /news/{news_id} - Get specific news article",
            "entities": "GET /entities - Get all extracted entities",
            "stocks": "GET /stocks/{symbol}/news - Get news for a specific stock"
        }
    }


@app.post("/ingest")
async def ingest_news(
    articles: List[NewsArticleInput],
    background_tasks: BackgroundTasks
):
    """Ingest new news articles and process them."""
    try:
        # Convert to dict format
        articles_dict = []
        for i, article in enumerate(articles):
            articles_dict.append({
                'id': f"NEW_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
                'title': article.title,
                'content': article.content,
                'source': article.source,
                'published_at': article.published_at or datetime.utcnow().isoformat(),
                'url': article.url
            })
        
        # Process articles in background
        background_tasks.add_task(process_articles_background, articles_dict)
        
        return {
            "message": f"Processing {len(articles_dict)} articles",
            "status": "queued"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/query")
async def query_news(q: str) -> QueryResponse:
    """Query news with natural language."""
    try:
        # Get all processed articles from database
        with get_db() as db:
            articles = db.query(NewsArticle).filter(
                NewsArticle.is_duplicate == 0
            ).all()
            
            # Get stock impacts
            stock_impacts_db = {}
            for article in articles:
                impacts = db.query(StockImpact).filter(
                    StockImpact.article_id == article.id
                ).all()
                stock_impacts_db[article.article_id] = [
                    {
                        'symbol': imp.symbol,
                        'confidence': imp.confidence,
                        'impact_type': imp.impact_type
                    }
                    for imp in impacts
                ]
            
            # Convert to dict format
            articles_dict = [
                {
                    'id': article.article_id,
                    'title': article.title,
                    'content': article.content,
                    'source': article.source,
                    'published_at': article.published_at.isoformat() if article.published_at else None
                }
                for article in articles
            ]
        
        # Fallback to mock data if database is empty
        if not articles_dict:
            try:
                with open("data/mock_news.json", "r") as f:
                    articles_dict = json.load(f)
                
                # Process articles to get stock impacts
                result_processed = orchestrator.process_articles(articles_dict)
                stock_impacts_db = result_processed.get('stock_impacts', {})
            except Exception:
                pass  # If mock data fails, continue with empty list
        
        # Process query
        result = query_service.process_query(q, articles_dict, stock_impacts_db)
        
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/news/{news_id}")
async def get_news(news_id: str):
    """Get specific news article with entities and impacts."""
    try:
        with get_db() as db:
            article = db.query(NewsArticle).filter(
                NewsArticle.article_id == news_id
            ).first()
            
            if article:
                # Get entities
                entities = db.query(Entity).filter(
                    Entity.article_id == article.id
                ).all()
                
                # Get stock impacts
                impacts = db.query(StockImpact).filter(
                    StockImpact.article_id == article.id
                ).all()
                
                return {
                    'id': article.article_id,
                    'title': article.title,
                    'content': article.content,
                    'source': article.source,
                    'published_at': article.published_at.isoformat() if article.published_at else None,
                    'entities': [
                        {
                            'type': e.entity_type,
                            'name': e.entity_name,
                            'confidence': e.confidence
                        }
                        for e in entities
                    ],
                    'stock_impacts': [
                        {
                            'symbol': i.symbol,
                            'confidence': i.confidence,
                            'impact_type': i.impact_type,
                            'reasoning': i.reasoning
                        }
                        for i in impacts
                    ]
                }
        
        # Fallback to mock data
        try:
            with open("data/mock_news.json", "r") as f:
                articles = json.load(f)
            
            article = next((a for a in articles if a['id'] == news_id), None)
            if not article:
                raise HTTPException(status_code=404, detail="Article not found")
            
            # Process article to get entities and impacts
            result = orchestrator.process_articles([article])
            entities_data = result.get('extracted_entities', {}).get(news_id, {})
            impacts_data = result.get('stock_impacts', {}).get(news_id, [])
            
            # Format entities
            entities_list = []
            for entity_type, entity_list in entities_data.items():
                for entity in entity_list:
                    entities_list.append({
                        'type': entity_type,
                        'name': entity.get('name', ''),
                        'confidence': entity.get('confidence', 1.0)
                    })
            
            # Format impacts
            impacts_list = [
                {
                    'symbol': imp.get('symbol', ''),
                    'confidence': imp.get('confidence', 0.0),
                    'impact_type': imp.get('impact_type', ''),
                    'reasoning': imp.get('reasoning', '')
                }
                for imp in impacts_data
            ]
            
            return {
                'id': article['id'],
                'title': article.get('title', ''),
                'content': article.get('content', ''),
                'source': article.get('source'),
                'published_at': article.get('published_at'),
                'entities': entities_list,
                'stock_impacts': impacts_list
            }
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Article not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/entities")
async def get_entities():
    """Get all extracted entities."""
    try:
        with get_db() as db:
            entities = db.query(Entity).all()
            
            grouped = {}
            for e in entities:
                if e.entity_type not in grouped:
                    grouped[e.entity_type] = []
                grouped[e.entity_type].append({
                    'name': e.entity_name,
                    'confidence': e.confidence
                })
            
            return grouped
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/deduplication-demo")
async def deduplication_demo():
    """Demo endpoint showing duplicate detection."""
    try:
        import json
        # Load mock data
        with open("data/mock_news.json", "r") as f:
            articles = json.load(f)
        
        # Process through orchestrator
        result = orchestrator.process_articles(articles)
        
        # Find the RBI rate hike duplicates (N2, N5, N6, N9)
        rbi_articles = [a for a in articles if a['id'] in ['N2', 'N5', 'N6', 'N9']]
        
        duplicates_info = []
        for unique_id, duplicate_ids in result.get('duplicates', {}).items():
            if len(duplicate_ids) > 1:  # Has duplicates
                story_data = result.get('unique_stories', {}).get(unique_id, {})
                duplicates_info.append({
                    'unique_story_id': unique_id,
                    'duplicate_ids': duplicate_ids,
                    'consolidated_title': story_data.get('consolidated_title', ''),
                    'articles': [a for a in articles if a['id'] in duplicate_ids]
                })
        
        return {
            'total_articles': len(articles),
            'unique_stories': len(result.get('unique_stories', {})),
            'duplicate_groups': len([d for d in duplicates_info if len(d['duplicate_ids']) > 1]),
            'rbi_rate_hike_example': {
                'articles': rbi_articles,
                'explanation': 'These 4 articles (N2, N5, N6, N9) all describe the same RBI rate hike event with different wording. They are identified as duplicates using semantic similarity.'
            },
            'all_duplicate_groups': duplicates_info[:5]  # Show first 5
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stocks/{symbol}/news")
async def get_stock_news(symbol: str):
    """Get news for a specific stock."""
    try:
        with get_db() as db:
            # Find articles with this stock impact
            impacts = db.query(StockImpact).filter(
                StockImpact.symbol == symbol.upper()
            ).all()
            
            if impacts:
                article_ids = [imp.article_id for imp in impacts]
                articles = db.query(NewsArticle).filter(
                    NewsArticle.id.in_(article_ids),
                    NewsArticle.is_duplicate == 0
                ).all()
                
                result = []
                for article in articles:
                    # Get impact for this stock
                    impact = next(
                        (i for i in impacts if i.article_id == article.id),
                        None
                    )
                    
                    result.append({
                        'id': article.article_id,
                        'title': article.title,
                        'content': article.content,
                        'source': article.source,
                        'published_at': article.published_at.isoformat() if article.published_at else None,
                        'impact': {
                            'confidence': impact.confidence if impact else None,
                            'impact_type': impact.impact_type if impact else None,
                            'reasoning': impact.reasoning if impact else None
                        }
                    })
                
                return {
                    'symbol': symbol.upper(),
                    'articles': result,
                    'count': len(result)
                }
        
        # Fallback to mock data
        try:
            with open("data/mock_news.json", "r") as f:
                articles = json.load(f)
            
            # Process all articles to get stock impacts
            result_processed = orchestrator.process_articles(articles)
            stock_impacts_db = result_processed.get('stock_impacts', {})
            
            # Find articles with this stock symbol
            result = []
            for article in articles:
                impacts = stock_impacts_db.get(article['id'], [])
                stock_impact = next((imp for imp in impacts if imp.get('symbol') == symbol.upper()), None)
                
                if stock_impact:
                    result.append({
                        'id': article['id'],
                        'title': article.get('title', ''),
                        'content': article.get('content', ''),
                        'source': article.get('source'),
                        'published_at': article.get('published_at'),
                        'impact': {
                            'confidence': stock_impact.get('confidence', 0.0),
                            'impact_type': stock_impact.get('impact_type', ''),
                            'reasoning': stock_impact.get('reasoning', '')
                        }
                    })
            
            return {
                'symbol': symbol.upper(),
                'articles': result,
                'count': len(result)
            }
        except FileNotFoundError:
            return {
                'symbol': symbol.upper(),
                'articles': [],
                'count': 0
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def process_articles_background(articles: List[Dict]):
    """Background task to process articles."""
    try:
        # Process through orchestrator
        result = orchestrator.process_articles(articles)
        
        # Save to database
        with get_db() as db:
            # Save unique stories
            for story_id, story_data in result.get('unique_stories', {}).items():
                # Check if story already exists
                existing = db.query(UniqueStory).filter(
                    UniqueStory.story_id == story_id
                ).first()
                
                if not existing:
                    story = UniqueStory(
                        story_id=story_id,
                        consolidated_title=story_data.get('consolidated_title', ''),
                        consolidated_content=story_data.get('consolidated_content', ''),
                        article_ids=story_data.get('article_ids', [])
                    )
                    db.add(story)
            
            # Save articles
            for article in articles:
                # Check if duplicate
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
                    published_at=datetime.fromisoformat(article.get('published_at', datetime.utcnow().isoformat())),
                    url=article.get('url'),
                    is_duplicate=is_duplicate,
                    duplicate_of=duplicate_of
                )
                db.add(news_article)
                db.flush()
                
                # Save entities
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
    except Exception as e:
        print(f"Error processing articles: {e}")
        import traceback
        traceback.print_exc()

