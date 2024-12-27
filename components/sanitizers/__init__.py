from .base import BaseSanitizer
from .names import (
    FullNameSanitizer,
    FirstNameSanitizer,
    LastNameSanitizer,
    MiddleNameSanitizer
)
from .identifiers import (
    SSNSanitizer,
    MRNSanitizer,
    InsuranceIDSanitizer,
    DriversLicenseSanitizer,
    MedicaidNumberSanitizer
)
from .contact import (
    AddressSanitizer,
    PhoneNumberSanitizer,
    EmailSanitizer
)
from .dates import (
    DOBSanitizer,
    AppointmentDateSanitizer
)

# Map field types to their sanitizers
SANITIZER_MAP = {
    'full_name': FullNameSanitizer,
    'first_name': FirstNameSanitizer,
    'last_name': LastNameSanitizer,
    'middle_name': MiddleNameSanitizer,
    'date_of_birth': DOBSanitizer,
    'ssn': SSNSanitizer,
    'address': AddressSanitizer,
    'phone_number': PhoneNumberSanitizer,
    'email': EmailSanitizer,
    'medical_record_number': MRNSanitizer,
    'insurance_id': InsuranceIDSanitizer,
    'drivers_license': DriversLicenseSanitizer,
    'appointment_date': AppointmentDateSanitizer,
    'medicaid_number': MedicaidNumberSanitizer
}

def get_sanitizer(field_type):
    """Get the appropriate sanitizer for a field type"""
    sanitizer_class = SANITIZER_MAP.get(field_type)
    if sanitizer_class:
        return sanitizer_class()
    return None
