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
            records: Dictionary of group IDs mapping to lists of related field names
                    Example: {
                        "group_1": ["first_name", "last_name", "dob"],
                        "group_2": ["address", "phone"]
                    }
        """
        self.common_records = records
        logger.info(f"Updated common records configuration with {len(records)} groups")
        
        # Initialize mappings for each group
        for group_id, fields in records.items():
            # Create a shared mapping file for the group
            mapping_file = os.path.join('configs', 'mappings', f"{group_id}.json")
            
            # Load existing mapping if available
            shared_mapping = {}
            if os.path.exists(mapping_file):
                try:
                    with open(mapping_file, 'r') as f:
                        shared_mapping = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading mapping for {group_id}: {str(e)}")
            
            # Ensure each field in the group uses the shared mapping
            for field in fields:
                if field in self.sanitizers:
                    self.sanitizers[field].set_shared_mapping(shared_mapping, mapping_file)
    
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
        
        # Track which fields have been processed to avoid double-processing
        processed_fields = set()
        
        # First process fields in common record groups
        for group_id, fields in self.common_records.items():
            # Create shared mapping file for the group
            mapping_file = os.path.join('configs', 'mappings', f"{group_id}.json")
            shared_mapping = {}
            
            # Load existing shared mapping if available
            if os.path.exists(mapping_file):
                try:
                    with open(mapping_file, 'r') as f:
                        shared_mapping = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading mapping for {group_id}: {str(e)}")
            
            # Process each field in the group
            for field_name in fields:
                if field_name not in sanitized_data.columns:
                    logger.warning(f"Field not found in data: {field_name}")
                    continue
                
                config = self.field_configs.get(field_name, {})
                sanitizer = self.sanitizers.get(field_name)
                if not sanitizer:
                    continue
                
                try:
                    # Set shared mapping for the field
                    sanitizer.set_shared_mapping(shared_mapping, mapping_file)
                    
                    # Sanitize the field
                    sanitized_data[field_name] = sanitizer.sanitize_series(
                        sanitized_data[field_name],
                        preserve_format=config.get('preserve_format', True)
                    )
                    
                    processed_fields.add(field_name)
                    logger.info(f"Sanitized field in group {group_id}: {field_name}")
                    
                except Exception as e:
                    logger.error(f"Error sanitizing field {field_name}: {str(e)}")
        
        # Process remaining fields that aren't part of any group
        for field_name, config in self.field_configs.items():
            if field_name in processed_fields:
                continue
                
            if field_name not in sanitized_data.columns:
                logger.warning(f"Field not found in data: {field_name}")
                continue
            
            sanitizer = self.sanitizers.get(field_name)
            if not sanitizer:
                continue
            
            try:
                # Use individual mapping for non-grouped fields
                if config.get('consistent_mapping'):
                    mapping_file = os.path.join('configs', 'mappings', f"{field_name}.json")
                    if os.path.exists(mapping_file):
                        sanitizer.load_mapping(mapping_file)
                
                # Sanitize the field
                sanitized_data[field_name] = sanitizer.sanitize_series(
                    sanitized_data[field_name],
                    preserve_format=config.get('preserve_format', True)
                )
                
                # Save individual mapping
                if config.get('consistent_mapping'):
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
