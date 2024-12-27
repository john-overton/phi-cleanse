import logging
from abc import ABC, abstractmethod
import json
import os

logger = logging.getLogger('phi_cleanse')

class BaseSanitizer(ABC):
    """Base class for all data sanitizers"""
    
    def __init__(self):
        self.mapping = {}
        self.reverse_mapping = {}
        self.shared_mapping = None
        self.shared_mapping_file = None
    
    @abstractmethod
    def sanitize(self, value, preserve_format=True):
        """
        Sanitize a single value
        
        Args:
            value: The value to sanitize
            preserve_format: Whether to preserve the original format
            
        Returns:
            The sanitized value
        """
        pass
    
    def sanitize_series(self, series, preserve_format=True):
        """
        Sanitize a pandas series
        
        Args:
            series: pandas.Series to sanitize
            preserve_format: Whether to preserve the original format
            
        Returns:
            pandas.Series with sanitized values
        """
        return series.apply(lambda x: self.sanitize(x, preserve_format))
    
    def get_mapping(self):
        """Get the current value mapping"""
        return self.shared_mapping if self.shared_mapping is not None else self.mapping
    
    def set_mapping(self, mapping):
        """Set a predefined value mapping"""
        if self.shared_mapping is not None:
            self.shared_mapping.update(mapping)
            self._save_shared_mapping()
        else:
            self.mapping = mapping
            self.reverse_mapping = {v: k for k, v in mapping.items()}
    
    def set_shared_mapping(self, mapping, mapping_file):
        """Set a shared mapping for related fields"""
        self.shared_mapping = mapping
        self.shared_mapping_file = mapping_file
        logger.info(f"Using shared mapping from {mapping_file}")
    
    def _save_shared_mapping(self):
        """Save the shared mapping to file"""
        if self.shared_mapping is not None and self.shared_mapping_file:
            try:
                os.makedirs(os.path.dirname(self.shared_mapping_file), exist_ok=True)
                with open(self.shared_mapping_file, 'w') as f:
                    json.dump(self.shared_mapping, f, indent=2)
                logger.info(f"Saved shared mapping to {self.shared_mapping_file}")
            except Exception as e:
                logger.error(f"Error saving shared mapping: {str(e)}")
    
    def save_mapping(self, filename):
        """Save the current mapping to a file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.mapping, f, indent=2)
            logger.info(f"Saved mapping to {filename}")
        except Exception as e:
            logger.error(f"Error saving mapping: {str(e)}")
    
    def load_mapping(self, filename):
        """Load a mapping from a file"""
        try:
            with open(filename, 'r') as f:
                self.mapping = json.load(f)
                self.reverse_mapping = {v: k for k, v in self.mapping.items()}
            logger.info(f"Loaded mapping from {filename}")
        except Exception as e:
            logger.error(f"Error loading mapping: {str(e)}")
    
    def clear_mapping(self):
        """Clear the current mapping"""
        self.mapping = {}
        self.reverse_mapping = {}
    
    def _get_consistent_value(self, original_value):
        """Get a consistent sanitized value for a given input"""
        mapping = self.shared_mapping if self.shared_mapping is not None else self.mapping
        reverse_mapping = {v: k for k, v in mapping.items()}
        
        if original_value in mapping:
            return mapping[original_value]
        
        # Generate new value
        new_value = self._generate_value(original_value)
        
        # Ensure uniqueness
        while new_value in reverse_mapping:
            new_value = self._generate_value(original_value)
        
        # Store mapping
        mapping[original_value] = new_value
        
        # Save shared mapping if using one
        if self.shared_mapping is not None:
            self._save_shared_mapping()
        else:
            self.reverse_mapping[new_value] = original_value
        
        return new_value
    
    @abstractmethod
    def _generate_value(self, original_value):
        """Generate a new sanitized value"""
        pass
    
    def _preserve_format(self, original, new):
        """Preserve the format of the original value"""
        if not original or not new:
            return new
            
        # Preserve case
        if original.isupper():
            return new.upper()
        elif original.islower():
            return new.lower()
        elif original[0].isupper():
            return new.capitalize()
        
        return new
