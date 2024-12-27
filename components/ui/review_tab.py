import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import pandas as pd
import os

logger = logging.getLogger('phi_cleanse')

class FieldConfigDialog(tk.Toplevel):
    """Dialog for configuring field sanitization settings"""
    def __init__(self, parent, field_name, field_type=None):
        super().__init__(parent)
        self.title(f"Configure Field: {field_name}")
        self.geometry("400x500")
        self.transient(parent)
        self.grab_set()
        
        # Store field info
        self.field_name = field_name
        self.field_type = field_type
        self.result = None
        
        self.setup_ui()
        
        # Center dialog
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Field type selection
        type_frame = ttk.LabelFrame(self, text="Field Type", padding=10)
        type_frame.pack(fill="x", padx=10, pady=5)
        
        self.type_var = tk.StringVar(value=self.field_type or "")
        
        # Add field type options from protected_fields.csv
        for field_type in ["full_name", "first_name", "last_name", "date_of_birth", 
                          "ssn", "address", "phone_number", "email"]:
            ttk.Radiobutton(type_frame, text=field_type.replace("_", " ").title(),
                          value=field_type, variable=self.type_var).pack(anchor="w")
        
        # Sanitization options
        options_frame = ttk.LabelFrame(self, text="Options", padding=10)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        self.preserve_format = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Preserve data format",
                       variable=self.preserve_format).pack(anchor="w")
        
        self.consistent_mapping = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Use consistent mapping",
                       variable=self.consistent_mapping).pack(anchor="w")
        
        # Preview section
        preview_frame = ttk.LabelFrame(self, text="Sample Output", padding=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Add preview content here when sanitization engine is implemented
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right")
    
    def on_ok(self):
        """Save configuration and close dialog"""
        self.result = {
            'field_type': self.type_var.get(),
            'preserve_format': self.preserve_format.get(),
            'consistent_mapping': self.consistent_mapping.get()
        }
        self.destroy()

class ReviewTab(ttk.Frame):
    """Tab for reviewing and configuring field sanitization"""
    def __init__(self, parent):
        super().__init__(parent)
        self.data_processor = None
        self.detected_fields = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Top frame for common settings
        self.settings_frame = ttk.LabelFrame(self, text="Common Record Settings", padding=10)
        self.settings_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(self.settings_frame, 
                 text="Configure settings for maintaining consistency across records"
        ).pack(anchor="w")
        
        # Main frame for data grid
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create table with scrollbars
        self.create_table()
        
        # Bottom frame for actions
        self.action_frame = ttk.Frame(self)
        self.action_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(
            self.action_frame,
            text="Save Configuration",
            command=self.save_configuration
        ).pack(side="right", padx=5)
        
        ttk.Button(
            self.action_frame,
            text="Load Configuration",
            command=self.load_configuration
        ).pack(side="right")
    
    def create_table(self):
        """Create the data preview table"""
        # Create scrollbars
        y_scroll = ttk.Scrollbar(self.main_frame)
        y_scroll.pack(side="right", fill="y")
        
        x_scroll = ttk.Scrollbar(self.main_frame, orient="horizontal")
        x_scroll.pack(side="bottom", fill="x")
        
        # Create treeview
        self.table = ttk.Treeview(
            self.main_frame,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        self.table.pack(fill="both", expand=True)
        
        # Configure scrollbars
        y_scroll.config(command=self.table.yview)
        x_scroll.config(command=self.table.xview)
        
        # Bind double-click event
        self.table.bind("<Double-1>", self.on_field_click)
    
    def update_content(self, data):
        """Update table content with imported data"""
        if not isinstance(data, pd.DataFrame):
            logger.error("Invalid data format for review tab")
            return
        
        # Get data processor from import tab
        import_tab = self.master.winfo_children()[0]  # First tab is import tab
        self.data_processor = import_tab.get_processor()
        self.detected_fields = getattr(import_tab, 'detected_fields', {})
        
        # Clear existing items
        self.table.delete(*self.table.get_children())
        
        # Configure columns
        self.table["columns"] = list(data.columns)
        self.table["show"] = "headings"
        
        for col in data.columns:
            # Add PHI indicator if field was detected
            if col in self.detected_fields:
                detection = self.detected_fields[col]
                heading_text = f"{col} (PHI: {detection['field_type']})"
            else:
                heading_text = col
            
            self.table.heading(col, text=heading_text)
            
            # Set column width based on content
            max_width = max(
                len(str(heading_text)),
                data[col].astype(str).str.len().max()
            ) * 10
            self.table.column(col, width=min(max_width, 300))
        
        # Insert data
        for idx, row in data.iterrows():
            self.table.insert("", "end", values=list(row))
    
    def on_field_click(self, event):
        """Handle field configuration dialog"""
        region = self.table.identify("region", event.x, event.y)
        if region == "heading":
            column = self.table.identify_column(event.x)
            column_id = int(column[1]) - 1  # Convert #1 to 0, #2 to 1, etc.
            field_name = self.table["columns"][column_id]
            
            # Get current field type if detected
            current_type = None
            if field_name in self.detected_fields:
                current_type = self.detected_fields[field_name]['field_type']
            
            dialog = FieldConfigDialog(self, field_name, current_type)
            self.wait_window(dialog)
            
            if dialog.result:
                logger.info(f"Field {field_name} configured: {dialog.result}")
                # Update configuration in data processor
                self.data_processor.configure_field(field_name, dialog.result)
                
                # Update column heading to show configuration
                heading_text = f"{field_name} (PHI: {dialog.result['field_type']})"
                self.table.heading(column, text=heading_text)
    
    def save_configuration(self):
        """Save current configuration to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
            initialdir="configs"
        )
        
        if filename:
            # Extract just the filename without path
            base_filename = os.path.basename(filename)
            self.data_processor.save_configuration(base_filename)
            messagebox.showinfo("Success", "Configuration saved successfully")
    
    def load_configuration(self):
        """Load configuration from file"""
        available_configs = self.data_processor.get_available_configurations()
        
        if not available_configs:
            messagebox.showinfo("No Configurations", 
                              "No saved configurations found")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Load Configuration")
        dialog.geometry("300x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Create listbox with scrollbar
        frame = ttk.Frame(dialog)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        listbox.pack(side="left", expand=True, fill="both")
        
        scrollbar.config(command=listbox.yview)
        
        # Insert configurations
        for config in available_configs:
            listbox.insert("end", config)
        
        def on_ok():
            selection = listbox.curselection()
            if selection:
                selected_config = available_configs[selection[0]]
                self.data_processor.load_configuration(selected_config)
                messagebox.showinfo("Success", "Configuration loaded successfully")
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Create buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="left", padx=5)
