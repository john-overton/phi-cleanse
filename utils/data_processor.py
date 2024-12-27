import logging
import pandas as pd
import json
import os
from typing import Dict, Tuple, Optional

from .phi_detector import PHIDetector
from components.sanitizers import get_sanitizer

logger = logging.getLogger('phi_cleanse')

class DataProcessor:
    """Handles data processing and sanitization"""
    
    def __init__(self):
        self.phi_detector = PHIDetector()
        self.imported_data = None
        self.field_configs = {}
        self.sanitizers = {}
        self.common_records = {}
    
    def process_file(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Process imported data and detect PHI fields
        
        Args:
            data: The imported DataFrame
            
        Returns:
            Tuple of (processed DataFrame, detected PHI fields)
        """
        self.imported_data = data
        
        # Detect PHI fields
        detected_fields = self.phi_detector.analyze_fields(data)
        
        logger.info(f"Detected {len(detected_fields)} potential PHI fields")
        
        return data, detected_fields
    
    def configure_field(self, field_name: str, config: Dict) -> None:
        """
        Configure sanitization settings for a field
        
        Args:
            field_name: Name of the field to configure
            config: Configuration dictionary containing:
                   - field_type: Type of PHI field
                   - preserve_format: Whether to preserve data format
                   - consistent_mapping: Whether to use consistent mapping
        """
        self.field_configs[field_name] = config
        
        # Initialize sanitizer
        if config.get('field_type'):
            sanitizer = get_sanitizer(config['field_type'])
            if sanitizer:
                self.sanitizers[field_name] = sanitizer
                logger.info(f"Configured sanitizer for field: {field_name}")
            else:
                logger.warning(f"No sanitizer found for field type: {config['field_type']}")
    
    def set_common_records(self, records: Dict) -> None:
        """
        Set common records mapping
        
        Args:
            records: Dictionary of field names and their common record settings
        """
        self.common_records = records
        logger.info("Updated common records configuration")
    
    def sanitize_data(self) -> pd.DataFrame:
        """
        Sanitize the data based on current configuration
        
        Returns:
            DataFrame with sanitized data
        """
        if self.imported_data is None:
            logger.error("No data to sanitize")
            return None
        
        sanitized_data = self.imported_data.copy()
        
        for field_name, config in self.field_configs.items():
            if field_name not in sanitized_data.columns:
                logger.warning(f"Field not found in data: {field_name}")
                continue
            
            sanitizer = self.sanitizers.get(field_name)
            if not sanitizer:
                continue
            
            try:
                # Load any existing mapping for consistent records
                if config.get('consistent_mapping') and field_name in self.common_records:
                    mapping_file = os.path.join('configs', 'mappings', f"{field_name}.json")
                    if os.path.exists(mapping_file):
                        sanitizer.load_mapping(mapping_file)
                
                # Sanitize the field
                sanitized_data[field_name] = sanitizer.sanitize_series(
                    sanitized_data[field_name],
                    preserve_format=config.get('preserve_format', True)
                )
                
                # Save mapping if using consistent mapping
                if config.get('consistent_mapping') and field_name in self.common_records:
                    os.makedirs(os.path.join('configs', 'mappings'), exist_ok=True)
                    sanitizer.save_mapping(mapping_file)
                
                logger.info(f"Sanitized field: {field_name}")
                
            except Exception as e:
                logger.error(f"Error sanitizing field {field_name}: {str(e)}")
        
        return sanitized_data
    
    def save_configuration(self, filename: str) -> None:
        """
        Save current configuration to file
        
        Args:
            filename: Name of the configuration file
        """
        config = {
            'field_configs': self.field_configs,
            'common_records': self.common_records
        }
        
        try:
            os.makedirs('configs', exist_ok=True)
            with open(os.path.join('configs', filename), 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved configuration to: {filename}")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
    
    def load_configuration(self, filename: str) -> None:
        """
        Load configuration from file
        
        Args:
            filename: Name of the configuration file
        """
        try:
            with open(os.path.join('configs', filename), 'r') as f:
                config = json.load(f)
            
            self.field_configs = config.get('field_configs', {})
            self.common_records = config.get('common_records', {})
            
            # Reinitialize sanitizers
            self.sanitizers = {}
            for field_name, field_config in self.field_configs.items():
                if field_config.get('field_type'):
                    sanitizer = get_sanitizer(field_config['field_type'])
                    if sanitizer:
                        self.sanitizers[field_name] = sanitizer
            
            logger.info(f"Loaded configuration from: {filename}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
    
    def get_available_configurations(self) -> list:
        """
        Get list of available configuration files
        
        Returns:
            List of configuration file names
        """
        try:
            if not os.path.exists('configs'):
                return []
            
            return [f for f in os.listdir('configs') 
                   if f.endswith('.json') and os.path.isfile(os.path.join('configs', f))]
        except Exception as e:
            logger.error(f"Error listing configurations: {str(e)}")
            return []
