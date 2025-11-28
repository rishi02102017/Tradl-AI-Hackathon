"""Stock mapping utilities - maps company names to stock symbols."""
import re
from typing import Dict, List, Tuple

# Indian stock market mapping
STOCK_MAP = {
    # Banking Sector
    "HDFC Bank": ("HDFCBANK", 1.0, "direct"),
    "HDFC": ("HDFCBANK", 1.0, "direct"),
    "ICICI Bank": ("ICICIBANK", 1.0, "direct"),
    "ICICI": ("ICICIBANK", 1.0, "direct"),
    "Axis Bank": ("AXISBANK", 1.0, "direct"),
    "Kotak Mahindra Bank": ("KOTAKBANK", 1.0, "direct"),
    "Kotak Bank": ("KOTAKBANK", 1.0, "direct"),
    "State Bank of India": ("SBIN", 1.0, "direct"),
    "SBI": ("SBIN", 1.0, "direct"),
    
    # IT Sector
    "TCS": ("TCS", 1.0, "direct"),
    "Tata Consultancy Services": ("TCS", 1.0, "direct"),
    "Infosys": ("INFY", 1.0, "direct"),
    "Wipro": ("WIPRO", 1.0, "direct"),
    "HCL Technologies": ("HCLTECH", 1.0, "direct"),
    "HCL": ("HCLTECH", 1.0, "direct"),
    
    # Conglomerates
    "Reliance Industries": ("RELIANCE", 1.0, "direct"),
    "Reliance": ("RELIANCE", 1.0, "direct"),
    "RIL": ("RELIANCE", 1.0, "direct"),
    
    # Telecom
    "Bharti Airtel": ("BHARTIARTL", 1.0, "direct"),
    "Airtel": ("BHARTIARTL", 1.0, "direct"),
    "Reliance Jio": ("RELIANCE", 0.8, "sector"),
    "Jio": ("RELIANCE", 0.8, "sector"),
    
    # Automobile
    "Maruti Suzuki": ("MARUTI", 1.0, "direct"),
    "Maruti": ("MARUTI", 1.0, "direct"),
    "Tata Motors": ("TATAMOTORS", 1.0, "direct"),
    
    # Infrastructure
    "L&T": ("LT", 1.0, "direct"),
    "Larsen & Toubro": ("LT", 1.0, "direct"),
    
    # Pharma
    "Sun Pharma": ("SUNPHARMA", 1.0, "direct"),
    "Sun Pharmaceutical": ("SUNPHARMA", 1.0, "direct"),
    
    # Adani Group
    "Adani": ("ADANIENT", 0.7, "sector"),  # Generic Adani mention
}

# Sector mappings
SECTOR_STOCKS = {
    "Banking": [
        ("HDFCBANK", 0.7, "sector"),
        ("ICICIBANK", 0.7, "sector"),
        ("AXISBANK", 0.7, "sector"),
        ("KOTAKBANK", 0.7, "sector"),
        ("SBIN", 0.7, "sector"),
    ],
    "Financial Services": [
        ("HDFCBANK", 0.6, "sector"),
        ("ICICIBANK", 0.6, "sector"),
        ("AXISBANK", 0.6, "sector"),
        ("KOTAKBANK", 0.6, "sector"),
        ("SBIN", 0.6, "sector"),
    ],
    "IT": [
        ("TCS", 0.7, "sector"),
        ("INFY", 0.7, "sector"),
        ("WIPRO", 0.7, "sector"),
        ("HCLTECH", 0.7, "sector"),
    ],
    "Telecom": [
        ("BHARTIARTL", 0.7, "sector"),
        ("RELIANCE", 0.6, "sector"),
    ],
    "Automobile": [
        ("MARUTI", 0.7, "sector"),
        ("TATAMOTORS", 0.7, "sector"),
    ],
    "Pharmaceutical": [
        ("SUNPHARMA", 0.7, "sector"),
    ],
}

# Regulator mappings
REGULATOR_IMPACTS = {
    "RBI": {
        "stocks": [
            ("HDFCBANK", 0.8, "regulatory"),
            ("ICICIBANK", 0.8, "regulatory"),
            ("AXISBANK", 0.8, "regulatory"),
            ("KOTAKBANK", 0.8, "regulatory"),
            ("SBIN", 0.8, "regulatory"),
        ],
        "sectors": ["Banking", "Financial Services"]
    },
    "SEBI": {
        "stocks": [],  # Market-wide impact
        "sectors": ["Financial Services"]
    },
    "NSE": {
        "stocks": [],  # Market-wide impact
        "sectors": []
    },
    "BSE": {
        "stocks": [],  # Market-wide impact
        "sectors": []
    },
}


def map_company_to_stock(company_name: str) -> List[Tuple[str, float, str]]:
    """Map a company name to stock symbol(s) with confidence."""
    results = []
    company_lower = company_name.lower()
    
    # Direct mapping
    for key, (symbol, confidence, impact_type) in STOCK_MAP.items():
        if key.lower() in company_lower or company_lower in key.lower():
            results.append((symbol, confidence, impact_type))
    
    return results if results else []


def map_sector_to_stocks(sector_name: str) -> List[Tuple[str, float, str]]:
    """Map a sector to relevant stocks."""
    sector_lower = sector_name.lower()
    
    for sector, stocks in SECTOR_STOCKS.items():
        if sector.lower() in sector_lower or sector_lower in sector.lower():
            return stocks
    
    return []


def map_regulator_to_impacts(regulator_name: str) -> Dict:
    """Map a regulator to impacted stocks and sectors."""
    regulator_upper = regulator_name.upper()
    
    for regulator, impacts in REGULATOR_IMPACTS.items():
        if regulator in regulator_upper or regulator_upper in regulator:
            return impacts
    
    return {"stocks": [], "sectors": []}

