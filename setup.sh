#!/bin/bash

# Setup script for Financial News Intelligence System

echo "Setting up Financial News Intelligence System..."
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Initialize database
echo "Initializing database..."
python -m src.database.init_db

echo ""
echo "Setup complete!"
echo ""
echo "To run the system:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run API server: python main.py"
echo "  3. Or run demo: python demo.py"
echo ""

