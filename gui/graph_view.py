import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.components import create_empty_state

class GraphPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        
        lbl_title = ttk.Label(self, text="Transaction Graph", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 20))
        
        # Controls Frame
        controls_frame = ttk.Frame(self, bootstyle=SECONDARY)
        controls_frame.pack(fill=X, pady=10)
        
        fields = [("Source Wallet:", 25), ("Target Wallet:", 25), ("Max Hops:", 10), ("Min Amount:", 15)]
        
        for text, width in fields:
            lbl = ttk.Label(controls_frame, text=text, bootstyle="inverse-secondary")
            lbl.pack(side=LEFT, padx=(10, 5), pady=10)
            entry = ttk.Entry(controls_frame, width=width)
            entry.pack(side=LEFT, padx=(0, 10), pady=10)
            
        btn_trace = ttk.Button(controls_frame, text="Trace", bootstyle=PRIMARY)
        btn_trace.pack(side=LEFT, padx=(10, 5), pady=10)
        
        btn_reset = ttk.Button(controls_frame, text="Reset", bootstyle=SECONDARY)
        btn_reset.pack(side=LEFT, padx=5, pady=10)
        
        # Graph Area
        graph_frame = ttk.Frame(self, bootstyle=DARK)
        graph_frame.pack(fill=BOTH, expand=True, pady=10)
        
        create_empty_state(graph_frame, "Transaction graph will appear here after blockchain data is loaded.")
