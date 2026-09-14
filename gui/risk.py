import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import logging

from gui.components import create_empty_state, create_section_header
from analysis.correlation_engine import CorrelationEngine
from analysis.risk_engine import RiskEngine
from analysis.reputation_engine import check_address

logger = logging.getLogger(__name__)

class RiskPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        
        lbl_title = ttk.Label(self, text="Investigative Risk Analysis", font=("Helvetica", 18, "bold"))
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
        
        self.btn_check = ttk.Button(search_frame, text="Run Risk Analysis", bootstyle=PRIMARY, command=self.on_check)
        self.btn_check.pack(side=LEFT)
        
        # Dashboard Grid
        grid_frame = ttk.Frame(self)
        grid_frame.pack(fill=X, pady=10)
        
        # Score Box
        self.score_frame = ttk.Frame(grid_frame, bootstyle=SECONDARY)
        self.score_frame.pack(side=LEFT, fill=Y, padx=(0, 10), ipadx=20, ipady=10)
        
        ttk.Label(self.score_frame, text="Investigation Risk", font=("Helvetica", 14), bootstyle="inverse-secondary").pack()
        self.lbl_score = ttk.Label(self.score_frame, text="-- / 100", font=("Helvetica", 28, "bold"), bootstyle="inverse-secondary")
        self.lbl_score.pack(pady=10)
        
        self.lbl_level = ttk.Label(self.score_frame, text="Level: N/A", font=("Helvetica", 12, "bold"), bootstyle="inverse-secondary")
        self.lbl_level.pack()
        
        self.lbl_mode = ttk.Label(self.score_frame, text="Data Mode: -", font=("Helvetica", 10, "italic"), bootstyle="inverse-secondary")
        self.lbl_mode.pack(pady=(10, 0))
        
        self.lbl_meth = ttk.Label(self.score_frame, text="Methodology: v1.0", font=("Helvetica", 8), bootstyle="inverse-secondary")
        self.lbl_meth.pack(pady=(5, 0))
        
        # Factors Table
        factors_frame = ttk.Frame(grid_frame)
        factors_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        create_section_header(factors_frame, "Contributing Risk Factors")
        
        columns = ("Factor", "Score", "Evidence", "Source", "Confidence")
        self.tree = ttk.Treeview(factors_frame, columns=columns, show="headings", height=8)
        
        col_widths = {
            "Factor": 150,
            "Score": 50,
            "Evidence": 250,
            "Source": 150,
            "Confidence": 80
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100))
            
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar = ttk.Scrollbar(factors_frame, orient=VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Disclaimers
        disclaimer_frame = ttk.Frame(self)
        disclaimer_frame.pack(fill=X, pady=20)
        ttk.Label(disclaimer_frame, text="Risk score is application-generated and does not by itself establish criminal conduct.", font=("Helvetica", 10, "bold"), bootstyle="warning").pack(anchor=W)
        
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
        self.lbl_score.config(text="CALC...")
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        thread = threading.Thread(target=self._worker_check, args=(address, blockchain))
        thread.daemon = True
        thread.start()
        
    def _worker_check(self, address, blockchain):
        try:
            # 1. Fetch Reputation
            rep_summary = check_address(address, blockchain)
            
            # 2. Extract context from app state if available (e.g. Graph, Transactions)
            # For phase 8, we pull from MainWindow if it has loaded data
            graph_paths = []
            tx_data = []
            
            main_win = self.winfo_toplevel()
            if hasattr(main_win, 'pages'):
                tx_page = main_win.pages.get("Transactions")
                if tx_page and hasattr(tx_page, 'transactions'):
                    tx_data = tx_page.transactions
                    
                graph_page = main_win.pages.get("Transaction Graph")
                if graph_page and hasattr(graph_page, 'last_trace_result'):
                    res = graph_page.last_trace_result
                    if res and res.candidate_paths:
                        graph_paths = res.candidate_paths

            # 3. Correlate
            corr_engine = CorrelationEngine()
            findings = corr_engine.correlate(address, blockchain, rep_summary, graph_paths, tx_data)
            
            # 4. Score Risk
            risk_engine = RiskEngine()
            assessment = risk_engine.evaluate(findings)
            
            self.after(0, self._update_ui, assessment)
        except Exception as e:
            logger.error(f"Risk analysis failed: {e}")
            self.after(0, self._handle_error, str(e))
            
    def _handle_error(self, err_msg):
        self.btn_check.config(state=NORMAL)
        self.lbl_score.config(text="ERR")
        self.lbl_level.config(text=f"ERROR")
        
    def _update_ui(self, assessment):
        self.btn_check.config(state=NORMAL)
        
        # Update Score Box
        self.lbl_score.config(text=f"{assessment.score} / 100")
        
        level_style = "inverse-secondary"
        if assessment.level == "CRITICAL":
            level_style = "danger-inverse-secondary"
        elif assessment.level == "HIGH":
            level_style = "warning-inverse-secondary"
        elif assessment.level == "MEDIUM":
            level_style = "info-inverse-secondary"
        elif assessment.level == "LOW":
            level_style = "success-inverse-secondary"
            
        self.lbl_level.config(text=f"Level: {assessment.level}", bootstyle=level_style)
        
        mode_text = "DEMO DATA" if "demo" in assessment.data_mode.lower() else "LIVE DATA"
        self.lbl_mode.config(text=f"Data Mode: {assessment.data_mode.upper()}", bootstyle="info-inverse-secondary" if mode_text == "DEMO DATA" else "inverse-secondary")
        self.lbl_meth.config(text=f"Methodology: v{assessment.methodology_version}")
        
        # Update Table
        for f in assessment.factors:
            self.tree.insert("", END, values=(
                f.factor_id,
                f"+{f.score}",
                f.evidence,
                f.source,
                f.confidence
            ))
