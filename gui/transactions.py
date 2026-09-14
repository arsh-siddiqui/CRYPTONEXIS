import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.components import create_empty_state

class TransactionsPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        
        lbl_title = ttk.Label(self, text="Transactions", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 20))
        
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=X, pady=10)
        
        self.entry_search = ttk.Entry(controls_frame, width=40)
        self.entry_search.pack(side=LEFT, padx=(0, 10))
        self.entry_search.insert(0, "Search...")
        
        btn_filter = ttk.Button(controls_frame, text="Filters", bootstyle=SECONDARY)
        btn_filter.pack(side=LEFT, padx=(0, 10))
        
        lbl_chain = ttk.Label(controls_frame, text="Blockchain: N/A", font=("Helvetica", 10, "italic"))
        lbl_chain.pack(side=RIGHT, padx=10)
        
        # Table Frame
        table_frame = ttk.Frame(self, bootstyle=SECONDARY)
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Columns
        columns = ("Hash", "Chain", "From", "To", "Amount", "Asset", "Time", "Direction", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        self.tree.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y, pady=10, padx=(0, 10))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        create_empty_state(self, "No transaction data loaded.")
