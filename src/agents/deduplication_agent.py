"""Deduplication agent using LangGraph."""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from src.services.deduplication_service import DeduplicationService
import logging

logger = logging.getLogger(__name__)


class DeduplicationState(TypedDict):
    """State for deduplication agent."""
    articles: list
    unique_stories: dict
    duplicates: dict


class DeduplicationAgent:
    """Agent responsible for identifying and consolidating duplicate articles."""
    
    def __init__(self):
        self.service = DeduplicationService()
    
    def identify_duplicates(self, state: DeduplicationState) -> DeduplicationState:
        """Identify duplicate articles."""
        articles = state.get('articles', [])
        
        logger.info(f"Deduplication agent processing {len(articles)} articles")
        
        # Identify duplicates
        duplicates = self.service.identify_duplicates(articles)
        
        # Consolidate stories
        unique_stories = {}
        for unique_id, duplicate_ids in duplicates.items():
            consolidated = self.service.consolidate_story(duplicate_ids, articles)
            if consolidated:
                unique_stories[unique_id] = consolidated
        
        return {
            'articles': articles,
            'unique_stories': unique_stories,
            'duplicates': duplicates
        }
    
    def build_graph(self) -> StateGraph:
        """Build the LangGraph for deduplication."""
        workflow = StateGraph(DeduplicationState)
        
        workflow.add_node("identify_duplicates", self.identify_duplicates)
        
        workflow.set_entry_point("identify_duplicates")
        workflow.add_edge("identify_duplicates", END)
        
        return workflow.compile()

