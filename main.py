"""Main entry point for the Financial News Intelligence System."""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Initialize database
    from src.database.init_db import init_database
    init_database()
    
    # Run the API server
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

