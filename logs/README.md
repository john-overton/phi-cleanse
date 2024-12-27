# PHI Cleanse Logs Directory

This directory contains application logs with PHI-safe logging practices.

## Log File Format

Log files are named with timestamp: `phi_cleanse_YYYYMMDD_HHMMSS.log`

Each log entry includes:
- Timestamp
- Log level
- Module/Component
- Action/Event description
- Error details (if applicable)

## PHI-Safe Logging Guidelines

1. Never log actual PHI data
2. Use field names and generic descriptions
3. Log processing statistics without data content
4. For errors, log the error type and location without sensitive data

## Example Log Entries

```
2024-01-20 10:15:30 - INFO - Import - Imported CSV file: example.csv
2024-01-20 10:15:31 - INFO - PHI Detector - Detected 5 potential PHI fields
2024-01-20 10:15:32 - INFO - Data Processor - Configured sanitizer for field: patient_name
2024-01-20 10:15:33 - WARNING - Data Processor - Field not found in data: birth_date
2024-01-20 10:15:34 - ERROR - Export - Error exporting file: Permission denied
```

## Retention

- Log files are created per session
- Implement appropriate retention policies based on your organization's requirements
- Regularly clean up old log files
- Ensure logs don't contain any PHI data before sharing
