"""Entity extraction service using NER."""
import spacy
from typing import List, Dict, Tuple
import logging
import re

logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy model not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None


class EntityExtractionService:
    """Service for extracting entities from news articles."""
    
    # Common financial entities patterns
    BANK_PATTERNS = [
        r'\bHDFC\s+Bank\b', r'\bICICI\s+Bank\b', r'\bAxis\s+Bank\b',
        r'\bKotak\s+Bank\b', r'\bSBI\b', r'\bState\s+Bank\s+of\s+India\b'
    ]
    
    REGULATOR_PATTERNS = [
        r'\bRBI\b', r'\bReserve\s+Bank\s+of\s+India\b',
        r'\bSEBI\b', r'\bNSE\b', r'\bBSE\b'
    ]
    
    SECTOR_KEYWORDS = {
        'Banking': ['bank', 'banking', 'lender', 'loan', 'deposit', 'credit'],
        'Financial Services': ['financial', 'finance', 'banking', 'investment'],
        'IT': ['IT', 'software', 'technology', 'digital', 'tech', 'consulting'],
        'Telecom': ['telecom', 'telecommunication', 'mobile', '5G', 'network'],
        'Automobile': ['automobile', 'auto', 'vehicle', 'car', 'motor'],
        'Pharmaceutical': ['pharma', 'pharmaceutical', 'drug', 'medicine'],
        'Infrastructure': ['infrastructure', 'construction', 'project', 'metro']
    }
    
    def __init__(self):
        if nlp is None:
            logger.warning("spaCy model not loaded. Entity extraction may be limited.")
    
    def extract_entities(self, text: str, title: str = "") -> Dict[str, List[Dict]]:
        """
        Extract entities from text.
        
        Returns:
            Dict with entity types as keys and lists of entities as values
        """
        full_text = f"{title} {text}"
        entities = {
            'companies': [],
            'sectors': [],
            'regulators': [],
            'people': [],
            'events': []
        }
        
        # Use spaCy for NER if available
        if nlp:
            doc = nlp(full_text)
            
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    # Check if it's a company
                    if any(keyword in ent.text.lower() for keyword in ['bank', 'ltd', 'limited', 'inc', 'corp']):
                        entities['companies'].append({
                            'name': ent.text,
                            'confidence': 0.9
                        })
                    # Check if it's a regulator
                    elif any(re.search(pattern, ent.text, re.IGNORECASE) for pattern in self.REGULATOR_PATTERNS):
                        entities['regulators'].append({
                            'name': ent.text,
                            'confidence': 0.95
                        })
                
                elif ent.label_ == "PERSON":
                    entities['people'].append({
                        'name': ent.text,
                        'confidence': 0.9
                    })
        
        # Pattern-based extraction for financial entities
        self._extract_financial_entities(full_text, entities)
        
        # Extract sectors
        self._extract_sectors(full_text, entities)
        
        # Remove duplicates
        for key in entities:
            seen = set()
            unique_entities = []
            for ent in entities[key]:
                if ent['name'] not in seen:
                    seen.add(ent['name'])
                    unique_entities.append(ent)
            entities[key] = unique_entities
        
        return entities
    
    def _extract_financial_entities(self, text: str, entities: Dict):
        """Extract financial entities using patterns."""
        # Extract banks
        for pattern in self.BANK_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities['companies'].append({
                    'name': match.group(),
                    'confidence': 0.95
                })
        
        # Extract regulators
        for pattern in self.REGULATOR_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities['regulators'].append({
                    'name': match.group(),
                    'confidence': 0.95
                })
        
        # Common company names
        company_patterns = [
            r'\bTCS\b', r'\bTata\s+Consultancy\b', r'\bInfosys\b', r'\bWipro\b',
            r'\bReliance\s+Industries\b', r'\bRIL\b', r'\bBharti\s+Airtel\b',
            r'\bMaruti\s+Suzuki\b', r'\bTata\s+Motors\b', r'\bL&T\b',
            r'\bLarsen\s+&\s+Toubro\b', r'\bSun\s+Pharma\b'
        ]
        
        for pattern in company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities['companies'].append({
                    'name': match.group(),
                    'confidence': 0.9
                })
    
    def _extract_sectors(self, text: str, entities: Dict):
        """Extract sectors based on keywords."""
        text_lower = text.lower()
        
        for sector, keywords in self.SECTOR_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                entities['sectors'].append({
                    'name': sector,
                    'confidence': 0.7
                })
        
        # Specific sector mentions
        sector_patterns = [
            (r'\bbanking\s+sector\b', 'Banking'),
            (r'\bIT\s+sector\b', 'IT'),
            (r'\btelecom\s+sector\b', 'Telecom'),
            (r'\bautomobile\s+sector\b', 'Automobile'),
            (r'\bpharma\s+sector\b', 'Pharmaceutical'),
        ]
        
        for pattern, sector in sector_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                entities['sectors'].append({
                    'name': sector,
                    'confidence': 0.9
                })

