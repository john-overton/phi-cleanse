import logging
import re
from faker import Faker
from .base import BaseSanitizer

logger = logging.getLogger('phi_cleanse')

class AddressSanitizer(BaseSanitizer):
    """Sanitizer for addresses"""
    
    def __init__(self):
        super().__init__()
        self.fake = Faker()
    
    def sanitize(self, value, preserve_format=True):
        if not value or not isinstance(value, str):
            return value
        
        sanitized = self._get_consistent_value(value)
        
        if preserve_format:
            # Preserve case and basic formatting
            sanitized = self._preserve_format(value, sanitized)
            
            # Try to preserve apartment/unit format
            apt_match = re.search(r'(#|Apt\.?|Unit|Suite)\s*([A-Za-z0-9-]+)', value, re.IGNORECASE)
            if apt_match:
                # Replace the generated address's apt/unit number with original format
                sanitized = re.sub(
                    r'(#|Apt\.?|Unit|Suite)\s*([A-Za-z0-9-]+)',
                    f"{apt_match.group(1)} {apt_match.group(2)}",
                    sanitized,
                    flags=re.IGNORECASE
                )
        
        return sanitized
    
    def _generate_value(self, original_value):
        """Generate a new address"""
        return self.fake.street_address()

class PhoneNumberSanitizer(BaseSanitizer):
    """Sanitizer for phone numbers"""
    
    def __init__(self):
        super().__init__()
        self.fake = Faker()
        # Pattern to identify phone number format
        self.pattern = re.compile(r'''
            (?P<area>\d{3})?[).\s-]*
            (?P<prefix>\d{3})[.\s-]*
            (?P<line>\d{4})
            (?P<ext>\s*(?:ext|x|ext.)\s*\d+)?
        ''', re.VERBOSE)
    
    def sanitize(self, value, preserve_format=True):
        if not value or not isinstance(value, str):
            return value
        
        sanitized = self._get_consistent_value(value)
        
        if preserve_format:
            # Try to match original format
            match = self.pattern.search(value)
            if match:
                # Get the original formatting
                area_format = value[:match.start('prefix')].replace(
                    match.group('area') or '', 'XXX'
                )
                separator = value[match.start('prefix'):match.start('line')].replace(
                    match.group('prefix'), ''
                )
                
                # Apply original formatting
                parts = sanitized.split('-')
                if len(parts) == 3:
                    area, prefix, line = parts
                    formatted = area_format.replace('XXX', area) + prefix + separator + line
                    
                    # Add extension if original had one
                    if match.group('ext'):
                        formatted += match.group('ext')
                    
                    return formatted
        
        return sanitized
    
    def _generate_value(self, original_value):
        """Generate a new phone number"""
        return self.fake.numerify('###-###-####')

class EmailSanitizer(BaseSanitizer):
    """Sanitizer for email addresses"""
    
    def __init__(self):
        super().__init__()
        self.fake = Faker()
    
    def sanitize(self, value, preserve_format=True):
        if not value or not isinstance(value, str):
            return value
        
        sanitized = self._get_consistent_value(value)
        
        if preserve_format:
            # Preserve domain if requested
            original_domain = value.split('@')[-1]
            sanitized_parts = sanitized.split('@')
            if len(sanitized_parts) == 2:
                sanitized = f"{sanitized_parts[0]}@{original_domain}"
            
            # Preserve case
            sanitized = self._preserve_format(value, sanitized)
        
        return sanitized
    
    def _generate_value(self, original_value):
        """Generate a new email address"""
        # Generate random email but preserve domain structure
        original_domain = original_value.split('@')[-1]
        username = self.fake.user_name()
        domain_parts = original_domain.split('.')
        
        if len(domain_parts) > 1:
            # Generate similar domain structure
            new_domain = f"{self.fake.word()}.{domain_parts[-1]}"
        else:
            new_domain = self.fake.domain_name()
        
        return f"{username}@{new_domain}"
