"""Entity extraction agent using LangGraph."""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from src.services.entity_extraction_service import EntityExtractionService
import logging

logger = logging.getLogger(__name__)


class EntityExtractionState(TypedDict):
    """State for entity extraction agent."""
    articles: list
    extracted_entities: dict  # article_id -> entities


class EntityExtractionAgent:
    """Agent responsible for extracting entities from articles."""
    
    def __init__(self):
        self.service = EntityExtractionService()
    
    def extract_entities(self, state: EntityExtractionState) -> EntityExtractionState:
        """Extract entities from articles."""
        articles = state.get('articles', [])
        extracted_entities = {}
        
        logger.info(f"Entity extraction agent processing {len(articles)} articles")
        
        for article in articles:
            title = article.get('title', '')
            content = article.get('content', '')
            
            entities = self.service.extract_entities(content, title)
            extracted_entities[article['id']] = entities
        
        return {
            'articles': articles,
            'extracted_entities': extracted_entities
        }
    
    def build_graph(self) -> StateGraph:
        """Build the LangGraph for entity extraction."""
        workflow = StateGraph(EntityExtractionState)
        
        workflow.add_node("extract_entities", self.extract_entities)
        
        workflow.set_entry_point("extract_entities")
        workflow.add_edge("extract_entities", END)
        
        return workflow.compile()

