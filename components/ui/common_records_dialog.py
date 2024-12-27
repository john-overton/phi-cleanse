import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger('phi_cleanse')

class CommonRecordsDialog:
    """Dialog for configuring common record groups"""
    
    def __init__(self, parent, columns, detected_fields, current_groups=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Common Record Settings")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.columns = columns
        self.detected_fields = detected_fields
        self.current_groups = current_groups or {}
        self.group_vars = {}
        self.result = None
        
        self.setup_ui()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Instructions
        ttk.Label(
            self.dialog,
            text="Group fields that should maintain consistent values across records.\n" +
                 "Fields in the same group will be treated as related identifiers.",
            wraplength=450
        ).pack(fill="x", padx=10, pady=5)
        
        # Frame for groups
        groups_frame = ttk.Frame(self.dialog)
        groups_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollable canvas for groups
        canvas = tk.Canvas(groups_frame)
        scrollbar = ttk.Scrollbar(groups_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add initial group or restore existing groups
        if self.current_groups:
            for group_id, fields in self.current_groups.items():
                self.add_group(group_id, fields)
        else:
            self.add_group()
        
        # Add Group button
        ttk.Button(self.dialog, text="Add Group", command=lambda: self.add_group()).pack(pady=5)
        
        # Bottom buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side="right")
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.dialog.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))
    
    def add_group(self, group_id=None, selected_fields=None):
        """Add a new group of related fields"""
        if group_id is None:
            group_id = f"group_{len(self.group_vars) + 1}"
            
        group_frame = ttk.LabelFrame(self.scrollable_frame, text=f"Record Group {len(self.group_vars) + 1}")
        group_frame.pack(fill="x", padx=5, pady=5)
        
        # Add checkboxes for each field
        field_vars = {}
        for col in self.columns:
            var = tk.BooleanVar(value=selected_fields and col in selected_fields)
            field_vars[col] = var
            
            if col in self.detected_fields:
                detection = self.detected_fields[col]
                checkbox_text = f"{col} (PHI: {detection['field_type']})"
                checkbox = ttk.Checkbutton(
                    group_frame,
                    text=checkbox_text,
                    variable=var,
                    style='PHI.TCheckbutton'
                )
            else:
                checkbox = ttk.Checkbutton(
                    group_frame,
                    text=col,
                    variable=var
                )
            checkbox.pack(anchor="w", padx=5)
        
        self.group_vars[group_id] = field_vars
        
        # Add remove button
        ttk.Button(
            group_frame,
            text="Remove Group",
            command=lambda f=group_frame, g=group_id: self.remove_group(f, g)
        ).pack(anchor="e", padx=5, pady=5)
    
    def remove_group(self, frame, group_id):
        """Remove a group"""
        frame.destroy()
        if group_id in self.group_vars:
            del self.group_vars[group_id]
    
    def on_ok(self):
        """Save group configuration"""
        # Convert group settings to format for data processor
        common_records = {}
        for group_id, fields in self.group_vars.items():
            group_fields = []
            for field, var in fields.items():
                if var.get():
                    group_fields.append(field)
            if group_fields:
                common_records[group_id] = group_fields
        
        self.result = common_records
        self.dialog.destroy()
        
        logger.info(f"Updated common record groups: {common_records}")
    
    def on_cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()
    
    def show(self):
        """Show dialog and return result"""
        self.dialog.wait_window()
        return self.result
