import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.components import create_card, create_empty_state, create_section_header

class ReputationPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        
        lbl_title = ttk.Label(self, text="Reputation Intelligence", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 20))
        
        # Search Frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=X, pady=10)
        
        lbl_addr = ttk.Label(search_frame, text="Wallet Address:", font=("Helvetica", 12))
        lbl_addr.pack(side=LEFT, padx=(0, 10))
        
        self.entry_addr = ttk.Entry(search_frame, width=50)
        self.entry_addr.pack(side=LEFT, padx=(0, 10))
        
        btn_check = ttk.Button(search_frame, text="Check Reputation", bootstyle=PRIMARY)
        btn_check.pack(side=LEFT)
        
        # Summary Cards
        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill=X, pady=10)
        
        create_card(cards_frame, "Ransomware Association", "None", bootstyle=SUCCESS)
        create_card(cards_frame, "Scam Reports", "0", bootstyle=SUCCESS)
        create_card(cards_frame, "Threat Intelligence", "Clean", bootstyle=SUCCESS)
        create_card(cards_frame, "Risk Indicator", "Low", bootstyle=SUCCESS)
        
        # Evidence Table
        create_section_header(self, "Evidence & Results")
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        
        columns = ("Source", "Finding", "Status", "Date", "Confidence")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
            
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empty state message
        msg_frame = ttk.Frame(self)
        msg_frame.pack(fill=X, pady=10)
        create_empty_state(msg_frame, "No reputation findings loaded.")
