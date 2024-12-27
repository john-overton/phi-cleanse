import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.logger import setup_logger
from components.ui.main_window import MainWindow

# Setup logging
logger = setup_logger()

class PHICleanseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PHI Cleanse Tool")
        self.root.geometry("900x700")
        
        # Set window icon
        try:
            # Get the base path for resources
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                base_path = sys._MEIPASS
            else:
                # Running in development
                base_path = os.path.abspath(os.path.dirname(__file__))
            
            icon_path = os.path.join(base_path, 'content', 'jo-dark-icon.png')
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon)
        except Exception as e:
            logger.error(f"Error loading application icon: {str(e)}")
        
        # Create main frame to hold everything
        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True)
        
        # Create top frame for help button
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x")
        
        # Create main window with tabs
        self.main_window = MainWindow(main_frame)
        
        # Create bottom frame for version and close button
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", pady=(0, 5))
        
        # Add close button to bottom right
        self.close_button = ttk.Button(bottom_frame, text="Close", command=root.destroy)
        self.close_button.pack(side="right", padx=10)

def main():
    root = tk.Tk()
    app = PHICleanseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
