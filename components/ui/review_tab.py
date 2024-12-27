import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import pandas as pd
import os

from .common_records_dialog import CommonRecordsDialog
from .data_grid import DataGrid

logger = logging.getLogger('phi_cleanse')

class ReviewTab(ttk.Frame):
    """Tab for reviewing and configuring field sanitization"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.data_processor = None
        self.detected_fields = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Button for common record settings
        self.common_records_btn = ttk.Button(
            self, 
            text="Common Record Settings",
            command=self.show_common_records_dialog
        )
        self.common_records_btn.pack(fill="x", padx=10, pady=(5, 0))
        
        # Data grid for displaying and configuring data
        self.data_grid = DataGrid(self)
        self.data_grid.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bottom frame for actions
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        ttk.Button(
            action_frame,
            text="Save Configuration",
            command=self.save_configuration
        ).pack(side="right", padx=5)
        
        ttk.Button(
            action_frame,
            text="Load Configuration",
            command=self.load_configuration
        ).pack(side="right")
    
    def show_common_records_dialog(self):
        """Show dialog for configuring common records"""
        if not self.data_processor:
            messagebox.showwarning(
                "No Data",
                "Please import data before configuring common records"
            )
            return
        
        dialog = CommonRecordsDialog(
            self,
            columns=self.data_grid.table["columns"],
            detected_fields=self.detected_fields,
            current_groups=self.data_processor.common_records
        )
        
        result = dialog.show()
        if result is not None:
            self.data_processor.set_common_records(result)
    
    def update_content(self, data):
        """Update content with imported data"""
        if not isinstance(data, pd.DataFrame):
            logger.error("Invalid data format for review tab")
            return
        
        logger.info(f"Review tab received data with shape: {data.shape}")
        
        # Get data processor from import tab
        import_tab = self.master.winfo_children()[0]  # First tab is import tab
        self.data_processor = import_tab.get_processor()
        self.detected_fields = getattr(import_tab, 'detected_fields', {})
        
        logger.info(f"Retrieved detected fields: {list(self.detected_fields.keys())}")
        
        # Update data grid
        self.data_grid.data_processor = self.data_processor
        logger.info("Updating data grid content...")
        self.data_grid.update_content(data, self.detected_fields)
        logger.info("Data grid update complete")
    
    def save_configuration(self):
        """Save current configuration to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
            initialdir="configs"
        )
        
        if filename:
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
