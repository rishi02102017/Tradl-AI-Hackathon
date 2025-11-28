"""Main orchestrator for multi-agent system using LangGraph."""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from src.agents.deduplication_agent import DeduplicationAgent
from src.agents.entity_extraction_agent import EntityExtractionAgent
from src.agents.impact_mapping_agent import ImpactMappingAgent
import logging

logger = logging.getLogger(__name__)


class ProcessingState(TypedDict):
    """Global state for the multi-agent system."""
    articles: list
    unique_stories: dict
    duplicates: dict
    extracted_entities: dict
    stock_impacts: dict
    processed_articles: list


class NewsProcessingOrchestrator:
    """Main orchestrator that coordinates all agents."""
    
    def __init__(self):
        self.dedup_agent = DeduplicationAgent()
        self.entity_agent = EntityExtractionAgent()
        self.impact_agent = ImpactMappingAgent()
    
    def deduplicate(self, state: ProcessingState) -> ProcessingState:
        """Run deduplication agent."""
        dedup_state = {
            'articles': state.get('articles', [])
        }
        result = self.dedup_agent.identify_duplicates(dedup_state)
        
        return {
            **state,
            'unique_stories': result.get('unique_stories', {}),
            'duplicates': result.get('duplicates', {})
        }
    
    def extract_entities(self, state: ProcessingState) -> ProcessingState:
        """Run entity extraction agent."""
        # Use unique stories if available, otherwise use all articles
        articles = state.get('articles', [])
        unique_stories = state.get('unique_stories', {})
        
        # Process unique stories
        if unique_stories:
            story_articles = []
            for story_id, story_data in unique_stories.items():
                # Create article representation from consolidated story
                story_articles.append({
                    'id': story_id,
                    'title': story_data.get('consolidated_title', ''),
                    'content': story_data.get('consolidated_content', '')
                })
            articles_to_process = story_articles
        else:
            articles_to_process = articles
        
        entity_state = {
            'articles': articles_to_process
        }
        result = self.entity_agent.extract_entities(entity_state)
        
        return {
            **state,
            'extracted_entities': result.get('extracted_entities', {})
        }
    
    def map_impacts(self, state: ProcessingState) -> ProcessingState:
        """Run impact mapping agent."""
        articles = state.get('articles', [])
        unique_stories = state.get('unique_stories', {})
        extracted_entities = state.get('extracted_entities', {})
        
        # Use unique stories if available
        if unique_stories:
            story_articles = []
            for story_id, story_data in unique_stories.items():
                story_articles.append({
                    'id': story_id,
                    'title': story_data.get('consolidated_title', ''),
                    'content': story_data.get('consolidated_content', '')
                })
            articles_to_process = story_articles
        else:
            articles_to_process = articles
        
        impact_state = {
            'articles': articles_to_process,
            'extracted_entities': extracted_entities
        }
        result = self.impact_agent.map_impacts(impact_state)
        
        return {
            **state,
            'stock_impacts': result.get('stock_impacts', {})
        }
    
    def build_graph(self) -> StateGraph:
        """Build the main LangGraph workflow."""
        workflow = StateGraph(ProcessingState)
        
        # Add nodes
        workflow.add_node("deduplicate", self.deduplicate)
        workflow.add_node("extract_entities", self.extract_entities)
        workflow.add_node("map_impacts", self.map_impacts)
        
        # Define workflow
        workflow.set_entry_point("deduplicate")
        workflow.add_edge("deduplicate", "extract_entities")
        workflow.add_edge("extract_entities", "map_impacts")
        workflow.add_edge("map_impacts", END)
        
        return workflow.compile()
    
    def process_articles(self, articles: list) -> dict:
        """Process articles through the entire pipeline."""
        initial_state = {
            'articles': articles,
            'unique_stories': {},
            'duplicates': {},
            'extracted_entities': {},
            'stock_impacts': {},
            'processed_articles': []
        }
        
        graph = self.build_graph()
        result = graph.invoke(initial_state)
        
        return result

