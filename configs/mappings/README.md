# PHI Cleanse Field Mappings Directory

This directory stores mapping files that maintain consistent sanitization across records.

## Purpose

When sanitizing PHI data with the "Use consistent mapping" option enabled, the application maintains a one-to-one mapping between original values and their sanitized replacements. These mappings are stored in this directory as JSON files, with one file per field.

## File Format

Each mapping file is named after the field it represents (e.g., `full_name.json`, `ssn.json`) and contains a JSON object mapping original values to their sanitized replacements:

```json
{
  "original_value1": "sanitized_value1",
  "original_value2": "sanitized_value2",
  "original_value3": "sanitized_value3"
}
```

## Security Notes

- Mapping files should be treated as sensitive data since they contain the relationship between original and sanitized values
- Consider encrypting or securely deleting mapping files after use if required by your security policies
- Do not share mapping files unless absolutely necessary, as they could be used to reverse the sanitization process

## File Management

- Files are automatically created when sanitizing fields with consistent mapping enabled
- Files are automatically loaded when processing new data with the same configuration
- Old mapping files can be safely deleted if consistency with previous sanitizations is not required
- The application will create new mapping files as needed
