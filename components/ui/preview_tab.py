import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import pandas as pd
import os

logger = logging.getLogger('phi_cleanse')

class PreviewTab(ttk.Frame):
    """Tab for previewing sanitized data and exporting"""
    def __init__(self, parent):
        super().__init__(parent)
        self.data_processor = None
        self.sanitized_data = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Top frame for export options
        self.options_frame = ttk.Frame(self)
        self.options_frame.pack(fill="x", padx=10, pady=5)
        
        # Export button
        self.export_button = ttk.Button(
            self.options_frame,
            text="Export to CSV",
            command=self.export_data
        )
        self.export_button.pack(side="right", padx=5)
        
        # Main frame for data grid
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create table with scrollbars
        self.create_table()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self,
            textvariable=self.status_var,
            relief="sunken",
            padding=5
        )
        self.status_bar.pack(fill="x", padx=10, pady=5)
    
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
        
        # Configure tags for highlighting
        self.table.tag_configure(
            'sanitized',
            background='#e6ffe6'  # Light green background
        )
    
    def update_content(self, data):
        """Update table content with sanitized data"""
        if not isinstance(data, pd.DataFrame):
            logger.error("Invalid data format for preview tab")
            return
        
        # Get data processor from import tab
        import_tab = self.master.winfo_children()[0]  # First tab is import tab
        self.data_processor = import_tab.get_processor()
        
        # Sanitize data
        self.sanitized_data = self.data_processor.sanitize_data()
        if self.sanitized_data is None:
            return
        
        # Clear existing items
        self.table.delete(*self.table.get_children())
        
        # Configure columns
        self.table["columns"] = list(data.columns)
        self.table["show"] = "headings"
        
        for col in data.columns:
            self.table.heading(col, text=col)
            # Set column width based on content
            max_width = max(
                len(str(col)),
                data[col].astype(str).str.len().max()
            ) * 10
            self.table.column(col, width=min(max_width, 300))
        
        # Insert data and highlight sanitized fields
        for idx, row in self.sanitized_data.iterrows():
            item_id = self.table.insert("", "end", values=list(row))
            
            # Highlight sanitized columns
            for col, value in row.items():
                if col in self.data_processor.field_configs:
                    col_idx = list(self.sanitized_data.columns).index(col)
                    self.table.item(item_id, tags=('sanitized',))
    
    def export_data(self):
        """Export sanitized data to CSV"""
        if self.sanitized_data is None:
            messagebox.showwarning("No Data", "No sanitized data to export")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export Sanitized Data",
            defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        
        if filename:
            try:
                # Export to CSV
                self.sanitized_data.to_csv(filename, index=False)
                self.status_var.set("Data exported successfully")
                logger.info(f"Exported sanitized data to: {filename}")
                messagebox.showinfo("Success", "Data exported successfully")
            except Exception as e:
                error_msg = f"Error exporting data: {str(e)}"
                self.status_var.set(error_msg)
                logger.error(error_msg)
                messagebox.showerror("Error", error_msg)
    
    def highlight_sanitized_fields(self, sanitized_columns):
        """Highlight columns that have been sanitized"""
        # This will be implemented when the sanitization engine is ready
        pass
