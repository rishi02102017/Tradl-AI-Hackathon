"""Vercel serverless function entry point for FastAPI."""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import and initialize database
from src.database.init_db import init_database
init_database()

# Import FastAPI app
from src.api.main import app

# Export for Vercel
handler = app
