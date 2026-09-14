import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.components import create_card, create_empty_state, create_section_header

class DashboardPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        
        lbl_title = ttk.Label(self, text="Dashboard", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 20))
        
        # Summary Cards
        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill=X, pady=10)
        
        create_card(cards_frame, "Active Cases", "0")
        create_card(cards_frame, "Investigated Wallets", "0")
        create_card(cards_frame, "High-Risk Addresses", "0", bootstyle=DANGER)
        create_card(cards_frame, "Monitored Wallets", "0", bootstyle=INFO)
        create_card(cards_frame, "Recent Alerts", "0", bootstyle=WARNING)
        
        # Recent Investigations
        create_section_header(self, "Recent Investigations")
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=X, expand=True)
        create_empty_state(table_frame, "No recent investigations found.")
        
        # Recent Alerts
        create_section_header(self, "Recent Alerts")
        alerts_frame = ttk.Frame(self)
        alerts_frame.pack(fill=X, expand=True)
        create_empty_state(alerts_frame, "No alerts yet.")
