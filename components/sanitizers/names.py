import logging
from faker import Faker
from .base import BaseSanitizer

logger = logging.getLogger('phi_cleanse')

class NameSanitizer(BaseSanitizer):
    """Base class for name sanitization"""
    
    def __init__(self):
        super().__init__()
        self.fake = Faker()
    
    def sanitize(self, value, preserve_format=True):
        """
        Sanitize a name value
        
        Args:
            value: The name to sanitize
            preserve_format: Whether to preserve the original format
            
        Returns:
            The sanitized name
        """
        if not value or not isinstance(value, str):
            return value
        
        sanitized = self._get_consistent_value(value)
        
        if preserve_format:
            sanitized = self._preserve_format(value, sanitized)
        
        return sanitized

class FullNameSanitizer(NameSanitizer):
    """Sanitizer for full names"""
    
    def _generate_value(self, original_value):
        """Generate a new full name"""
        return self.fake.name()

class FirstNameSanitizer(NameSanitizer):
    """Sanitizer for first names"""
    
    def _generate_value(self, original_value):
        """Generate a new first name"""
        return self.fake.first_name()

class LastNameSanitizer(NameSanitizer):
    """Sanitizer for last names"""
    
    def _generate_value(self, original_value):
        """Generate a new last name"""
        return self.fake.last_name()

class MiddleNameSanitizer(NameSanitizer):
    """Sanitizer for middle names"""
    
    def _generate_value(self, original_value):
        """Generate a new middle name"""
        # If original is just an initial
        if len(original_value) == 1:
            return self.fake.random_letter().upper()
        return self.fake.first_name()  # Use first name as middle name
