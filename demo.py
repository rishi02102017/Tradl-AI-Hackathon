"""Demo CLI interface for the Financial News Intelligence System."""
import json
import sys
from src.agents.orchestrator import NewsProcessingOrchestrator
from src.services.query_service import QueryService
from src.database.init_db import init_database
from src.database.db_session import get_db
from src.database.models import NewsArticle, Entity, StockImpact
from src.services.ingestion_service import NewsIngestionService
from datetime import datetime


def load_mock_data():
    """Load mock news data."""
    with open("data/mock_news.json", "r") as f:
        return json.load(f)


def print_separator():
    """Print a separator line."""
    print("\n" + "="*80 + "\n")


def demo_deduplication():
    """Demo deduplication functionality."""
    print_separator()
    print("DEMO 1: Intelligent Deduplication")
    print_separator()
    
    articles = load_mock_data()
    
    # Show example duplicates
    print("Example articles that should be identified as duplicates:")
    print("\nArticle N2: 'RBI raises repo rate by 25bps to 6.75%, citing inflation concerns'")
    print("Article N5: 'Reserve Bank hikes interest rates by 0.25% in surprise move'")
    print("Article N6: 'Central bank raises policy rate 25bps, signals hawkish stance'")
    print("Article N9: 'RBI increases repo rate by 25 basis points to combat inflation'")
    
    orchestrator = NewsProcessingOrchestrator()
    result = orchestrator.process_articles(articles)
    
    print("\n\nDeduplication Results:")
    print(f"Total articles processed: {len(articles)}")
    print(f"Unique stories identified: {len(result.get('unique_stories', {}))}")
    
    print("\nDuplicate Groups Found:")
    for unique_id, duplicate_ids in list(result.get('duplicates', {}).items())[:5]:
        print(f"\n  Unique Story: {unique_id}")
        print(f"  Duplicates: {', '.join(duplicate_ids)}")
        if unique_id in result.get('unique_stories', {}):
            story = result['unique_stories'][unique_id]
            print(f"  Consolidated Title: {story.get('consolidated_title', '')[:80]}...")


def demo_entity_extraction():
    """Demo entity extraction."""
    print_separator()
    print("DEMO 2: Entity Extraction & Impact Mapping")
    print_separator()
    
    articles = load_mock_data()
    
    # Process a sample article
    sample_article = articles[0]  # HDFC Bank article
    print(f"Sample Article: {sample_article['title']}")
    print(f"Content: {sample_article['content'][:200]}...")
    
    orchestrator = NewsProcessingOrchestrator()
    result = orchestrator.process_articles([sample_article])
    
    entities = result.get('extracted_entities', {}).get(sample_article['id'], {})
    impacts = result.get('stock_impacts', {}).get(sample_article['id'], [])
    
    print("\n\nExtracted Entities:")
    for entity_type, entity_list in entities.items():
        if entity_list:
            print(f"\n  {entity_type.upper()}:")
            for entity in entity_list[:5]:
                print(f"    - {entity.get('name')} (confidence: {entity.get('confidence', 0):.2f})")
    
    print("\n\nStock Impacts:")
    for impact in impacts[:5]:
        print(f"  - {impact.get('symbol')}: {impact.get('confidence', 0):.2f} ({impact.get('impact_type')})")
        print(f"    Reasoning: {impact.get('reasoning', '')}")


