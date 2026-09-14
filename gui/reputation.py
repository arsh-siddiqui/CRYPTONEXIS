import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import logging

from gui.components import create_empty_state, create_section_header
from analysis.reputation_engine import check_address
from analysis.reputation_models import ReputationStatus

logger = logging.getLogger(__name__)

class ReputationPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        
        lbl_title = ttk.Label(self, text="Reputation Intelligence", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 20))
        
        # Search Frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=X, pady=10)
        
        ttk.Label(search_frame, text="Wallet Address:", font=("Helvetica", 12)).pack(side=LEFT, padx=(0, 10))
        self.entry_addr = ttk.Entry(search_frame, width=50)
        self.entry_addr.pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(search_frame, text="Blockchain:", font=("Helvetica", 12)).pack(side=LEFT, padx=(0, 10))
        self.combo_chain = ttk.Combobox(search_frame, values=["Bitcoin", "Ethereum", "BNB Smart Chain"], state="readonly", width=20)
        self.combo_chain.pack(side=LEFT, padx=(0, 10))
        self.combo_chain.current(0)
        
        self.btn_check = ttk.Button(search_frame, text="Check Reputation", bootstyle=PRIMARY, command=self.on_check)
        self.btn_check.pack(side=LEFT)
        
        # Summary Frame
        self.summary_frame = ttk.Frame(self, bootstyle=SECONDARY)
        self.summary_frame.pack(fill=X, pady=10)
        
        # Will be populated dynamically
        self.lbl_status = ttk.Label(self.summary_frame, text="Status: PENDING", font=("Helvetica", 12, "bold"), bootstyle="inverse-secondary")
        self.lbl_status.pack(anchor=W, padx=10, pady=(10, 5))
        
        self.lbl_ransomware = ttk.Label(self.summary_frame, text="Ransomware: -", bootstyle="inverse-secondary")
        self.lbl_ransomware.pack(anchor=W, padx=10, pady=2)
        
        self.lbl_scam = ttk.Label(self.summary_frame, text="Scam / Threat Reports: -", bootstyle="inverse-secondary")
        self.lbl_scam.pack(anchor=W, padx=10, pady=2)
        
        self.lbl_mode = ttk.Label(self.summary_frame, text="Data Mode: -", font=("Helvetica", 10, "italic"), bootstyle="inverse-secondary")
        self.lbl_mode.pack(anchor=W, padx=10, pady=(2, 10))
        
        self.lbl_disclaimer = ttk.Label(self.summary_frame, text="", bootstyle="warning-inverse-secondary", wraplength=800)
        self.lbl_disclaimer.pack(anchor=W, padx=10, pady=(0, 10))
        
        # Evidence Table
        create_section_header(self, "Evidence & Results")
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        
        columns = ("Type", "Finding", "Source", "Source Type", "Date", "Confidence", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        col_widths = {
            "Type": 100,
            "Finding": 300,
            "Source": 150,
            "Source Type": 150,
            "Date": 100,
            "Confidence": 80,
            "Status": 80
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100))
            
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
    def load_address(self, address: str, blockchain: str):
        """Called by other parts of the app to pre-fill and check an address."""
        self.entry_addr.delete(0, END)
        self.entry_addr.insert(0, address)
        if blockchain in self.combo_chain["values"]:
            self.combo_chain.set(blockchain)
        self.on_check()
        
    def on_check(self):
        address = self.entry_addr.get().strip()
        blockchain = self.combo_chain.get().strip()
        
        if not address or not blockchain:
            return
            
        self.btn_check.config(state=DISABLED)
        self.lbl_status.config(text="Status: LOADING...", bootstyle="warning-inverse-secondary")
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        thread = threading.Thread(target=self._worker_check, args=(address, blockchain))
        thread.daemon = True
        thread.start()
        
    def _worker_check(self, address, blockchain):
        try:
            summary = check_address(address, blockchain)
            self.after(0, self._update_ui, summary)
        except Exception as e:
            logger.error(f"Reputation check failed: {e}")
            self.after(0, self._handle_error, str(e))
            
    def _handle_error(self, err_msg):
        self.btn_check.config(state=NORMAL)
        self.lbl_status.config(text=f"Status: ERROR - {err_msg}", bootstyle="danger-inverse-secondary")
        
    def _update_ui(self, summary):
        self.btn_check.config(state=NORMAL)
        
        # Update Summary
        status_text = summary.status.value
        style = "inverse-secondary"
        if summary.status == ReputationStatus.MATCH:
            style = "danger-inverse-secondary"
        elif summary.status == ReputationStatus.REPORTED:
            style = "warning-inverse-secondary"
        elif summary.status == ReputationStatus.NO_MATCH:
            style = "success-inverse-secondary"
            
        self.lbl_status.config(text=f"Status: {status_text}", bootstyle=style)
        
        if summary.ransomware_reports > 0:
            self.lbl_ransomware.config(text=f"Ransomware Association: Reported association ({summary.ransomware_reports})", bootstyle="danger-inverse-secondary")
        else:
            self.lbl_ransomware.config(text="Ransomware Association: No known match", bootstyle="inverse-secondary")
            
        self.lbl_scam.config(text=f"Scam / Threat Reports: {summary.other_reports}", bootstyle="warning-inverse-secondary" if summary.other_reports > 0 else "inverse-secondary")
        
        mode_text = "DEMO DATA" if summary.data_mode == "demo" else "LIVE DATA"
        self.lbl_mode.config(text=f"Data Mode: {mode_text}", bootstyle="info-inverse-secondary" if mode_text == "DEMO DATA" else "inverse-secondary")
        
        # Disclaimers
        if summary.status == ReputationStatus.NO_MATCH:
            self.lbl_disclaimer.config(text=summary.message)
        else:
            self.lbl_disclaimer.config(text="")
            
        # Update Table
        for f in summary.findings:
            self.tree.insert("", END, values=(
                f.finding_type.capitalize(),
                f.finding,
                f.source,
                f.source_type,
                f.reported_date if f.reported_date else "N/A",
                f.confidence,
                status_text
            ))
