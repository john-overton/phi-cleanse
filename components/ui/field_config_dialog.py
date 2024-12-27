import tkinter as tk
from tkinter import ttk
import logging
import csv
import os

logger = logging.getLogger('phi_cleanse')

class FieldConfigDialog(tk.Toplevel):
    """Dialog for configuring field sanitization settings"""
    
    def __init__(self, parent, field_name, field_type=None):
        super().__init__(parent)
        self.title(f"Configure Field: {field_name}")
        self.geometry("400x600")
        self.transient(parent)
        self.grab_set()
        
        # Store field info
        self.field_name = field_name
        self.field_type = field_type
        self.result = None
        
        # Load field types and data types from protected_fields.csv
        self.field_types = self.load_field_types()
        
        self.setup_ui()
        
        # Center dialog
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def load_field_types(self):
        """Load field types and their expected data types from protected_fields.csv"""
        field_types = {}
        try:
            csv_path = os.path.join('sample_data', 'protected_fields.csv')
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    field_types[row['field_type']] = {
                        'description': row.get('description', ''),
                        'data_type': row.get('data_type', 'string'),
                        'format': row.get('format', '')
                    }
        except Exception as e:
            logger.error(f"Error loading field types: {str(e)}")
            # Fallback to basic types if file can't be loaded
            field_types = {
                'full_name': {'data_type': 'string'},
                'first_name': {'data_type': 'string'},
                'last_name': {'data_type': 'string'},
                'date_of_birth': {'data_type': 'date'},
                'ssn': {'data_type': 'string'},
                'medicaid_number': {'data_type': 'string'},
                'address': {'data_type': 'string'},
                'phone_number': {'data_type': 'string'},
                'email': {'data_type': 'string'}
            }
        return field_types
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Field type selection
        type_frame = ttk.LabelFrame(self, text="Field Type", padding=10)
        type_frame.pack(fill="x", padx=10, pady=5)
        
        self.type_var = tk.StringVar(value=self.field_type or "")
        self.type_var.trace('w', self.on_type_change)
        
        # Add field type options
        for field_type, info in self.field_types.items():
            frame = ttk.Frame(type_frame)
            frame.pack(fill="x", pady=2)
            
            radio = ttk.Radiobutton(
                frame,
                text=field_type.replace("_", " ").title(),
                value=field_type,
                variable=self.type_var
            )
            radio.pack(side="left")
            
            if info.get('data_type'):
                ttk.Label(
                    frame,
                    text=f"({info['data_type']})",
                    foreground='gray'
                ).pack(side="left", padx=5)
        
        # Data type info
        self.info_frame = ttk.LabelFrame(self, text="Field Information", padding=10)
        self.info_frame.pack(fill="x", padx=10, pady=5)
        
        self.info_label = ttk.Label(self.info_frame, wraplength=350)
        self.info_label.pack(fill="x")
        
        # Format example
        self.format_frame = ttk.LabelFrame(self, text="Expected Format", padding=10)
        self.format_frame.pack(fill="x", padx=10, pady=5)
        
        self.format_label = ttk.Label(self.format_frame, wraplength=350)
        self.format_label.pack(fill="x")
        
        # Sanitization options
        options_frame = ttk.LabelFrame(self, text="Options", padding=10)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        self.preserve_format = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Preserve data format",
            variable=self.preserve_format
        ).pack(anchor="w")
        
        self.consistent_mapping = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Use consistent mapping",
            variable=self.consistent_mapping
        ).pack(anchor="w")
        
        # Preview section
        preview_frame = ttk.LabelFrame(self, text="Sample Output", padding=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Add preview content here when sanitization engine is implemented
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right")
        
        # Update info for initial field type
        self.update_field_info()
    
    def on_type_change(self, *args):
        """Handle field type change"""
        self.update_field_info()
    
    def update_field_info(self):
        """Update field information display"""
        field_type = self.type_var.get()
        if field_type in self.field_types:
            info = self.field_types[field_type]
            
            # Update description
            if info.get('description'):
                self.info_label.config(text=info['description'])
            else:
                self.info_label.config(text="No description available")
            
            # Update format example
            if info.get('format'):
                self.format_label.config(text=f"Example: {info['format']}")
            else:
                self.format_label.config(text="No format example available")
        else:
            self.info_label.config(text="")
            self.format_label.config(text="")
    
    def on_ok(self):
        """Save configuration and close dialog"""
        field_type = self.type_var.get()
        if not field_type:
            tk.messagebox.showerror(
                "Error",
                "Please select a field type"
            )
            return
        
        self.result = {
            'field_type': field_type,
            'data_type': self.field_types[field_type]['data_type'],
            'preserve_format': self.preserve_format.get(),
            'consistent_mapping': self.consistent_mapping.get()
        }
        self.destroy()
