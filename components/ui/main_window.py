import tkinter as tk
from tkinter import ttk
import logging

from .import_tab import ImportTab
from .review_tab import ReviewTab
from .preview_tab import PreviewTab
from .help_component import HelpComponent

logger = logging.getLogger('phi_cleanse')

class MainWindow:
    def __init__(self, parent):
        self.parent = parent
        
        # Add help component
        self.help_component = HelpComponent(parent)
        self.help_component.pack(anchor="ne", padx=5, pady=5)
        
        # Create main tab control
        self.tab_control = ttk.Notebook(parent)
        
        # Create tabs
        self.import_tab = ImportTab(self.tab_control)
        self.review_tab = ReviewTab(self.tab_control)
        self.preview_tab = PreviewTab(self.tab_control)
        
        # Add tabs to notebook
        self.tab_control.add(self.import_tab, text='Import File')
        self.tab_control.add(self.review_tab, text='Review & Configure')
        self.tab_control.add(self.preview_tab, text='Preview & Export')
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Bind tab change event
        self.tab_control.bind('<<NotebookTabChanged>>', self.on_tab_change)
    
    def on_tab_change(self, event):
        """Handle tab change events"""
        current_tab = self.tab_control.select()
        tab_name = self.tab_control.tab(current_tab, "text")
        logger.info(f"Switched to tab: {tab_name}")
        
        # Update tab content based on current state
        if tab_name == 'Review & Configure' and hasattr(self.import_tab, 'imported_data'):
            self.review_tab.update_content(self.import_tab.imported_data)
        elif tab_name == 'Preview & Export' and hasattr(self.review_tab, 'configured_data'):
            self.preview_tab.update_content(self.review_tab.configured_data)
