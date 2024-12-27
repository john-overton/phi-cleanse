import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger('phi_cleanse')

class HelpComponent(ttk.Frame):
    """A help component that displays instructions in a popup window"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.help_text = """PHI Cleanse Tool Documentation

Overview
--------
The PHI Cleanse Tool helps sanitize files containing Protected Health Information (PHI) 
by replacing sensitive data with randomly generated but consistently mapped values.

File Requirements
----------------
- Supported formats: CSV, Excel (.xlsx, .xls)
- Files should have headers identifying the columns
- For Excel files, you will be prompted to select the worksheet to process

Step-by-Step Usage
-----------------
1. Import File:
   - Click "Import File" button
   - Select your CSV or Excel file
   - For Excel, select the worksheet to process
   - The tool will analyze field names and suggest PHI fields

2. Review & Configure:
   - Review detected PHI fields
   - Click on columns to configure sanitization settings
   - Select field types for replacement data
   - Configure common record settings for consistent mapping

3. Preview & Export:
   - Review the sanitized data
   - Highlighted fields show sanitized content
   - Export the cleaned data as CSV
   - Save configuration for future use

Configuration Management
----------------------
- Saved configurations are stored in the 'configs' folder
- Configurations can be quickly loaded for similar file types
- Each configuration saves:
  * Field mappings
  * Data type settings
  * Common record settings

Error Handling
-------------
If errors occur:
1. Check the logs folder for detailed information
2. Verify file format and contents
3. Ensure all required fields are properly configured

Notes
-----
- PHI data is never logged or stored
- Consistent mapping ensures the same input always produces the same sanitized output
- Regular review of sanitized data helps ensure proper configuration

"""
        # Create help button with ? symbol
        self.help_button = ttk.Button(self, text="?", width=3, command=self.show_help)
        self.help_button.pack(side="right", padx=5)
    
    def show_help(self):
        """Display help window with instructions"""
        help_window = tk.Toplevel()
        help_window.title("PHI Cleanse Tool Help")
        help_window.geometry("600x500")
        
        # Create text widget
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(expand=True, fill="both")
        
        # Insert help text
        text_widget.insert("1.0", self.help_text)
        text_widget.config(state="disabled")  # Make text read-only
        
        # Add close button
        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)
        
        logger.info("Help documentation displayed")
