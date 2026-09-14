import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.components import create_section_header, create_empty_state

class AlertsPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        
        lbl_title = ttk.Label(self, text="Alerts & Monitoring", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 20))
        
        # Monitored Wallets Section
        create_section_header(self, "Monitored Wallets")
        
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=X, pady=(0, 10))
        
        btn_add = ttk.Button(controls_frame, text="Add Wallet", bootstyle=SUCCESS)
        btn_add.pack(side=LEFT, padx=(0, 10))
        
        btn_remove = ttk.Button(controls_frame, text="Remove Wallet", bootstyle=DANGER)
        btn_remove.pack(side=LEFT, padx=(0, 10))
        
        btn_refresh = ttk.Button(controls_frame, text="Refresh", bootstyle=INFO)
        btn_refresh.pack(side=LEFT)
        
        monitored_frame = ttk.Frame(self, bootstyle=SECONDARY)
        monitored_frame.pack(fill=X, pady=10)
        
        cols_monitored = ("Wallet", "Blockchain", "Status", "Last Activity", "Monitoring Started")
        tree_monitored = ttk.Treeview(monitored_frame, columns=cols_monitored, show="headings", height=5)
        for col in cols_monitored:
            tree_monitored.heading(col, text=col)
            tree_monitored.column(col, width=150)
        tree_monitored.pack(side=LEFT, fill=X, expand=True)
        
        # Recent Alerts Section
        create_section_header(self, "Recent Alerts")
        
        # Severity legend
        legend_frame = ttk.Frame(self)
        legend_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(legend_frame, text="INFO", bootstyle="inverse-info", padding=5).pack(side=LEFT, padx=5)
        ttk.Label(legend_frame, text="LOW", bootstyle="inverse-success", padding=5).pack(side=LEFT, padx=5)
        ttk.Label(legend_frame, text="MEDIUM", bootstyle="inverse-warning", padding=5).pack(side=LEFT, padx=5)
        ttk.Label(legend_frame, text="HIGH", bootstyle="inverse-danger", padding=5).pack(side=LEFT, padx=5)
        ttk.Label(legend_frame, text="CRITICAL", bootstyle="inverse-dark", padding=5).pack(side=LEFT, padx=5)
        
        alerts_frame = ttk.Frame(self, bootstyle=SECONDARY)
        alerts_frame.pack(fill=BOTH, expand=True, pady=10)
        
        cols_alerts = ("Time", "Wallet", "Blockchain", "Event", "Severity", "Status")
        tree_alerts = ttk.Treeview(alerts_frame, columns=cols_alerts, show="headings", height=10)
        for col in cols_alerts:
            tree_alerts.heading(col, text=col)
            tree_alerts.column(col, width=120)
        tree_alerts.pack(side=LEFT, fill=BOTH, expand=True)
        
        create_empty_state(self, "No active monitoring configured.")
