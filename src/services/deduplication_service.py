"""Deduplication service for identifying duplicate news articles."""
from typing import List, Dict, Tuple
from src.utils.embeddings import compute_similarity
import logging

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.85  # 85% similarity threshold for duplicates


class DeduplicationService:
    """Service for identifying and consolidating duplicate news articles."""
    
    def __init__(self, similarity_threshold: float = SIMILARITY_THRESHOLD):
        self.similarity_threshold = similarity_threshold
    
    def identify_duplicates(
        self,
        articles: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        Identify duplicate articles based on semantic similarity.
        
        Returns:
            Dict mapping unique article IDs to lists of duplicate article IDs
        """
        unique_stories = {}
        processed = set()
        
        for i, article1 in enumerate(articles):
            if article1['id'] in processed:
                continue
            
            # Create a combined text for comparison
            text1 = f"{article1.get('title', '')} {article1.get('content', '')}"
            
            duplicates = [article1['id']]
            
            for j, article2 in enumerate(articles[i+1:], start=i+1):
                if article2['id'] in processed:
                    continue
                
                text2 = f"{article2.get('title', '')} {article2.get('content', '')}"
                
                # Compute similarity
                similarity = compute_similarity(text1, text2)
                
                if similarity >= self.similarity_threshold:
                    duplicates.append(article2['id'])
                    processed.add(article2['id'])
                    logger.info(
                        f"Found duplicate: {article1['id']} <-> {article2['id']} "
                        f"(similarity: {similarity:.3f})"
                    )
            
            if len(duplicates) > 0:
                unique_stories[article1['id']] = duplicates
                processed.add(article1['id'])
        
        return unique_stories
    
    def consolidate_story(
        self,
        article_ids: List[str],
        articles: List[Dict]
    ) -> Dict:
        """
        Consolidate multiple duplicate articles into a single story.
        
        Args:
            article_ids: List of article IDs to consolidate
            articles: List of all articles
            
        Returns:
            Consolidated story dictionary
        """
        article_dict = {a['id']: a for a in articles}
        story_articles = [article_dict[aid] for aid in article_ids if aid in article_dict]
        
        if not story_articles:
            return None
        
        # Use the first article as base, but combine information
        base_article = story_articles[0]
        
        # Combine titles (use the most detailed one)
        titles = [a.get('title', '') for a in story_articles]
        consolidated_title = max(titles, key=len)
        
        # Combine content (use the longest one)
        contents = [a.get('content', '') for a in story_articles]
        consolidated_content = max(contents, key=len)
        
        # Combine sources
        sources = list(set([a.get('source', '') for a in story_articles if a.get('source')]))
        
        # Use earliest publication date
        published_dates = [a.get('published_at') for a in story_articles if a.get('published_at')]
        earliest_date = min(published_dates) if published_dates else None
        
        return {
            'story_id': f"STORY_{base_article['id']}",
            'consolidated_title': consolidated_title,
            'consolidated_content': consolidated_content,
            'article_ids': article_ids,
            'sources': sources,
            'published_at': earliest_date,
            'url': base_article.get('url')
        }

