"""Query service for context-aware news retrieval."""
from typing import List, Dict, Optional
from src.utils.embeddings import find_similar_articles
from src.services.entity_extraction_service import EntityExtractionService
from src.services.impact_mapping_service import ImpactMappingService
from src.utils.stock_mapper import map_company_to_stock, map_sector_to_stocks
import logging

logger = logging.getLogger(__name__)


class QueryService:
    """Service for context-aware query processing."""
    
    def __init__(self):
        self.entity_extractor = EntityExtractionService()
        self.impact_mapper = ImpactMappingService()
    
    def process_query(
        self,
        query: str,
        news_articles: List[Dict],
        stock_impacts_db: Optional[Dict] = None
    ) -> Dict:
        """
        Process a natural language query and return relevant news.
        
        Args:
            query: Natural language query
            news_articles: List of news articles
            stock_impacts_db: Optional pre-computed stock impacts mapping
            
        Returns:
            Dictionary with relevant news articles and metadata
        """
        # Extract entities from query
        query_entities = self.entity_extractor.extract_entities(query)
        
        # Determine query intent
        query_intent = self._determine_query_intent(query, query_entities)
        
        # Find relevant articles
        relevant_articles = self._find_relevant_articles(
            query,
            query_intent,
            query_entities,
            news_articles,
            stock_impacts_db
        )
        
        return {
            'query': query,
            'query_intent': query_intent,
            'extracted_entities': query_entities,
            'relevant_articles': relevant_articles,
            'count': len(relevant_articles)
        }
    
    def _determine_query_intent(self, query: str, entities: Dict) -> str:
        """Determine the intent of the query."""
        query_lower = query.lower()
        
        # Check for specific patterns
        if any(company['name'].lower() in query_lower for company in entities.get('companies', [])):
            return 'company_specific'
        
        if any(sector['name'].lower() in query_lower for sector in entities.get('sectors', [])):
            return 'sector_wide'
        
        if any(reg['name'].lower() in query_lower for reg in entities.get('regulators', [])):
            return 'regulator_specific'
        
        if 'sector' in query_lower or 'industry' in query_lower:
            return 'sector_wide'
        
        if 'rate' in query_lower or 'interest' in query_lower or 'policy' in query_lower:
            return 'thematic'
        
        return 'general'
    
    def _find_relevant_articles(
        self,
        query: str,
        query_intent: str,
        query_entities: Dict,
        news_articles: List[Dict],
        stock_impacts_db: Optional[Dict] = None
    ) -> List[Dict]:
        """Find relevant articles based on query intent and entities."""
        relevant = []
        
        # Extract target companies/sectors from query
        target_companies = [e['name'] for e in query_entities.get('companies', [])]
        target_sectors = [e['name'] for e in query_entities.get('sectors', [])]
        target_regulators = [e['name'] for e in query_entities.get('regulators', [])]
        
        # Get target stock symbols
        target_stocks = set()
        for company in target_companies:
            stocks = map_company_to_stock(company)
            target_stocks.update([s[0] for s in stocks])
        
        for sector in target_sectors:
            stocks = map_sector_to_stocks(sector)
            target_stocks.update([s[0] for s in stocks])
        
        # Find articles based on intent
        if query_intent == 'company_specific':
            # Direct mentions + sector-wide news
            relevant = self._find_company_articles(
                target_companies,
                target_stocks,
                news_articles,
                stock_impacts_db
            )
        elif query_intent == 'sector_wide':
            # All sector-tagged news
            relevant = self._find_sector_articles(
                target_sectors,
                news_articles,
                stock_impacts_db
            )
        elif query_intent == 'regulator_specific':
            # Regulator-specific filter
            relevant = self._find_regulator_articles(
                target_regulators,
                news_articles
            )
        else:
            # Semantic search for thematic queries
            relevant = self._find_thematic_articles(
                query,
                news_articles
            )
        
        # Remove duplicates and sort by relevance
        seen_ids = set()
        unique_relevant = []
        for article in relevant:
            if article['id'] not in seen_ids:
                seen_ids.add(article['id'])
                unique_relevant.append(article)
        
        return unique_relevant
    
    def _find_company_articles(
        self,
        companies: List[str],
        target_stocks: set,
        news_articles: List[Dict],
        stock_impacts_db: Optional[Dict]
    ) -> List[Dict]:
        """Find articles related to specific companies."""
        relevant = []
        
        for article in news_articles:
            article_text = f"{article.get('title', '')} {article.get('content', '')}"
            
            # Check for direct mentions
            for company in companies:
                if company.lower() in article_text.lower():
                    relevant.append(article)
                    break
            
            # Check stock impacts if available
            if stock_impacts_db and article['id'] in stock_impacts_db:
                article_stocks = {imp['symbol'] for imp in stock_impacts_db[article['id']]}
                if article_stocks.intersection(target_stocks):
                    if article not in relevant:
                        relevant.append(article)
        
        return relevant
    
    def _find_sector_articles(
        self,
        sectors: List[str],
        news_articles: List[Dict],
        stock_impacts_db: Optional[Dict]
    ) -> List[Dict]:
        """Find articles related to sectors."""
        relevant = []
        
        for article in news_articles:
            article_text = f"{article.get('title', '')} {article.get('content', '')}"
            
            # Check for sector mentions
            for sector in sectors:
                if sector.lower() in article_text.lower():
                    relevant.append(article)
                    break
        
        return relevant
    
    def _find_regulator_articles(
        self,
        regulators: List[str],
        news_articles: List[Dict]
    ) -> List[Dict]:
        """Find articles related to regulators."""
        relevant = []
        
        for article in news_articles:
            article_text = f"{article.get('title', '')} {article.get('content', '')}"
            
            for regulator in regulators:
                if regulator.upper() in article_text.upper():
                    relevant.append(article)
                    break
        
        return relevant
    
    def _find_thematic_articles(
        self,
        query: str,
        news_articles: List[Dict]
    ) -> List[Dict]:
        """Find articles using semantic search."""
        article_texts = [
            f"{a.get('title', '')} {a.get('content', '')}"
            for a in news_articles
        ]
        
        similar_indices = find_similar_articles(query, article_texts, threshold=0.7)
        
        return [news_articles[idx] for idx, _ in similar_indices]