def demo_query_system():
    """Demo context-aware query system."""
    print_separator()
    print("DEMO 3: Context-Aware Query System")
    print_separator()
    
    articles = load_mock_data()
    
    # Process all articles
    orchestrator = NewsProcessingOrchestrator()
    result = orchestrator.process_articles(articles)
    
    # Build stock impacts mapping
    stock_impacts_db = result.get('stock_impacts', {})
    
    query_service = QueryService()
    
    # Test queries
    test_queries = [
        "HDFC Bank news",
        "Banking sector update",
        "RBI policy changes",
        "Interest rate impact"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 80)
        
        query_result = query_service.process_query(
            query,
            articles,
            stock_impacts_db
        )
        
        print(f"Query Intent: {query_result['query_intent']}")
        print(f"Found {query_result['count']} relevant articles")
        
        if query_result.get('extracted_entities'):
            print("\nExtracted Entities from Query:")
            for entity_type, entity_list in query_result['extracted_entities'].items():
                if entity_list:
                    print(f"  {entity_type}: {[e['name'] for e in entity_list]}")
        
        print("\nRelevant Articles:")
        for article in query_result['relevant_articles'][:3]:
            print(f"  - {article.get('title', '')[:70]}...")


def demo_full_pipeline():
    """Demo the full processing pipeline."""
    print_separator()
    print("DEMO 4: Full Processing Pipeline")
    print_separator()
    
    # Initialize database
    init_database()
    
    # Load and process articles
    articles = load_mock_data()
    print(f"Loading {len(articles)} articles from mock data...")
    
    orchestrator = NewsProcessingOrchestrator()
    result = orchestrator.process_articles(articles)
    
    print(f"\nProcessing complete!")
    print(f"  - Unique stories: {len(result.get('unique_stories', {}))}")
    print(f"  - Total entities extracted: {sum(len(e) for e in result.get('extracted_entities', {}).values())}")
    print(f"  - Total stock impacts: {sum(len(i) for i in result.get('stock_impacts', {}).values())}")
    
    # Save to database
    print("\nSaving to database...")
    try:
        with get_db() as db:
            # Save articles (simplified version)
            for article in articles[:5]:  # Save first 5 for demo
                news_article = NewsArticle(
                    article_id=article['id'],
                    title=article.get('title', ''),
                    content=article.get('content', ''),
                    source=article.get('source'),
                    published_at=datetime.fromisoformat(article.get('published_at', datetime.utcnow().isoformat())),
                    url=article.get('url'),
                    is_duplicate=0
                )
                db.add(news_article)
            
            print("Articles saved to database!")
    except Exception as e:
        print(f"Error saving to database: {e}")


def interactive_query():
    """Interactive query interface."""
    print_separator()
    print("INTERACTIVE QUERY MODE")
    print("Type 'exit' to quit")
    print_separator()
    
    articles = load_mock_data()
    orchestrator = NewsProcessingOrchestrator()
    result = orchestrator.process_articles(articles)
    stock_impacts_db = result.get('stock_impacts', {})
    
    query_service = QueryService()
    
    while True:
        query = input("\nEnter your query: ").strip()
        
        if query.lower() in ['exit', 'quit', 'q']:
            break
        
        if not query:
            continue
        
        try:
            query_result = query_service.process_query(query, articles, stock_impacts_db)
            
            print(f"\nFound {query_result['count']} relevant articles")
            print(f"Query Intent: {query_result['query_intent']}")
            
            for i, article in enumerate(query_result['relevant_articles'][:5], 1):
                print(f"\n{i}. {article.get('title', '')}")
                print(f"   {article.get('content', '')[:100]}...")
        
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main demo menu."""
    print("\n" + "="*80)
    print("AI-Powered Financial News Intelligence System - Demo")
    print("="*80)
    
    menu = """
    Select a demo:
    1. Deduplication Demo
    2. Entity Extraction Demo
    3. Query System Demo
    4. Full Pipeline Demo
    5. Interactive Query Mode
    6. Run All Demos
    0. Exit
    
    Enter choice: """
    
    while True:
        choice = input(menu).strip()
        
        if choice == '0':
            print("Goodbye!")
            break
        elif choice == '1':
            demo_deduplication()
        elif choice == '2':
            demo_entity_extraction()
        elif choice == '3':
            demo_query_system()
        elif choice == '4':
            demo_full_pipeline()
        elif choice == '5':
            interactive_query()
        elif choice == '6':
            demo_deduplication()
            demo_entity_extraction()
            demo_query_system()
            demo_full_pipeline()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

