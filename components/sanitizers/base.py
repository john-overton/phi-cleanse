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
        return self.mapping
    
    def set_mapping(self, mapping):
        """Set a predefined value mapping"""
        self.mapping = mapping
        self.reverse_mapping = {v: k for k, v in mapping.items()}
    
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
        if original_value in self.mapping:
            return self.mapping[original_value]
        
        # Generate new value
        new_value = self._generate_value(original_value)
        
        # Ensure uniqueness
        while new_value in self.reverse_mapping:
            new_value = self._generate_value(original_value)
        
        # Store mapping
        self.mapping[original_value] = new_value
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
