import tkinter as tk
from tkinter import ttk, font
import logging
import pandas as pd
from .field_config_dialog import FieldConfigDialog

logger = logging.getLogger('phi_cleanse')

class DataGrid(ttk.Frame):
    """Data grid component with PHI highlighting and field configuration"""
    
    def __init__(self, parent, data_processor=None):
        super().__init__(parent)
        self.data_processor = data_processor
        self.detected_fields = {}
        self.phi_columns = set()
        
        # Configure custom styles
        style = ttk.Style()
        
        # Configure treeview styles
        style.configure('Highlight.Treeview',
                       background='white',
                       fieldbackground='white')
        
        style.configure('Highlight.Treeview.Heading',
                       background='#f5f5f5',  # Light gray for headings
                       relief='raised')
        
        # Configure selection colors
        style.map('Highlight.Treeview',
                 background=[('selected', '#e3f2fd')],  # Light blue when selected
                 foreground=[('selected', 'black')])    # Keep text black when selected
        
        self.setup_ui()
        self.setup_context_menu()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Create container frame
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        # Create scrollbars
        y_scroll = ttk.Scrollbar(self.container)
        y_scroll.pack(side="right", fill="y")
        
        x_scroll = ttk.Scrollbar(self.container, orient="horizontal")
        x_scroll.pack(side="bottom", fill="x")
        
        # Create treeview
        self.table = ttk.Treeview(
            self.container,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
            selectmode="extended",
            style='Highlight.Treeview'
        )
        self.table.pack(side="left", fill="both", expand=True)
        
        # Configure scrollbars
        y_scroll.config(command=self.table.yview)
        x_scroll.config(command=self.table.xview)
        
        # Configure column resizing
        self.table.bind('<B1-Motion>', self.on_column_resize)
        
        # Bind events
        self.table.bind("<Shift-MouseWheel>", self.on_horizontal_scroll)
        
        # Configure PHI tag
        self.table.tag_configure('phi', background='#fff3e0')  # Light orange for PHI cells
    
    def setup_context_menu(self):
        """Setup right-click context menu"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit Field", command=self.show_field_config)
        
        # Bind right-click event
        self.table.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        # Get clicked column
        region = self.table.identify("region", event.x, event.y)
        if region == "heading":
            self.clicked_column = self.table.identify_column(event.x)
            self.context_menu.post(event.x_root, event.y_root)
    
    def show_field_config(self):
        """Show field configuration dialog for clicked column"""
        if not hasattr(self, 'clicked_column'):
            return
            
        column_id = int(self.clicked_column[1]) - 1  # Convert #1 to 0, #2 to 1, etc.
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
            
            # Update column heading
            heading_text = f"{field_name} (PHI: {dialog.result['field_type']})"
            self.table.heading(self.clicked_column, text=heading_text)
            
            # Update PHI columns set
            self.phi_columns.add(field_name)
            
            # Refresh the data to update PHI highlighting
            self.refresh_data()
    
    def refresh_data(self):
        """Refresh the data display with current PHI settings"""
        # Store current data
        data = []
        for item in self.table.get_children():
            values = self.table.item(item)['values']
            data.append(values)
        
        # Clear and reinsert with updated PHI highlighting
        self.table.delete(*self.table.get_children())
        for values in data:
            self.insert_row(values)
    
    def insert_row(self, values):
        """Insert a row with proper PHI highlighting"""
        # Create list of tags for this row
        tags = []
        for col_idx, col in enumerate(self.table["columns"]):
            if col in self.phi_columns:
                tags.append(f'phi_{col_idx}')
                self.table.tag_configure(f'phi_{col_idx}', background='#fff3e0')
        
        # Insert row with tags
        item_id = self.table.insert("", "end", values=values, tags=tags)
        return item_id
    
    def update_content(self, data, detected_fields=None):
        """Update table content with imported data"""
        if not isinstance(data, pd.DataFrame):
            logger.error("Invalid data format for data grid")
            return
        
        logger.info(f"Data grid updating with DataFrame shape: {data.shape}")
        self.detected_fields = detected_fields or {}
        
        # Clear existing items
        self.table.delete(*self.table.get_children())
        logger.info("Cleared existing items from table")
        
        # Configure columns
        columns = list(data.columns)
        logger.info(f"Configuring {len(columns)} columns: {columns}")
        self.table["columns"] = columns
        self.table["show"] = "headings"
        
        # Configure each column
        for col_idx, col in enumerate(data.columns):
            # Set heading text
            heading_text = col
            
            if col in self.detected_fields:
                detection = self.detected_fields[col]
                heading_text = f"{col} (PHI: {detection['field_type']})"
                self.phi_columns.add(col)
            
            self.table.heading(col, text=heading_text)
            
            # Set column width and allow stretching
            sample_width = min(
                max(
                    len(str(heading_text)) * 10,
                    data[col].astype(str).str.len().max() * 10,
                    300  # Maximum width
                ),
                100  # Minimum width
            )
            self.table.column(col, width=sample_width, minwidth=100, stretch=True)
        
        # Insert all data rows
        logger.info(f"Inserting {len(data)} rows into table")
        for idx, row in data.iterrows():
            try:
                # Convert all values to strings and handle None/NaN
                values = []
                for val in row:
                    if pd.isna(val):
                        values.append("")
                    else:
                        try:
                            values.append(str(val))
                        except Exception as e:
                            logger.warning(f"Error converting value to string: {val}, using repr() instead")
                            values.append(repr(val))
                
                # Insert row with PHI highlighting
                self.insert_row(values)
                logger.debug(f"Inserted row {idx}")
                
            except Exception as e:
                logger.error(f"Error inserting row {idx}: {str(e)}")
                logger.error(f"Row values: {values}")
        
        logger.info("Data grid update complete")
    
    def on_horizontal_scroll(self, event):
        """Handle horizontal scrolling with Shift+MouseWheel"""
        self.table.xview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"
    
    def on_column_resize(self, event):
        """Handle column resize event"""
        region = self.table.identify_region(event.x, event.y)
        if region == "separator":
            column = self.table.identify_column(event.x)
            tree_x = event.x - self.table.winfo_rootx()
            new_width = max(100, tree_x - self.table.column(column, "x"))
            self.table.column(column, width=new_width)
            return "break"
