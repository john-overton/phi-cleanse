import logging
import re
from datetime import datetime, timedelta
from faker import Faker
from .base import BaseSanitizer

logger = logging.getLogger('phi_cleanse')

class DateSanitizer(BaseSanitizer):
    """Base sanitizer for dates"""
    
    def __init__(self):
        super().__init__()
        self.fake = Faker()
        
        # Common date formats
        self.date_formats = [
            "%Y-%m-%d",      # 2023-12-31
            "%m/%d/%Y",      # 12/31/2023
            "%m-%d-%Y",      # 12-31-2023
            "%d/%m/%Y",      # 31/12/2023
            "%d-%m-%Y",      # 31-12-2023
            "%b %d, %Y",     # Dec 31, 2023
            "%B %d, %Y",     # December 31, 2023
            "%Y%m%d",        # 20231231
            "%m/%d/%y",      # 12/31/23
            "%d/%m/%y",      # 31/12/23
        ]
    
    def _parse_date(self, value):
        """Try to parse date string using various formats"""
        for fmt in self.date_formats:
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
        return None
    
    def _format_date(self, date, original_format):
        """Format date according to original format"""
        try:
            return date.strftime(original_format)
        except ValueError:
            return date.strftime(self.date_formats[0])  # fallback to ISO format

class DOBSanitizer(DateSanitizer):
    """Sanitizer for dates of birth"""
    
    def sanitize(self, value, preserve_format=True):
        if not value or not isinstance(value, str):
            return value
        
        # Try to parse the original date
        original_date = None
        original_format = None
        
        for fmt in self.date_formats:
            try:
                original_date = datetime.strptime(value.strip(), fmt)
                original_format = fmt
                break
            except ValueError:
                continue
        
        if not original_date:
            logger.warning(f"Could not parse date: {value}")
            return value
        
        sanitized = self._get_consistent_value(value)
        
        if preserve_format and original_format:
            try:
                # Parse the sanitized date and reformat it
                sanitized_date = datetime.strptime(sanitized, self.date_formats[0])
                sanitized = self._format_date(sanitized_date, original_format)
            except ValueError as e:
                logger.error(f"Error formatting date: {str(e)}")
        
        return sanitized
    
    def _generate_value(self, original_value):
        """Generate a new date of birth"""
        # Try to parse original date to maintain approximate age
        original_date = self._parse_date(original_value)
        
        if original_date:
            # Generate a date within 1 year of original
            days_diff = self.fake.random_int(min=-365, max=365)
            new_date = original_date + timedelta(days=days_diff)
        else:
            # Fallback to random date between 18 and 90 years ago
            new_date = self.fake.date_of_birth(minimum_age=18, maximum_age=90)
        
        # Return in ISO format
        return new_date.strftime("%Y-%m-%d")

class AppointmentDateSanitizer(DateSanitizer):
    """Sanitizer for appointment dates"""
    
    def sanitize(self, value, preserve_format=True):
        if not value or not isinstance(value, str):
            return value
        
        # Try to parse the original date
        original_date = None
        original_format = None
        
        for fmt in self.date_formats:
            try:
                original_date = datetime.strptime(value.strip(), fmt)
                original_format = fmt
                break
            except ValueError:
                continue
        
        if not original_date:
            logger.warning(f"Could not parse date: {value}")
            return value
        
        sanitized = self._get_consistent_value(value)
        
        if preserve_format and original_format:
            try:
                # Parse the sanitized date and reformat it
                sanitized_date = datetime.strptime(sanitized, self.date_formats[0])
                sanitized = self._format_date(sanitized_date, original_format)
            except ValueError as e:
                logger.error(f"Error formatting date: {str(e)}")
        
        return sanitized
    
    def _generate_value(self, original_value):
        """Generate a new appointment date"""
        # Try to parse original date
        original_date = self._parse_date(original_value)
        
        if original_date:
            # Generate a date within 30 days of original
            days_diff = self.fake.random_int(min=-30, max=30)
            new_date = original_date + timedelta(days=days_diff)
            
            # Avoid weekends
            while new_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                new_date += timedelta(days=1)
        else:
            # Fallback to random future date
            new_date = self.fake.future_date(end_date='+30d')
        
        # Return in ISO format
        return new_date.strftime("%Y-%m-%d")
