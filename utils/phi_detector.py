import pandas as pd
import logging
from Levenshtein import ratio
import os

logger = logging.getLogger('phi_cleanse')

class PHIDetector:
    """Detects potential PHI fields in data based on field names and patterns"""
    
    def __init__(self):
        self.protected_fields = None
        self.load_protected_fields()
    
    def load_protected_fields(self):
        """Load protected field definitions from CSV"""
        try:
            # Get the path relative to the current file
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            fields_path = os.path.join(base_path, 'sample_data', 'protected_fields.csv')
            
            self.protected_fields = pd.read_csv(fields_path)
            logger.info("Loaded protected fields definitions")
        except Exception as e:
            logger.error(f"Error loading protected fields: {str(e)}")
            self.protected_fields = pd.DataFrame(columns=['primary_field', 'common_aliases'])
    
    def analyze_field_name(self, field_name):
        """Analyze a single field name and return potential PHI type"""
        if self.protected_fields is None:
            return None
        
        field_name = field_name.lower().strip()
        best_match = None
        best_score = 0.7  # Minimum similarity threshold
        
        for _, row in self.protected_fields.iterrows():
            # Check exact match with primary field
            if field_name == row['primary_field'].lower():
                return {
                    'field_type': row['primary_field'],
                    'confidence': 1.0,
                    'match_type': 'exact'
                }
            
            # Check aliases
            aliases = [alias.strip().lower() for alias in row['common_aliases'].split(',')]
            if field_name in aliases:
                return {
                    'field_type': row['primary_field'],
                    'confidence': 1.0,
                    'match_type': 'alias'
                }
            
            # Check fuzzy matches
            # First check primary field
            score = ratio(field_name, row['primary_field'].lower())
            if score > best_score:
                best_score = score
                best_match = {
                    'field_type': row['primary_field'],
                    'confidence': score,
                    'match_type': 'fuzzy'
                }
            
            # Then check aliases
            for alias in aliases:
                score = ratio(field_name, alias)
                if score > best_score:
                    best_score = score
                    best_match = {
                        'field_type': row['primary_field'],
                        'confidence': score,
                        'match_type': 'fuzzy'
                    }
        
        return best_match
    
    def analyze_fields(self, df):
        """Analyze all fields in a dataframe and return PHI field suggestions"""
        results = {}
        
        for column in df.columns:
            match = self.analyze_field_name(column)
            if match:
                results[column] = match
                logger.info(f"Detected potential PHI field: {column} -> {match['field_type']} "
                          f"(confidence: {match['confidence']:.2f}, type: {match['match_type']})")
        
        return results
    
    def analyze_data_patterns(self, df, column):
        """Analyze data patterns in a column to confirm PHI type"""
        # This will be implemented to analyze actual data patterns
        # For example:
        # - Check if values match SSN pattern (XXX-XX-XXXX)
        # - Check if values match date patterns
        # - Check if values match phone number patterns
        # - etc.
        pass
