import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import logging

from gui.components import create_section_header
from services.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)

class AlertsPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.monitoring_service = MonitoringService(config)
        
        lbl_title = ttk.Label(self, text="Real-Time Wallet Monitoring", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 20))
        
        # Upper Split: Watchlist vs Global Controls
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=X, pady=10)
        
        # 1. Watchlist Add Section
        add_frame = ttk.LabelFrame(top_frame, text="Add Monitored Wallet", bootstyle=INFO)
        add_frame.pack(side=LEFT, fill=Y, padx=(0, 20), ipadx=10, ipady=10)
        
        ttk.Label(add_frame, text="Address:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.entry_addr = ttk.Entry(add_frame, width=40)
        self.entry_addr.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Blockchain:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.combo_chain = ttk.Combobox(add_frame, values=["Bitcoin", "Ethereum", "BNB Smart Chain"], state="readonly")
        self.combo_chain.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        self.combo_chain.current(0)
        
        ttk.Label(add_frame, text="Label:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.entry_label = ttk.Entry(add_frame, width=40)
        self.entry_label.grid(row=2, column=1, padx=5, pady=5)
        
        self.btn_add = ttk.Button(add_frame, text="Add Wallet", bootstyle=PRIMARY, command=self.on_add_wallet)
        self.btn_add.grid(row=3, column=0, columnspan=2, pady=(10,0))
        
        # 2. Global Controls
        control_frame = ttk.LabelFrame(top_frame, text="Monitoring Engine", bootstyle=SECONDARY)
        control_frame.pack(side=LEFT, fill=Y, ipadx=10, ipady=10)
        
        self.lbl_engine_status = ttk.Label(control_frame, text="Status: STOPPED", font=("Helvetica", 12, "bold"), bootstyle=DANGER)
        self.lbl_engine_status.pack(pady=(0, 10))
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack()
        
        self.btn_start = ttk.Button(btn_frame, text="Start Monitoring", bootstyle=SUCCESS, command=self.on_start_monitoring)
        self.btn_start.pack(side=LEFT, padx=5)
        
        self.btn_stop = ttk.Button(btn_frame, text="Stop Monitoring", bootstyle=DANGER, state=DISABLED, command=self.on_stop_monitoring)
        self.btn_stop.pack(side=LEFT, padx=5)
        
        self.btn_refresh = ttk.Button(btn_frame, text="Refresh Data", bootstyle=SECONDARY, command=self.refresh_all)
        self.btn_refresh.pack(side=LEFT, padx=5)
        
        # 3. Watchlist Table
        create_section_header(self, "Monitored Wallets (Watchlist)")
        wl_frame = ttk.Frame(self)
        wl_frame.pack(fill=X, pady=5)
        
        wl_cols = ("ID", "Address", "Blockchain", "Label", "Status", "Last Checked")
        self.tree_wl = ttk.Treeview(wl_frame, columns=wl_cols, show="headings", height=5)
        
        for col in wl_cols:
            self.tree_wl.heading(col, text=col)
            self.tree_wl.column(col, width=150 if col != "ID" else 50)
            
        self.tree_wl.pack(side=LEFT, fill=X, expand=True)
        wl_scroll = ttk.Scrollbar(wl_frame, orient=VERTICAL, command=self.tree_wl.yview)
        wl_scroll.pack(side=RIGHT, fill=Y)
        self.tree_wl.configure(yscrollcommand=wl_scroll.set)
        
        # Watchlist Actions
        wl_actions = ttk.Frame(self)
        wl_actions.pack(fill=X, pady=(0, 20))
        
        ttk.Button(wl_actions, text="Toggle Enabled", bootstyle=SECONDARY, command=self.on_toggle_wallet).pack(side=LEFT, padx=(0, 5))
        ttk.Button(wl_actions, text="Remove Wallet", bootstyle=DANGER, command=self.on_remove_wallet).pack(side=LEFT, padx=(0, 5))
        ttk.Button(wl_actions, text="Simulate Demo Tx", bootstyle=WARNING, command=self.on_simulate).pack(side=LEFT, padx=(0, 5))
        
        # 4. Alerts Table
        create_section_header(self, "Generated Alerts")
        alerts_frame = ttk.Frame(self)
        alerts_frame.pack(fill=BOTH, expand=True, pady=5)
        
        al_cols = ("ID", "Time", "Severity", "Blockchain", "Wallet", "Direction", "Amount", "Message")
        self.tree_al = ttk.Treeview(alerts_frame, columns=al_cols, show="headings", height=10)
        
        for col in al_cols:
            self.tree_al.heading(col, text=col)
            self.tree_al.column(col, width=100)
            
        self.tree_al.column("Message", width=300)
        self.tree_al.column("Wallet", width=200)
            
        self.tree_al.pack(side=LEFT, fill=BOTH, expand=True)
        al_scroll = ttk.Scrollbar(alerts_frame, orient=VERTICAL, command=self.tree_al.yview)
        al_scroll.pack(side=RIGHT, fill=Y)
        self.tree_al.configure(yscrollcommand=al_scroll.set)
        
        # Start automatic UI refresh loop
        self._ui_refresh_loop()
        
    def _ui_refresh_loop(self):
        """Periodically refreshes the tables without freezing UI."""
        self.refresh_all()
        self.after(5000, self._ui_refresh_loop)
        
    def refresh_all(self):
        # Refresh Watchlist
        for item in self.tree_wl.get_children():
            self.tree_wl.delete(item)
            
        wallets = self.monitoring_service.list_wallets()
        for w in wallets:
            status = "ENABLED" if w.enabled else "DISABLED"
            self.tree_wl.insert("", END, values=(w.id, w.wallet_address, w.blockchain, w.label, status, w.last_checked_at or "Never"))
            
        # Refresh Alerts
        for item in self.tree_al.get_children():
            self.tree_al.delete(item)
            
        alerts = self.monitoring_service.get_alerts()
        for a in alerts:
            self.tree_al.insert("", END, values=(
                a.id, 
                a.detected_at, 
                a.severity, 
                a.blockchain, 
                a.wallet_address, 
                a.direction, 
                a.amount, 
                a.message
            ))
            
    def on_add_wallet(self):
        addr = self.entry_addr.get().strip()
        chain = self.combo_chain.get().strip()
        label = self.entry_label.get().strip()
        
        if not addr:
            return
            
        self.btn_add.config(state=DISABLED, text="Adding (Baselining)...")
        
        # Run in thread so baseline API calls don't freeze UI
        def _add():
            try:
                self.monitoring_service.add_wallet(addr, chain, label)
            except Exception as e:
                logger.error(f"Failed to add wallet: {e}")
            finally:
                self.after(0, lambda: self.btn_add.config(state=NORMAL, text="Add Wallet"))
                self.after(0, lambda: self.entry_addr.delete(0, END))
                self.after(0, lambda: self.entry_label.delete(0, END))
                self.after(0, self.refresh_all)
                
        t = threading.Thread(target=_add)
        t.daemon = True
        t.start()
        
    def on_toggle_wallet(self):
        selected = self.tree_wl.selection()
        if not selected:
            return
        item = self.tree_wl.item(selected[0])
        w_id = item['values'][0]
        w_status = item['values'][4]
        
        new_status = False if w_status == "ENABLED" else True
        self.monitoring_service.toggle_wallet(w_id, new_status)
        self.refresh_all()
        
    def on_remove_wallet(self):
        selected = self.tree_wl.selection()
        if not selected:
            return
        item = self.tree_wl.item(selected[0])
        w_id = item['values'][0]
        
        self.monitoring_service.remove_wallet(w_id)
        self.refresh_all()
        
    def on_simulate(self):
        selected = self.tree_wl.selection()
        if not selected:
            return
        item = self.tree_wl.item(selected[0])
        w_id = item['values'][0]
        
        # Simulate in thread
        def _sim():
            self.monitoring_service.simulate_demo_transaction(w_id)
            self.after(0, self.refresh_all)
            
        t = threading.Thread(target=_sim)
        t.daemon = True
        t.start()
        
    def on_start_monitoring(self):
        self.monitoring_service.start_monitoring()
        self.btn_start.config(state=DISABLED)
        self.btn_stop.config(state=NORMAL)
        self.lbl_engine_status.config(text="Status: ACTIVE", bootstyle=SUCCESS)
        
    def on_stop_monitoring(self):
        self.monitoring_service.stop_monitoring()
        self.btn_start.config(state=NORMAL)
        self.btn_stop.config(state=DISABLED)
        self.lbl_engine_status.config(text="Status: STOPPED", bootstyle=DANGER)
