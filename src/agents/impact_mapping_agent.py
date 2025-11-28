"""Impact mapping agent using LangGraph."""
from typing import TypedDict
from langgraph.graph import StateGraph, END
from src.services.impact_mapping_service import ImpactMappingService
import logging

logger = logging.getLogger(__name__)


class ImpactMappingState(TypedDict):
    """State for impact mapping agent."""
    articles: list
    extracted_entities: dict
    stock_impacts: dict  # article_id -> stock_impacts


class ImpactMappingAgent:
    """Agent responsible for mapping entities to stock impacts."""
    
    def __init__(self):
        self.service = ImpactMappingService()
    
    def map_impacts(self, state: ImpactMappingState) -> ImpactMappingState:
        """Map entities to stock impacts."""
        articles = state.get('articles', [])
        extracted_entities = state.get('extracted_entities', {})
        stock_impacts = {}
        
        logger.info(f"Impact mapping agent processing {len(articles)} articles")
        
        for article in articles:
            article_id = article['id']
            entities = extracted_entities.get(article_id, {})
            
            impacts = self.service.map_entities_to_stocks(entities)
            stock_impacts[article_id] = impacts
        
        return {
            'articles': articles,
            'extracted_entities': extracted_entities,
            'stock_impacts': stock_impacts
        }
    
    def build_graph(self) -> StateGraph:
        """Build the LangGraph for impact mapping."""
        workflow = StateGraph(ImpactMappingState)
        
        workflow.add_node("map_impacts", self.map_impacts)
        
        workflow.set_entry_point("map_impacts")
        workflow.add_edge("map_impacts", END)
        
        return workflow.compile()

