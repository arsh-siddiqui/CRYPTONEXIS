import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.components import create_card, create_empty_state, create_section_header
from services.case_service import CaseService
import threading

class DashboardPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.case_service = CaseService()
        
        lbl_title = ttk.Label(self, text="Dashboard", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 20))
        
        # Summary Cards
        self.cards_frame = ttk.Frame(self)
        self.cards_frame.pack(fill=X, pady=10)
        
        self.val_cases = tk.StringVar(value="0")
        self.val_evidence = tk.StringVar(value="0")
        self.val_monitored = tk.StringVar(value="0")
        self.val_alerts = tk.StringVar(value="0")
        
        create_card(self.cards_frame, "Active Cases", self.val_cases)
        create_card(self.cards_frame, "Evidence Items", self.val_evidence, bootstyle=INFO)
        create_card(self.cards_frame, "Monitored Wallets", self.val_monitored, bootstyle=WARNING)
        create_card(self.cards_frame, "Open Alerts", self.val_alerts, bootstyle=DANGER)
        
        # Recent Investigations
        create_section_header(self, "Recent Investigations")
        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill=X, expand=True)
        
        cols = ("Case #", "Title", "Status", "Updated")
        self.tree_cases = ttk.Treeview(self.table_frame, columns=cols, show="headings", height=5)
        for col in cols:
            self.tree_cases.heading(col, text=col)
        self.tree_cases.pack(fill=BOTH, expand=True)
        
        # Load stats
        self._load_stats()
        
    def _load_stats(self):
        def run():
            cases = self.case_service.list_cases()
            self.val_cases.set(str(len([c for c in cases if c.status != "CLOSED"])))
            
            ev_count = 0
            for c in cases:
                if c.evidence: ev_count += len(c.evidence)
            self.val_evidence.set(str(ev_count))
            
            for item in self.tree_cases.get_children():
                self.tree_cases.delete(item)
            for c in cases[:5]:
                self.tree_cases.insert("", tk.END, values=(c.case_number, c.title, c.status, c.updated_at[:10]))
                
        threading.Thread(target=run, daemon=True).start()
