import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class SettingsPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        
        lbl_title = ttk.Label(self, text="Settings & Configuration", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 20))
        
        # Application Mode
        mode_frame = ttk.LabelFrame(self, text="Application Mode", padding=20)
        mode_frame.pack(fill=X, pady=10)
        
        self.mode_var = tk.StringVar(value="Demo")
        if self.config.get("DATA_MODE", "").lower() == "live":
            self.mode_var.set("Live")
            
        ttk.Radiobutton(mode_frame, text="Demo (Safe synthetic data)", variable=self.mode_var, value="Demo").pack(anchor=W, pady=5)
        ttk.Radiobutton(mode_frame, text="Live (Real blockchain APIs)", variable=self.mode_var, value="Live").pack(anchor=W, pady=5)
        
        # API Status
        api_frame = ttk.LabelFrame(self, text="Blockchain API Status", padding=20)
        api_frame.pack(fill=X, pady=10)
        
        apis = [
            ("Bitcoin (Blockchain.com)", "BLOCKCHAIN_API_KEY"),
            ("Ethereum (Etherscan V2)", "ETHERSCAN_API_KEY"),
            ("BNB Smart Chain (BscScan)", "BSCSCAN_API_KEY")
        ]
        
        import os
        for name, env_key in apis:
            row = ttk.Frame(api_frame)
            row.pack(fill=X, pady=5)
            
            ttk.Label(row, text=name, width=30).pack(side=LEFT)
            
            status = "Configured" if os.getenv(env_key) else "Not Configured"
            color = SUCCESS if status == "Configured" else WARNING
            ttk.Label(row, text=status, bootstyle=color, font=("Helvetica", 10, "bold")).pack(side=LEFT)
