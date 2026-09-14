import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.components import create_section_header
from analysis.crypto_detector import detect_and_validate

class InvestigationPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        
        lbl_title = ttk.Label(self, text="New Investigation", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 20))
        
        desc = ttk.Label(self, text="Enter a wallet address or transaction identifier to begin an investigation.", font=("Helvetica", 12))
        desc.pack(anchor=NW, pady=(0, 20))
        
        form_frame = ttk.Frame(self, bootstyle=SECONDARY)
        form_frame.pack(fill=X, pady=10, padx=10)
        
        # Address Input
        lbl_addr = ttk.Label(form_frame, text="Wallet Address / Transaction Hash", font=("Helvetica", 10, "bold"), bootstyle="inverse-secondary")
        lbl_addr.pack(anchor=NW, padx=20, pady=(20, 5))
        
        self.entry_addr = ttk.Entry(form_frame, width=60)
        self.entry_addr.pack(anchor=NW, padx=20, pady=5)
        
        # Blockchain Select
        lbl_chain = ttk.Label(form_frame, text="Blockchain", font=("Helvetica", 10, "bold"), bootstyle="inverse-secondary")
        lbl_chain.pack(anchor=NW, padx=20, pady=(15, 5))
        
        self.chain_var = tk.StringVar(value="Auto Detect")
        chains = ["Auto Detect", "Bitcoin", "Ethereum", "BNB Smart Chain"]
        self.combo_chain = ttk.Combobox(form_frame, textvariable=self.chain_var, values=chains, state="readonly", width=30)
        self.combo_chain.pack(anchor=NW, padx=20, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame, bootstyle=SECONDARY)
        btn_frame.pack(anchor=NW, fill=X, padx=20, pady=30)
        
        btn_validate = ttk.Button(btn_frame, text="Validate", bootstyle=INFO, command=self.run_validation)
        btn_validate.pack(side=LEFT, padx=(0, 10))
        
        btn_start = ttk.Button(btn_frame, text="Start Investigation", bootstyle=PRIMARY, command=self.placeholder_start)
        btn_start.pack(side=LEFT)
        
        # Result Panel (Hidden by default, shown upon validation)
        self.result_frame = ttk.Frame(self, bootstyle=DARK)
        self.result_frame.pack(fill=X, pady=10, padx=10)
        self.result_frame.pack_forget() # Hide initially
        
        create_section_header(self.result_frame, "Address Validation")
        
        self.lbl_status = ttk.Label(self.result_frame, text="Status: ", font=("Helvetica", 12, "bold"))
        self.lbl_status.pack(anchor=NW, padx=20, pady=2)
        
        self.lbl_type = ttk.Label(self.result_frame, text="Type: ", font=("Helvetica", 12))
        self.lbl_type.pack(anchor=NW, padx=20, pady=2)
        
        self.lbl_networks = ttk.Label(self.result_frame, text="", font=("Helvetica", 12))
        self.lbl_networks.pack(anchor=NW, padx=20, pady=2)
        
        self.lbl_confidence = ttk.Label(self.result_frame, text="Confidence: ", font=("Helvetica", 12))
        self.lbl_confidence.pack(anchor=NW, padx=20, pady=2)
        
        self.lbl_message = ttk.Label(self.result_frame, text="Message: ", font=("Helvetica", 12))
        self.lbl_message.pack(anchor=NW, padx=20, pady=(2, 20))
        
        self.lbl_start_msg = ttk.Label(self, text="", font=("Helvetica", 10, "italic"), bootstyle="warning")
        self.lbl_start_msg.pack(anchor=NW, padx=20, pady=10)
        
    def run_validation(self):
        address = self.entry_addr.get()
        chain = self.chain_var.get()
        
        result = detect_and_validate(address, chain)
        
        # Display the result frame
        self.result_frame.pack(fill=X, pady=10, padx=10)
        self.lbl_start_msg.config(text="") # Clear start message
        
        if result["valid"]:
            self.lbl_status.config(text="Status: VALID", bootstyle=SUCCESS)
            self.lbl_type.config(text=f"Type: {result['detected_type']}")
            
            if "possible_chains" in result and len(result["possible_chains"]) > 1:
                self.lbl_networks.config(text=f"Possible Networks: {' / '.join(result['possible_chains'])}")
                self.lbl_networks.pack(anchor=NW, padx=20, pady=2)
            else:
                self.lbl_networks.pack_forget()
                
            self.lbl_confidence.config(text=f"Confidence: {result['confidence']}")
            self.lbl_message.config(text=f"Message: {result['reason']}")
        else:
            self.lbl_status.config(text="Status: INVALID", bootstyle=DANGER)
            self.lbl_type.config(text="")
            self.lbl_networks.pack_forget()
            self.lbl_confidence.config(text="")
            self.lbl_message.config(text=f"Reason: {result['reason']}")
            
    def placeholder_start(self):
        self.lbl_start_msg.config(text="Backend functionality will be connected in a later phase.")
