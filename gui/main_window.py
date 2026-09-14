import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.dashboard import DashboardPage
from gui.investigation import InvestigationPage
from gui.transactions import TransactionsPage
from gui.graph_view import GraphPage
from gui.reputation import ReputationPage
from gui.risk import RiskPage
from gui.alerts import AlertsPage
from gui.reports import ReportsPage
from gui.settings import SettingsPage

class MainWindow(ttk.Window):
    def __init__(self, config):
        super().__init__(themename="darkly")
        self.config = config
        self.title("CRYPTONEXIS - Trace. Correlate. Investigate.")
        self.geometry("1200x800")
        
        self.pages = {}
        self.current_page = None
        self.nav_buttons = {}

        self._build_header()
        self._build_layout()
        
        self.show_page("Dashboard")

    def _build_header(self):
        header_frame = ttk.Frame(self, bootstyle=DARK)
        header_frame.pack(side=TOP, fill=X)
        
        left_frame = ttk.Frame(header_frame, bootstyle=DARK)
        left_frame.pack(side=LEFT, padx=20, pady=10)
        
        title = ttk.Label(left_frame, text="CRYPTONEXIS", font=("Helvetica", 20, "bold"), bootstyle="inverse-dark")
        title.pack(anchor=W)
        
        subtitle = ttk.Label(left_frame, text="Trace. Correlate. Investigate.", font=("Helvetica", 10, "italic"), bootstyle="inverse-dark")
        subtitle.pack(anchor=W)
        
        right_frame = ttk.Frame(header_frame, bootstyle=DARK)
        right_frame.pack(side=RIGHT, padx=20, pady=10)
        
        mode = self.config.get("DATA_MODE", "demo").upper() + " MODE"
        mode_style = SUCCESS if mode == "LIVE MODE" else WARNING
        
        status_lbl = ttk.Label(right_frame, text=mode, font=("Helvetica", 12, "bold"), bootstyle=mode_style)
        status_lbl.pack(anchor=E, pady=10)

    def _build_layout(self):
        body_frame = ttk.Frame(self)
        body_frame.pack(side=TOP, fill=BOTH, expand=True)
        
        # Sidebar
        sidebar = ttk.Frame(body_frame, bootstyle=SECONDARY, width=200)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False) # keep width
        
        # Main Content
        self.content_area = ttk.Frame(body_frame)
        self.content_area.pack(side=LEFT, fill=BOTH, expand=True, padx=20, pady=20)
        
        # Navigation Items
        nav_items = [
            ("Dashboard", DashboardPage),
            ("New Investigation", InvestigationPage),
            ("Transactions", TransactionsPage),
            ("Transaction Graph", GraphPage),
            ("Reputation", ReputationPage),
            ("Risk Analysis", RiskPage),
            ("Alerts", AlertsPage),
            ("Reports", ReportsPage),
            ("Settings", SettingsPage)
        ]
        
        for name, page_class in nav_items:
            btn = ttk.Button(sidebar, text=name, bootstyle="outline-secondary", 
                             command=lambda n=name: self.show_page(n))
            btn.pack(side=TOP, fill=X, padx=10, pady=5)
            self.nav_buttons[name] = btn
            
            # Initialize page
            page_frame = page_class(self.content_area, self.config)
            self.pages[name] = page_frame
            
    def show_page(self, name):
        if self.current_page:
            self.pages[self.current_page].pack_forget()
            self.nav_buttons[self.current_page].configure(bootstyle="outline-secondary")
            
        self.pages[name].pack(fill=BOTH, expand=True)
        self.nav_buttons[name].configure(bootstyle="secondary")
        self.current_page = name

    def load_transactions(self, data, blockchain, address):
        """Coordinates passing data to the Transactions page and Graph page."""
        tx_page = self.pages.get("Transactions")
        if tx_page:
            tx_page.load_transactions(data, blockchain, address)
            
        graph_page = self.pages.get("Transaction Graph")
        if graph_page:
            graph_page.load_transactions(data)
            
def launch_gui(config):
    app = MainWindow(config)
    app.mainloop()
