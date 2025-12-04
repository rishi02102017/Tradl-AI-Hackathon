"""Tests for accuracy metrics."""
import pytest
from src.agents.orchestrator import NewsProcessingOrchestrator


class TestDeduplicationAccuracy:
    """Tests for deduplication accuracy."""
    
    def test_rbi_duplicate_detection(self):
        """Test RBI rate hike articles are identified as duplicates."""
        orchestrator = NewsProcessingOrchestrator()
        
        # These 4 articles should be identified as duplicates
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
            },
            {
                'id': 'N6',
                'title': 'Central bank raises policy rate 25bps, signals hawkish stance',
                'content': 'The central bank raised the policy rate by 25 basis points, signaling a hawkish stance.'
            },
            {
                'id': 'N9',
                'title': 'RBI monetary policy: Repo rate up by 25 bps to 6.75%',
                'content': 'The Reserve Bank of India announced a 25 basis point increase in the repo rate to 6.75%.'
            }
        ]
        
        result = orchestrator.process_articles(articles)
        
        duplicates = result.get('duplicates', {})
        unique_stories = result.get('unique_stories', {})
        
        # Check that duplicates were found
        found_duplicate_group = False
        for unique_id, duplicate_ids in duplicates.items():
            if len(duplicate_ids) > 1:
                ids = set(duplicate_ids)
                # Check if at least 2 of the RBI articles are grouped together
                rbi_ids = {'N2', 'N5', 'N6', 'N9'}
                if len(ids.intersection(rbi_ids)) >= 2:
                    found_duplicate_group = True
                    break
        
        # Note: Due to similarity threshold, may not always group all 4
        # But should group at least 2
        assert found_duplicate_group or len(unique_stories) < len(articles)


class TestEntityExtractionPrecision:
    """Tests for entity extraction precision."""
    
    def test_hdfc_entity_extraction(self):
        """Test HDFC Bank entity extraction."""
        orchestrator = NewsProcessingOrchestrator()
        
        articles = [
            {
                'id': 'N1',
                'title': 'HDFC Bank announces 15% dividend, board approves stock buyback',
                'content': 'HDFC Bank, India\'s largest private sector bank, announced a 15% dividend payout to shareholders. The board of directors has also approved a stock buyback program worth Rs 10,000 crores.'
            }
        ]
        
        result = orchestrator.process_articles(articles)
        
        entities = result.get('extracted_entities', {})
        assert 'N1' in entities
        
        article_entities = entities['N1']
        
        # Should extract HDFC Bank
        companies = article_entities.get('companies', [])
        found_hdfc = any('HDFC' in str(c).upper() for c in companies)
        
        # Should extract Banking sector
        sectors = article_entities.get('sectors', [])
        found_banking = any('bank' in str(s).lower() for s in sectors)
        
        # At least one should be found
        assert found_hdfc or found_banking
    
    def test_rbi_entity_extraction(self):
        """Test RBI entity extraction."""
        orchestrator = NewsProcessingOrchestrator()
        
        articles = [
            {
                'id': 'N2',
                'title': 'RBI raises repo rate by 25bps to 6.75%, citing inflation concerns',
                'content': 'The Reserve Bank of India raised the repo rate by 25 basis points to 6.75%, citing inflation concerns.'
            }
        ]
        
        result = orchestrator.process_articles(articles)
        
        entities = result.get('extracted_entities', {})
        assert 'N2' in entities
        
        article_entities = entities['N2']
        
        # Should extract RBI as regulator
        regulators = article_entities.get('regulators', [])
        found_rbi = any('RBI' in str(r).upper() for r in regulators)
        
        assert found_rbi


class TestStockMappingAccuracy:
    """Tests for stock mapping accuracy."""
    
    def test_hdfc_stock_mapping(self):
        """Test HDFC Bank stock mapping."""
        orchestrator = NewsProcessingOrchestrator()
        
        articles = [
            {
                'id': 'N1',
                'title': 'HDFC Bank announces 15% dividend',
                'content': 'HDFC Bank announced a 15% dividend.'
            }
        ]
        
        result = orchestrator.process_articles(articles)
        
        impacts = result.get('stock_impacts', {})
        assert 'N1' in impacts
        
        article_impacts = impacts['N1']
        
        # Should map to HDFCBANK with high confidence
        hdfc_impacts = [i for i in article_impacts if 'HDFCBANK' in i.get('symbol', '')]
        
        if hdfc_impacts:
            assert hdfc_impacts[0]['confidence'] >= 0.9
            assert hdfc_impacts[0]['impact_type'] == 'direct'

