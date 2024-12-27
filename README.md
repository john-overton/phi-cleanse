# PHI Cleanse Tool

A Python application for sanitizing Protected Health Information (PHI) in CSV and Excel files while maintaining data consistency and format.

## Features

- Import CSV and Excel files with PHI data
- Automatic detection of PHI fields based on column names
- Configurable sanitization settings for each field
- Consistent data mapping across records
- Format preservation for sanitized data
- Configuration save/load functionality
- Export sanitized data to CSV
- PHI-safe logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/phi-cleanse.git
cd phi-cleanse
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python app/main.py
```

2. Import Data:
   - Click "Import File" button
   - Select your CSV or Excel file
   - For Excel files, select the worksheet to process
   - The tool will analyze field names and suggest PHI fields

3. Review & Configure:
   - Review detected PHI fields
   - Click on column headers to configure sanitization settings
   - Set field types for replacement data
   - Configure common record settings for consistent mapping
   - Save configurations for future use

4. Preview & Export:
   - Review sanitized data with highlighted changes
   - Export the sanitized data as CSV

## Supported PHI Types

- Names (Full, First, Last, Middle)
- Dates (Birth dates, Appointment dates)
- Identifiers (SSN, MRN, Insurance ID, Driver's License)
- Contact Information (Address, Phone, Email)
- And more...

## Configuration

Configurations are stored in the `configs` directory and can be:
- Saved for different file types
- Loaded for quick processing
- Shared across team members

Each configuration includes:
- Field mappings
- Data type settings
- Common record settings

## Logging

Logs are stored in the `logs` directory with:
- Unique session identifiers
- PHI-safe error messages
- Processing statistics
- Configuration changes

## Development

### Project Structure
```
phi-cleanse/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   └── logger.py
├── components/
│   ├── sanitizers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── names.py
│   │   ├── dates.py
│   │   ├── identifiers.py
│   │   └── contact.py
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py
│       ├── import_tab.py
│       ├── review_tab.py
│       └── preview_tab.py
├── utils/
│   ├── __init__.py
│   ├── phi_detector.py
│   └── data_processor.py
├── configs/
├── logs/
└── requirements.txt
```

### Adding New Sanitizers

1. Create a new sanitizer class in `components/sanitizers/`
2. Inherit from `BaseSanitizer`
3. Implement `sanitize()` and `_generate_value()` methods
4. Add to `SANITIZER_MAP` in `components/sanitizers/__init__.py`

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
