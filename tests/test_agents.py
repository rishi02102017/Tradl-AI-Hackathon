"""Unit tests for LangGraph agents."""
import pytest
from src.agents.deduplication_agent import DeduplicationAgent, DeduplicationState
from src.agents.entity_extraction_agent import EntityExtractionAgent, EntityExtractionState
from src.agents.impact_mapping_agent import ImpactMappingAgent, ImpactMappingState


class TestDeduplicationAgent:
    """Tests for Deduplication Agent."""
    
    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = DeduplicationAgent()
        assert agent is not None
        assert agent.service is not None
    
    def test_identify_duplicates_rbi_example(self):
        """Test RBI rate hike duplicate detection."""
        agent = DeduplicationAgent()
        
        articles = [
            {
                'id': 'N2',
                'title': 'RBI increases repo rate by 25 basis points to combat inflation',
                'content': 'The Reserve Bank of India has increased the repo rate by 25 basis points.'
            },
            {
                'id': 'N5',
                'title': 'Reserve Bank hikes interest rates by 0.25% in surprise move',
                'content': 'The RBI has hiked interest rates by 0.25% in a surprise move.'
            },
            {
                'id': 'N6',
                'title': 'Central bank raises policy rate 25bps, signals hawkish stance',
                'content': 'The central bank raised the policy rate by 25 basis points.'
            }
        ]
        
        state: DeduplicationState = {
            'articles': articles,
            'unique_stories': {},
            'duplicates': {}
        }
        
        result = agent.identify_duplicates(state)
        
        assert 'unique_stories' in result
        assert 'duplicates' in result
        assert len(result['unique_stories']) > 0
    
    def test_build_graph(self):
        """Test graph construction."""
        agent = DeduplicationAgent()
        graph = agent.build_graph()
        assert graph is not None


class TestEntityExtractionAgent:
    """Tests for Entity Extraction Agent."""
    
    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = EntityExtractionAgent()
        assert agent is not None
        assert agent.service is not None
    
    def test_extract_entities_hdfc_example(self):
        """Test entity extraction from HDFC Bank article."""
        agent = EntityExtractionAgent()
        
        articles = [
            {
                'id': 'N1',
                'title': 'HDFC Bank announces 15% dividend, board approves stock buyback',
                'content': 'HDFC Bank announced a 15% dividend payout. The banking sector shows strong growth.'
            }
        ]
        
        state: EntityExtractionState = {
            'articles': articles,
            'extracted_entities': {}
        }
        
        result = agent.extract_entities(state)
        
        assert 'extracted_entities' in result
        assert 'N1' in result['extracted_entities']
        entities = result['extracted_entities']['N1']
        assert 'companies' in entities or 'sectors' in entities
    
    def test_build_graph(self):
        """Test graph construction."""
        agent = EntityExtractionAgent()
        graph = agent.build_graph()
        assert graph is not None


class TestImpactMappingAgent:
    """Tests for Impact Mapping Agent."""
    
    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = ImpactMappingAgent()
        assert agent is not None
        assert agent.service is not None
    
    def test_map_impacts_hdfc_example(self):
        """Test stock impact mapping for HDFC Bank."""
        agent = ImpactMappingAgent()
        
        articles = [
            {
                'id': 'N1',
                'title': 'HDFC Bank announces 15% dividend',
                'content': 'HDFC Bank announced dividend.'
            }
        ]
        
        extracted_entities = {
            'N1': {
                'companies': ['HDFC Bank'],
                'sectors': ['Banking']
            }
        }
        
        state: ImpactMappingState = {
            'articles': articles,
            'extracted_entities': extracted_entities,
            'stock_impacts': {}
        }
        
        result = agent.map_impacts(state)
        
        assert 'stock_impacts' in result
        assert 'N1' in result['stock_impacts']
        impacts = result['stock_impacts']['N1']
        assert len(impacts) > 0
        # Check for HDFCBANK with high confidence
        hdfc_impact = [i for i in impacts if 'HDFCBANK' in i.get('symbol', '')]
        if hdfc_impact:
            assert hdfc_impact[0]['confidence'] >= 0.9
    
    def test_build_graph(self):
        """Test graph construction."""
        agent = ImpactMappingAgent()
        graph = agent.build_graph()
        assert graph is not None

