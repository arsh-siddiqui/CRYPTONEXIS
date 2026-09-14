import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.components import create_section_header
from analysis.crypto_detector import detect_and_validate
import threading
import logging

from services.bitcoin_service import BitcoinService
from services.ethereum_service import EthereumService
from services.bsc_service import BscService

logger = logging.getLogger(__name__)

class InvestigationPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.parent = parent
        
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
        
        self.btn_validate = ttk.Button(btn_frame, text="Validate", bootstyle=INFO, command=self.run_validation)
        self.btn_validate.pack(side=LEFT, padx=(0, 10))
        
        self.btn_start = ttk.Button(btn_frame, text="Start Investigation", bootstyle=PRIMARY, command=self.start_investigation)
        self.btn_start.pack(side=LEFT)
        
        # Progress (hidden initially)
        self.progress = ttk.Progressbar(self, mode="indeterminate", bootstyle=SUCCESS)
        
        # Result Panel (Hidden by default, shown upon validation/completion)
        self.result_frame = ttk.Frame(self, bootstyle=DARK)
        self.result_frame.pack(fill=X, pady=10, padx=10)
        self.result_frame.pack_forget() # Hide initially
        
        create_section_header(self.result_frame, "Wallet Summary")
        
        self.lbl_status = ttk.Label(self.result_frame, text="Status: ", font=("Helvetica", 12, "bold"))
        self.lbl_status.pack(anchor=NW, padx=20, pady=2)
        
        self.lbl_blockchain = ttk.Label(self.result_frame, text="Blockchain: ", font=("Helvetica", 12))
        self.lbl_blockchain.pack(anchor=NW, padx=20, pady=2)
        
        self.lbl_address = ttk.Label(self.result_frame, text="Address: ", font=("Helvetica", 12))
        self.lbl_address.pack(anchor=NW, padx=20, pady=2)
        
        self.lbl_balance = ttk.Label(self.result_frame, text="Balance: ", font=("Helvetica", 12))
        self.lbl_balance.pack(anchor=NW, padx=20, pady=2)
        
        self.lbl_txcount = ttk.Label(self.result_frame, text="Transaction Count: ", font=("Helvetica", 12))
        self.lbl_txcount.pack(anchor=NW, padx=20, pady=2)
        
        self.lbl_total_recv = ttk.Label(self.result_frame, text="Total Received: ", font=("Helvetica", 12))
        self.lbl_total_recv.pack(anchor=NW, padx=20, pady=2)
        
        self.lbl_total_sent = ttk.Label(self.result_frame, text="Total Sent: ", font=("Helvetica", 12))
        self.lbl_total_sent.pack(anchor=NW, padx=20, pady=2)
        
        self.lbl_message = ttk.Label(self.result_frame, text="", font=("Helvetica", 12))
        self.lbl_message.pack(anchor=NW, padx=20, pady=(2, 20))
        
        self.lbl_start_msg = ttk.Label(self, text="", font=("Helvetica", 10, "italic"), bootstyle="warning")
        self.lbl_start_msg.pack(anchor=NW, padx=20, pady=10)
        
    def run_validation(self):
        address = self.entry_addr.get().strip()
        chain = self.chain_var.get()
        
        result = detect_and_validate(address, chain)
        
        self.result_frame.pack(fill=X, pady=10, padx=10)
        self.lbl_start_msg.config(text="") 
        
        if result["valid"]:
            self.lbl_status.config(text="Status: VALID SYNTAX", bootstyle=SUCCESS)
            self.lbl_blockchain.config(text=f"Detected Type: {result['detected_type']}")
            self.lbl_address.config(text=f"Address: {address}")
            self.lbl_balance.pack_forget()
            self.lbl_txcount.pack_forget()
            self.lbl_total_recv.pack_forget()
            self.lbl_total_sent.pack_forget()
            self.lbl_message.config(text=f"Message: {result['reason']}")
            
            if "possible_chains" in result and len(result["possible_chains"]) > 1:
                self.lbl_message.config(text=f"Message: Ambiguous EVM address. Please select Ethereum or BNB Smart Chain from the dropdown.")
        else:
            self.lbl_status.config(text="Status: INVALID SYNTAX", bootstyle=DANGER)
            self.lbl_blockchain.config(text="")
            self.lbl_address.config(text="")
            self.lbl_balance.pack_forget()
            self.lbl_txcount.pack_forget()
            self.lbl_total_recv.pack_forget()
            self.lbl_total_sent.pack_forget()
            self.lbl_message.config(text=f"Reason: {result['reason']}")
            
    def start_investigation(self):
        address = self.entry_addr.get().strip()
        chain = self.chain_var.get()
        
        if not address:
            self.lbl_start_msg.config(text="Please enter an address.")
            return
            
        result = detect_and_validate(address, chain)
        if not result["valid"]:
            self.lbl_start_msg.config(text="Invalid address syntax.")
            return
            
        selected_chain = chain
        if selected_chain == "Auto Detect":
            if "possible_chains" in result and len(result["possible_chains"]) > 1:
                self.lbl_start_msg.config(text="Ambiguous EVM address. Please manually select Ethereum or BNB Smart Chain.")
                return
            else:
                # If unambiguous, select the detected chain
                if result["detected_type"] == "Bitcoin":
                    selected_chain = "Bitcoin"
                elif result["detected_type"] == "EVM":
                    # Should be handled above, but fallback
                    self.lbl_start_msg.config(text="Ambiguous EVM address. Please select chain.")
                    return
                else:
                    self.lbl_start_msg.config(text="Unsupported blockchain type.")
                    return
        
        data_mode = self.config.get("DATA_MODE", "demo").lower()
        if data_mode == "demo":
            self.lbl_start_msg.config(text="Running in Demo Mode. Live API data is disabled.")
            return
            
        self.btn_start.config(state=DISABLED)
        self.btn_validate.config(state=DISABLED)
        self.lbl_start_msg.config(text="Fetching live data...", bootstyle=INFO)
        self.progress.pack(fill=X, pady=5, padx=10)
        self.progress.start()
        
        # Launch background thread
        thread = threading.Thread(target=self._fetch_live_data, args=(address, selected_chain))
        thread.daemon = True
        thread.start()

    def _fetch_live_data(self, address, chain):
        try:
            summary = {}
            if chain == "Bitcoin":
                svc = BitcoinService()
                summary = svc.get_address_summary(address)
            elif chain == "Ethereum":
                key = self.config.get("ETHERSCAN_API_KEY")
                svc = EthereumService(api_key=key)
                summary = svc.get_address_summary(address)
            elif chain == "BNB Smart Chain":
                key = self.config.get("ANKR_API_KEY")
                svc = BscService(api_key=key)
                summary = svc.get_address_summary(address)
            else:
                summary = {"error": f"Unsupported chain: {chain}"}
                
            # Schedule UI update
            self.after(0, self._handle_live_data_result, summary, chain, address)
        except Exception as e:
            logger.error(f"Error fetching live data: {e}")
            self.after(0, self._handle_live_data_result, {"error": "Internal exception occurred."}, chain, address)

    def _handle_live_data_result(self, summary, chain, address):
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_start.config(state=NORMAL)
        self.btn_validate.config(state=NORMAL)
        self.lbl_start_msg.config(text="")
        
        self.result_frame.pack(fill=X, pady=10, padx=10)
        
        if "error" in summary:
            self.lbl_status.config(text="Status: API ERROR", bootstyle=DANGER)
            self.lbl_blockchain.config(text=f"Blockchain: {chain}")
            self.lbl_address.config(text=f"Address: {address}")
            self.lbl_message.config(text=summary["error"])
            
            self.lbl_balance.pack_forget()
            self.lbl_txcount.pack_forget()
            self.lbl_total_recv.pack_forget()
            self.lbl_total_sent.pack_forget()
            return
            
        self.lbl_status.config(text="Status: LIVE DATA", bootstyle=SUCCESS)
        self.lbl_blockchain.config(text=f"Blockchain: {chain}")
        self.lbl_address.config(text=f"Address: {address}")
        self.lbl_message.config(text="")
        
        # Display available metrics safely
        self.lbl_balance.pack(anchor=NW, padx=20, pady=2)
        if "final_balance" in summary:
            bal = summary['final_balance']
            if chain == "Bitcoin":
                self.lbl_balance.config(text=f"Balance: {bal / 100000000:.8f} BTC")
            else:
                self.lbl_balance.config(text=f"Balance (wei): {bal}")
        else:
            self.lbl_balance.config(text="Balance: N/A")
            
        self.lbl_txcount.pack(anchor=NW, padx=20, pady=2)
        self.lbl_txcount.config(text=f"Transaction Count: {summary.get('n_tx', 0)}")
        
        if chain == "Bitcoin":
            self.lbl_total_recv.pack(anchor=NW, padx=20, pady=2)
            self.lbl_total_sent.pack(anchor=NW, padx=20, pady=2)
            self.lbl_total_recv.config(text=f"Total Received: {summary.get('total_received', 0) / 100000000:.8f} BTC")
            self.lbl_total_sent.config(text=f"Total Sent: {summary.get('total_sent', 0) / 100000000:.8f} BTC")
        else:
            self.lbl_total_recv.pack_forget()
            self.lbl_total_sent.pack_forget()
            
        # Update Transactions Page via Main Window
        tx_list = summary.get("transactions", [])
        provider_name = ""
        if chain == "Bitcoin":
            provider_name = "blockchain.com"
        elif chain == "Ethereum":
            provider_name = "etherscan"
        elif chain == "BNB Smart Chain":
            provider_name = "ankr"
            
        from analysis.transaction_normalizer import normalize_transactions
        normalized_txs = normalize_transactions(provider_name, tx_list, address, chain)
        
        main_win = self.winfo_toplevel()
        if hasattr(main_win, 'load_transactions'):
            main_win.load_transactions(normalized_txs, chain, address)
            self.lbl_start_msg.config(text=f"Successfully loaded {len(normalized_txs)} transactions.", bootstyle=SUCCESS)
