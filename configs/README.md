# PHI Cleanse Configurations Directory

This directory stores saved sanitization configurations and field mappings.

## Structure

- `*.json` - Configuration files containing field settings and common record mappings
- `mappings/*.json` - Individual field mapping files for consistent data sanitization

## Configuration File Format

```json
{
  "field_configs": {
    "field_name": {
      "field_type": "type_name",
      "preserve_format": true,
      "consistent_mapping": true
    }
  },
  "common_records": {
    "field_name": true
  }
}
```

## Field Mapping File Format

```json
{
  "original_value1": "sanitized_value1",
  "original_value2": "sanitized_value2"
}
```

## Notes

- Do not store any actual PHI data in configuration files
- Mappings should only contain sanitized values
- Configuration files can be shared between team members
- Each field type has its own mapping file when using consistent mapping
