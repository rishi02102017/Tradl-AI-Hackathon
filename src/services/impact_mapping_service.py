"""Impact mapping service - maps entities to stock impacts."""
from typing import List, Dict, Tuple
from src.utils.stock_mapper import (
    map_company_to_stock,
    map_sector_to_stocks,
    map_regulator_to_impacts
)
import logging

logger = logging.getLogger(__name__)


class ImpactMappingService:
    """Service for mapping entities to stock impacts with confidence scores."""
    
    def map_entities_to_stocks(self, entities: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Map extracted entities to impacted stocks.
        
        Args:
            entities: Dictionary of extracted entities by type
            
        Returns:
            List of stock impact dictionaries
        """
        stock_impacts = {}
        
        # Map companies to stocks (direct impact)
        for company in entities.get('companies', []):
            company_name = company['name']
            stock_mappings = map_company_to_stock(company_name)
            
            for symbol, confidence, impact_type in stock_mappings:
                # Adjust confidence based on entity confidence
                adjusted_confidence = confidence * company.get('confidence', 1.0)
                
                if symbol not in stock_impacts:
                    stock_impacts[symbol] = {
                        'symbol': symbol,
                        'confidence': adjusted_confidence,
                        'impact_type': impact_type,
                        'reasoning': f"Direct mention of {company_name}"
                    }
                else:
                    # Take maximum confidence if already exists
                    if adjusted_confidence > stock_impacts[symbol]['confidence']:
                        stock_impacts[symbol]['confidence'] = adjusted_confidence
                        stock_impacts[symbol]['impact_type'] = impact_type
                        stock_impacts[symbol]['reasoning'] = f"Direct mention of {company_name}"
        
        # Map sectors to stocks (sector-wide impact)
        for sector in entities.get('sectors', []):
            sector_name = sector['name']
            sector_stocks = map_sector_to_stocks(sector_name)
            
            for symbol, confidence, impact_type in sector_stocks:
                # Adjust confidence based on entity confidence
                adjusted_confidence = confidence * sector.get('confidence', 1.0)
                
                if symbol not in stock_impacts:
                    stock_impacts[symbol] = {
                        'symbol': symbol,
                        'confidence': adjusted_confidence,
                        'impact_type': impact_type,
                        'reasoning': f"Sector-wide impact: {sector_name}"
                    }
                else:
                    # For sector impacts, we might want to keep the higher confidence
                    # but update reasoning if it's more specific
                    if impact_type == 'sector' and stock_impacts[symbol]['impact_type'] != 'direct':
                        if adjusted_confidence > stock_impacts[symbol]['confidence']:
                            stock_impacts[symbol]['confidence'] = adjusted_confidence
                            stock_impacts[symbol]['reasoning'] = f"Sector-wide impact: {sector_name}"
        
        # Map regulators to stocks (regulatory impact)
        for regulator in entities.get('regulators', []):
            regulator_name = regulator['name']
            regulator_impacts = map_regulator_to_impacts(regulator_name)
            
            # Add direct stock impacts
            for symbol, confidence, impact_type in regulator_impacts.get('stocks', []):
                adjusted_confidence = confidence * regulator.get('confidence', 1.0)
                
                if symbol not in stock_impacts:
                    stock_impacts[symbol] = {
                        'symbol': symbol,
                        'confidence': adjusted_confidence,
                        'impact_type': impact_type,
                        'reasoning': f"Regulatory impact from {regulator_name}"
                    }
                else:
                    # Regulatory impacts might override sector impacts
                    if impact_type == 'regulatory':
                        if adjusted_confidence > stock_impacts[symbol]['confidence']:
                            stock_impacts[symbol]['confidence'] = adjusted_confidence
                            stock_impacts[symbol]['impact_type'] = impact_type
                            stock_impacts[symbol]['reasoning'] = f"Regulatory impact from {regulator_name}"
            
            # Add sector impacts from regulators
            for sector_name in regulator_impacts.get('sectors', []):
                sector_stocks = map_sector_to_stocks(sector_name)
                for symbol, confidence, impact_type in sector_stocks:
                    adjusted_confidence = confidence * 0.8 * regulator.get('confidence', 1.0)
                    
                    if symbol not in stock_impacts:
                        stock_impacts[symbol] = {
                            'symbol': symbol,
                            'confidence': adjusted_confidence,
                            'impact_type': 'regulatory',
                            'reasoning': f"Regulatory impact on {sector_name} sector from {regulator_name}"
                        }
                    else:
                        if adjusted_confidence > stock_impacts[symbol]['confidence']:
                            stock_impacts[symbol]['confidence'] = adjusted_confidence
                            stock_impacts[symbol]['impact_type'] = 'regulatory'
                            stock_impacts[symbol]['reasoning'] = f"Regulatory impact on {sector_name} sector from {regulator_name}"
        
        return list(stock_impacts.values())
    
    def get_impact_summary(self, stock_impacts: List[Dict]) -> Dict:
        """Get a summary of stock impacts."""
        direct_impacts = [s for s in stock_impacts if s['impact_type'] == 'direct']
        sector_impacts = [s for s in stock_impacts if s['impact_type'] == 'sector']
        regulatory_impacts = [s for s in stock_impacts if s['impact_type'] == 'regulatory']
        
        return {
            'total_impacts': len(stock_impacts),
            'direct_impacts': len(direct_impacts),
            'sector_impacts': len(sector_impacts),
            'regulatory_impacts': len(regulatory_impacts),
            'high_confidence': len([s for s in stock_impacts if s['confidence'] >= 0.8]),
            'medium_confidence': len([s for s in stock_impacts if 0.5 <= s['confidence'] < 0.8]),
            'low_confidence': len([s for s in stock_impacts if s['confidence'] < 0.5])
        }

