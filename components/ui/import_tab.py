import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import pandas as pd

from utils.data_processor import DataProcessor

logger = logging.getLogger('phi_cleanse')

class ImportTab(ttk.Frame):
    """Tab for importing and initially processing files"""
    def __init__(self, parent):
        super().__init__(parent)
        self.data_processor = DataProcessor()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Create centered frame for import button
        self.center_frame = ttk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Create import button
        self.import_button = ttk.Button(
            self.center_frame,
            text="Import File",
            command=self.import_file,
            width=20
        )
        self.import_button.pack(pady=10)
        
        # Create label for supported formats
        self.format_label = ttk.Label(
            self.center_frame,
            text="Supported formats: CSV, Excel (.xlsx, .xls)",
            font=("Arial", 10)
        )
        self.format_label.pack(pady=5)
        
        # Create progress frame (hidden initially)
        self.progress_frame = ttk.Frame(self)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            length=300,
            mode='determinate',
            variable=self.progress_var
        )
        self.progress_label = ttk.Label(self.progress_frame, text="")
        
        self.progress_bar.pack(pady=5)
        self.progress_label.pack(pady=5)
    
    def import_file(self):
        """Handle file import"""
        filename = filedialog.askopenfilename(
            title="Select File to Sanitize",
            filetypes=(
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            )
        )
        
        if not filename:
            return
        
        try:
            # Show progress
            self.progress_frame.place(relx=0.5, rely=0.6, anchor="center")
            self.progress_var.set(0)
            self.progress_label.config(text="Reading file...")
            self.update_idletasks()
            
            # Import based on file type
            if filename.lower().endswith('.csv'):
                try:
                    # First try with default settings
                    self.imported_data = pd.read_csv(filename)
                except pd.errors.ParserError:
                    # If that fails, try with more flexible parsing
                    logger.info("Retrying CSV import with error_bad_lines=False")
                    self.imported_data = pd.read_csv(
                        filename,
                        on_bad_lines='skip',  # Skip lines with too many fields
                        encoding='utf-8',     # Explicitly set encoding
                        engine='python'       # Use python engine for better error handling
                    )
                    messagebox.showwarning(
                        "Import Warning",
                        "Some rows in the CSV file had inconsistent formatting and were skipped. "
                        "Please check the data carefully."
                    )
                logger.info(f"Imported CSV file: {filename}")
            else:  # Excel file
                # Get list of sheets
                excel_file = pd.ExcelFile(filename)
                if len(excel_file.sheet_names) > 1:
                    sheet_name = self.select_sheet(excel_file.sheet_names)
                    if not sheet_name:
                        return
                else:
                    sheet_name = excel_file.sheet_names[0]
                
                self.imported_data = pd.read_excel(filename, sheet_name=sheet_name)
                logger.info(f"Imported Excel file: {filename}, sheet: {sheet_name}")
            
            # Update progress
            self.progress_var.set(50)
            self.progress_label.config(text="Analyzing fields...")
            self.update_idletasks()
            
            # Basic data validation
            if self.imported_data.empty:
                raise ValueError("The imported file contains no data")
            
            if len(self.imported_data.columns) < 2:
                raise ValueError("The file must contain at least two columns")
            
            # Check for completely empty columns
            empty_cols = self.imported_data.columns[self.imported_data.isna().all()].tolist()
            if empty_cols:
                messagebox.showwarning(
                    "Empty Columns Detected",
                    f"The following columns are completely empty and will be removed:\n"
                    f"{', '.join(empty_cols)}"
                )
                self.imported_data = self.imported_data.drop(columns=empty_cols)
            
            # Process file and detect PHI fields
            self.progress_var.set(75)
            self.progress_label.config(text="Analyzing fields for PHI...")
            self.update_idletasks()
            
            self.imported_data, detected_fields = self.data_processor.process_file(self.imported_data)
            
            # Show summary of detected fields
            if detected_fields:
                messagebox.showinfo(
                    "PHI Fields Detected",
                    f"Detected {len(detected_fields)} potential PHI fields.\n"
                    "Please review the field configurations in the next tab."
                )
            else:
                messagebox.showwarning(
                    "No PHI Fields Detected",
                    "No potential PHI fields were detected. Please review the data "
                    "and manually configure any fields that contain sensitive information."
                )
            
            # Complete progress
            self.progress_var.set(100)
            self.progress_label.config(text="Import complete!")
            self.update_idletasks()
            
            # Store detected fields and switch to review tab
            self.detected_fields = detected_fields
            self.after(1000, self.switch_to_review)
            
        except Exception as e:
            logger.error(f"Error importing file: {str(e)}")
            self.progress_label.config(text=f"Error: {str(e)}")
    
    def select_sheet(self, sheet_names):
        """Display dialog for sheet selection"""
        dialog = tk.Toplevel(self)
        dialog.title("Select Worksheet")
        dialog.geometry("300x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Create and pack widgets
        label = ttk.Label(dialog, text="Select worksheet to process:")
        label.pack(pady=10)
        
        # Create listbox with scrollbar
        frame = ttk.Frame(dialog)
        frame.pack(expand=True, fill="both", padx=10)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        listbox.pack(side="left", expand=True, fill="both")
        
        scrollbar.config(command=listbox.yview)
        
        # Insert sheet names
        for name in sheet_names:
            listbox.insert("end", name)
        
        # Select first sheet by default
        listbox.select_set(0)
        
        selected_sheet = [None]  # Use list to store result
        
        def on_ok():
            selection = listbox.curselection()
            if selection:
                selected_sheet[0] = sheet_names[selection[0]]
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Create buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ok_button = ttk.Button(button_frame, text="OK", command=on_ok)
        ok_button.pack(side="left", padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
        cancel_button.pack(side="left", padx=5)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return selected_sheet[0]
    
    def get_processor(self):
        """Get the data processor instance"""
        return self.data_processor
    
    def switch_to_review(self):
        """Switch to the review tab"""
        notebook = self.master
        review_tab_index = 1  # Index of review tab
        notebook.select(review_tab_index)
