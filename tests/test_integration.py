"""Integration tests for end-to-end workflow."""
import pytest
from src.agents.orchestrator import NewsProcessingOrchestrator


class TestEndToEndWorkflow:
    """Integration tests for complete processing pipeline."""
    
    def test_full_pipeline_rbi_example(self):
        """Test complete pipeline with RBI rate hike example."""
        orchestrator = NewsProcessingOrchestrator()
        
        articles = [
            {
                'id': 'N2',
                'title': 'RBI increases repo rate by 25 basis points to combat inflation',
                'content': 'The Reserve Bank of India has increased the repo rate by 25 basis points to combat rising inflation.'
            },
            {
                'id': 'N5',
                'title': 'Reserve Bank hikes interest rates by 0.25% in surprise move',
                'content': 'The Reserve Bank of India hiked interest rates by 0.25% in a surprise move.'
            }
        ]
        
        result = orchestrator.process_articles(articles)
        
        assert 'unique_stories' in result
        assert 'extracted_entities' in result
        assert 'stock_impacts' in result
        assert 'duplicates' in result
    
    def test_full_pipeline_hdfc_example(self):
        """Test complete pipeline with HDFC Bank example."""
        orchestrator = NewsProcessingOrchestrator()
        
        articles = [
            {
                'id': 'N1',
                'title': 'HDFC Bank announces 15% dividend, board approves stock buyback',
                'content': 'HDFC Bank, India\'s largest private sector bank, announced a 15% dividend payout to shareholders. The board of directors has also approved a stock buyback program worth Rs 10,000 crores.'
            }
        ]
        
        result = orchestrator.process_articles(articles)
        
        assert 'unique_stories' in result
        assert 'extracted_entities' in result
        assert 'stock_impacts' in result
        
        # Check entities extracted
        entities = result.get('extracted_entities', {})
        assert 'N1' in entities
        
        # Check stock impacts
        impacts = result.get('stock_impacts', {})
        assert 'N1' in impacts
        assert len(impacts['N1']) > 0
    
    def test_pipeline_with_multiple_articles(self):
        """Test pipeline with multiple diverse articles."""
        orchestrator = NewsProcessingOrchestrator()
        
        articles = [
            {
                'id': 'A1',
                'title': 'HDFC Bank dividend',
                'content': 'HDFC Bank announced dividend.'
            },
            {
                'id': 'A2',
                'title': 'ICICI Bank expansion',
                'content': 'ICICI Bank opens new branches.'
            },
            {
                'id': 'A3',
                'title': 'RBI rate hike',
                'content': 'RBI increased repo rate.'
            }
        ]
        
        result = orchestrator.process_articles(articles)
        
        assert 'unique_stories' in result
        assert 'extracted_entities' in result
        assert 'stock_impacts' in result
        
        # Should process all articles
        entities = result.get('extracted_entities', {})
        assert len(entities) > 0
    
    def test_pipeline_state_management(self):
        """Test state is properly managed through pipeline."""
        orchestrator = NewsProcessingOrchestrator()
        
        articles = [
            {
                'id': 'T1',
                'title': 'Test Article',
                'content': 'This is a test article about banking.'
            }
        ]
        
        result = orchestrator.process_articles(articles)
        
        # Check state progression
        assert 'articles' in result or len(result) > 0
        assert 'extracted_entities' in result
        assert 'stock_impacts' in result

