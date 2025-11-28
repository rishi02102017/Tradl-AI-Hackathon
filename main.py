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
    
    # Get port from environment (for deployment) or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Run the API server
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV") != "production"  # Disable reload in production
    )

