import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def create_card(parent, title, value, bootstyle=PRIMARY):
    """Creates a metric card."""
    frame = ttk.Frame(parent, bootstyle=SECONDARY)
    frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
    
    lbl_title = ttk.Label(frame, text=title, font=("Helvetica", 10), bootstyle="inverse-secondary")
    lbl_title.pack(anchor=NW, padx=10, pady=(10, 0))
    
    lbl_value = ttk.Label(frame, text=value, font=("Helvetica", 18, "bold"), bootstyle=f"inverse-secondary")
    lbl_value.pack(anchor=NW, padx=10, pady=(0, 10))
    
    return frame

def create_empty_state(parent, message):
    """Creates a standard empty state placeholder."""
    frame = ttk.Frame(parent)
    frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
    lbl = ttk.Label(frame, text=message, font=("Helvetica", 12, "italic"), justify=CENTER)
    lbl.pack(expand=True)
    return frame

def create_section_header(parent, title):
    """Creates a consistent section header."""
    lbl = ttk.Label(parent, text=title, font=("Helvetica", 14, "bold"))
    lbl.pack(anchor=NW, pady=(20, 10))
    return lbl
