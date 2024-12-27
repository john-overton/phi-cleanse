import logging
import random
import re
from faker import Faker
from .base import BaseSanitizer

logger = logging.getLogger('phi_cleanse')

class SSNSanitizer(BaseSanitizer):
    """Sanitizer for Social Security Numbers"""
    
    def __init__(self):
        super().__init__()
        self.pattern = re.compile(r'^\d{3}-?\d{2}-?\d{4}$')
    
    def sanitize(self, value, preserve_format=True):
        if not value or not isinstance(value, str):
            return value
        
        # Check if value matches SSN pattern
        original_format = bool(self.pattern.match(value))
        has_dashes = '-' in value
        
        sanitized = self._get_consistent_value(value)
        
        if preserve_format and original_format and has_dashes:
            # Add dashes if original had them
            sanitized = f"{sanitized[:3]}-{sanitized[3:5]}-{sanitized[5:]}"
        
        return sanitized
    
    def _generate_value(self, original_value):
        """Generate a new SSN"""
        # Generate area number (first 3 digits)
        area = random.randint(1, 899)  # 900-999 are not valid area numbers
        
        # Generate group number (middle 2 digits)
        group = random.randint(1, 99)
        
        # Generate serial number (last 4 digits)
        serial = random.randint(1, 9999)
        
        # Format without dashes
        return f"{area:03d}{group:02d}{serial:04d}"

class MRNSanitizer(BaseSanitizer):
    """Sanitizer for Medical Record Numbers"""
    
    def __init__(self):
        super().__init__()
        self.fake = Faker()
    
    def sanitize(self, value, preserve_format=True):
        if not value or not isinstance(value, str):
            return value
        
        sanitized = self._get_consistent_value(value)
        
        if preserve_format:
            # Preserve length and any prefix/suffix patterns
            if value[0].isalpha():  # If original starts with letter
                sanitized = sanitized[0].upper() + sanitized[1:]
            if len(value) != len(sanitized):
                sanitized = sanitized[:len(value)]
        
        return sanitized
    
    def _generate_value(self, original_value):
        """Generate a new MRN"""
        # Generate a random string of digits with optional letter prefix
        length = len(original_value)
        if original_value[0].isalpha():
            return self.fake.lexify('?') + self.fake.numerify('#' * (length - 1))
        return self.fake.numerify('#' * length)

class InsuranceIDSanitizer(BaseSanitizer):
    """Sanitizer for Insurance IDs"""
    
    def __init__(self):
        super().__init__()
        self.fake = Faker()
    
    def sanitize(self, value, preserve_format=True):
        if not value or not isinstance(value, str):
            return value
        
        sanitized = self._get_consistent_value(value)
        
        if preserve_format:
            # Preserve any special formatting (dashes, spaces, etc.)
            format_chars = re.findall(r'[^a-zA-Z0-9]', value)
            if format_chars:
                sanitized_parts = list(sanitized)
                original_parts = list(value)
                for i, char in enumerate(original_parts):
                    if char in format_chars and i < len(sanitized_parts):
                        sanitized_parts[i] = char
                sanitized = ''.join(sanitized_parts)
        
        return sanitized
    
    def _generate_value(self, original_value):
        """Generate a new Insurance ID"""
        # Remove any non-alphanumeric characters
        clean_value = re.sub(r'[^a-zA-Z0-9]', '', original_value)
        length = len(clean_value)
        
        # Generate pattern based on original
        pattern = ''
        for char in clean_value:
            if char.isalpha():
                pattern += '?'
            else:
                pattern += '#'
        
        return self.fake.bothify(pattern)

class MedicaidNumberSanitizer(BaseSanitizer):
    """Sanitizer for Medicaid Numbers"""
    
    def __init__(self):
        super().__init__()
        self.fake = Faker()
        # Common Medicaid number patterns:
        # - AA12345A (alpha-numeric with letter suffix)
        # - 1234567890 (pure numeric, length varies by state)
        # - AB-12345678 (with separators)
        self.patterns = [
            re.compile(r'^[A-Z]{2}\d{5}[A-Z]$'),  # AA12345A
            re.compile(r'^\d{7,12}$'),            # Pure numeric
            re.compile(r'^[A-Z]{2}-\d{8}$')       # With separator
        ]
    
    def sanitize(self, value, preserve_format=True):
        if not value or not isinstance(value, str):
            return value
        
        sanitized = self._get_consistent_value(value)
        
        if preserve_format:
            # Preserve any separators
            if '-' in value:
                parts = sanitized.split('-')
                if len(parts) == 2:
                    sanitized = f"{parts[0]}-{parts[1]}"
            
            # Ensure same length as original
            if len(value) != len(sanitized):
                sanitized = sanitized[:len(value)]
        
        return sanitized
    
    def _generate_value(self, original_value):
        """Generate a new Medicaid number matching the original format"""
        # Clean the original value
        clean_value = re.sub(r'[^A-Z0-9]', '', original_value.upper())
        
        # Check which pattern it matches
        for pattern in self.patterns:
            if pattern.match(clean_value):
                if pattern == self.patterns[0]:  # AA12345A
                    return (
                        self.fake.lexify('??') +
                        self.fake.numerify('#####') +
                        self.fake.lexify('?')
                    )
                elif pattern == self.patterns[1]:  # Pure numeric
                    return self.fake.numerify('#' * len(clean_value))
                elif pattern == self.patterns[2]:  # With separator
                    return (
                        self.fake.lexify('??') +
                        '-' +
                        self.fake.numerify('########')
                    )
        
        # Default to same length random alphanumeric
        return self.fake.bothify('?' * len(clean_value))


class DriversLicenseSanitizer(BaseSanitizer):
    """Sanitizer for Drivers License Numbers"""
    
    def __init__(self):
        super().__init__()
        self.fake = Faker()
    
    def sanitize(self, value, preserve_format=True):
        if not value or not isinstance(value, str):
            return value
        
        sanitized = self._get_consistent_value(value)
        
        if preserve_format:
            # Preserve state prefix if present
            if value[:2].isalpha():
                sanitized = value[:2] + sanitized[2:]
            # Preserve length
            if len(value) != len(sanitized):
                sanitized = sanitized[:len(value)]
        
        return sanitized
    
    def _generate_value(self, original_value):
        """Generate a new Drivers License Number"""
        # Keep state prefix if present
        if original_value[:2].isalpha():
            state_prefix = original_value[:2]
            length = len(original_value) - 2
            return state_prefix + self.fake.bothify('?' * length)
        
        # Otherwise generate completely random
        return self.fake.bothify('?' * len(original_value))
