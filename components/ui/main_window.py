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
        
        # Create top frame for help component
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill="x", padx=5)
        
        # Add help component to top right
        self.help_component = HelpComponent(top_frame)
        self.help_component.pack(side="right")
        
        # Create main tab control
        self.tab_control = ttk.Notebook(parent)
        self.tab_control.pack(fill="both", expand=True, padx=5)
        
        # Create tabs
        self.import_tab = ImportTab(self.tab_control)
        self.review_tab = ReviewTab(self.tab_control)
        self.preview_tab = PreviewTab(self.tab_control)
        
        # Add tabs to notebook
        self.tab_control.add(self.import_tab, text='Import File')
        self.tab_control.add(self.review_tab, text='Review & Configure')
        self.tab_control.add(self.preview_tab, text='Preview & Export')
        
        # Bind tab change event
        self.tab_control.bind('<<NotebookTabChanged>>', self.on_tab_change)
    
    def on_tab_change(self, event):
        """Handle tab change events"""
        current_tab = self.tab_control.select()
        tab_name = self.tab_control.tab(current_tab, "text")
        logger.info(f"Switched to tab: {tab_name}")
        
        # Update preview tab content when switching to it
        if tab_name == 'Preview & Export' and hasattr(self.review_tab, 'configured_data'):
            self.preview_tab.update_content(self.review_tab.configured_data)
