"""Database models for financial news storage."""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class NewsArticle(Base):
    """Model for storing news articles."""
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String)
    published_at = Column(DateTime, nullable=False)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Deduplication fields
    is_duplicate = Column(Integer, default=0)  # 0 = unique, 1 = duplicate
    duplicate_of = Column(Integer, ForeignKey('news_articles.id'), nullable=True)
    similarity_score = Column(Float, nullable=True)
    
    # Relationships
    entities = relationship("Entity", back_populates="article")
    stock_impacts = relationship("StockImpact", back_populates="article")
    duplicates = relationship("NewsArticle", remote_side=[id])


class Entity(Base):
    """Model for storing extracted entities."""
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('news_articles.id'), nullable=False)
    entity_type = Column(String, nullable=False)  # Company, Sector, Regulator, Person, Event
    entity_name = Column(String, nullable=False)
    confidence = Column(Float, default=1.0)
    entity_metadata = Column(JSON)  # Additional entity information
    
    # Relationships
    article = relationship("NewsArticle", back_populates="entities")


class StockImpact(Base):
    """Model for storing stock impact mappings."""
    __tablename__ = "stock_impacts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('news_articles.id'), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    impact_type = Column(String, nullable=False)  # direct, sector, regulatory
    reasoning = Column(Text)
    
    # Relationships
    article = relationship("NewsArticle", back_populates="stock_impacts")


class UniqueStory(Base):
    """Model for storing consolidated unique stories."""
    __tablename__ = "unique_stories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(String, unique=True, nullable=False)
    consolidated_title = Column(String, nullable=False)
    consolidated_content = Column(Text, nullable=False)
    article_ids = Column(JSON, nullable=False)  # List of article IDs in this story
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    entities = relationship("StoryEntity", back_populates="story")
    stock_impacts = relationship("StoryStockImpact", back_populates="story")


class StoryEntity(Base):
    """Model for entities in unique stories."""
    __tablename__ = "story_entities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(Integer, ForeignKey('unique_stories.id'), nullable=False)
    entity_type = Column(String, nullable=False)
    entity_name = Column(String, nullable=False)
    confidence = Column(Float, default=1.0)
    
    story = relationship("UniqueStory", back_populates="entities")


class StoryStockImpact(Base):
    """Model for stock impacts in unique stories."""
    __tablename__ = "story_stock_impacts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(Integer, ForeignKey('unique_stories.id'), nullable=False)
    symbol = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    impact_type = Column(String, nullable=False)
    
    story = relationship("UniqueStory", back_populates="stock_impacts")

