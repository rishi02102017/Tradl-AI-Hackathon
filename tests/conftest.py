"""Pytest configuration and fixtures."""
import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_articles():
    """Sample articles for testing."""
    return [
        {
            'id': 'N1',
            'title': 'HDFC Bank announces 15% dividend, board approves stock buyback',
            'content': 'HDFC Bank, India\'s largest private sector bank, announced a 15% dividend payout to shareholders.'
        },
        {
            'id': 'N2',
            'title': 'RBI increases repo rate by 25 basis points to combat inflation',
            'content': 'The Reserve Bank of India has increased the repo rate by 25 basis points to combat rising inflation.'
        }
    ]


@pytest.fixture
def rbi_duplicate_articles():
    """RBI rate hike articles that should be identified as duplicates."""
    return [
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
        }
    ]

