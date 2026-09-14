import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.components import create_empty_state

class ReportsPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        
        lbl_title = ttk.Label(self, text="Investigation Reports", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 20))
        
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=X, pady=10)
        
        btn_view = ttk.Button(controls_frame, text="View", bootstyle=INFO)
        btn_view.pack(side=LEFT, padx=(0, 10))
        
        btn_json = ttk.Button(controls_frame, text="Export JSON", bootstyle=SECONDARY)
        btn_json.pack(side=LEFT, padx=(0, 10))
        
        btn_pdf = ttk.Button(controls_frame, text="Export PDF", bootstyle=PRIMARY)
        btn_pdf.pack(side=LEFT)
        
        table_frame = ttk.Frame(self, bootstyle=SECONDARY)
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        
        cols = ("Case ID", "Wallet", "Blockchain", "Created", "Risk", "Status", "Report availability")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        create_empty_state(self, "No investigation cases available.")
