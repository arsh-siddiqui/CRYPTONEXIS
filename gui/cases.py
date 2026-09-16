import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.components import create_empty_state, create_section_header
from services.case_service import CaseService
from analysis.crypto_detector import detect_and_validate
import threading
from tkinter import messagebox

class CasesPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.case_service = CaseService()
        self.active_case_id = None
        
        # Split layout: Left (Case List), Right (Case Details)
        self.paned = ttk.PanedWindow(self, orient=HORIZONTAL)
        self.paned.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        self.left_frame = ttk.Frame(self.paned)
        self.right_frame = ttk.Frame(self.paned)
        
        self.paned.add(self.left_frame, weight=1)
        self.paned.add(self.right_frame, weight=2)
        
        self._build_left_panel()
        self._build_right_panel()
        
        self.refresh_cases()

    def _build_left_panel(self):
        lbl_title = ttk.Label(self.left_frame, text="Case Management", font=("Helvetica", 16, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 10))
        
        controls = ttk.Frame(self.left_frame)
        controls.pack(fill=X, pady=(0, 10))
        
        ttk.Button(controls, text="New Case", bootstyle=SUCCESS, command=self._open_new_case_dialog).pack(side=LEFT, padx=(0,5))
        ttk.Button(controls, text="Refresh", bootstyle=SECONDARY, command=self.refresh_cases).pack(side=LEFT)
        
        cols = ("Case #", "Title", "Status")
        self.tree = ttk.Treeview(self.left_frame, columns=cols, show="headings", height=15)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_case_select)
        
    def _build_right_panel(self):
        self.details_container = ttk.Frame(self.right_frame)
        self.details_container.pack(fill=BOTH, expand=True, padx=10)
        create_empty_state(self.details_container, "Select a case to view details.")

    def refresh_cases(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        def load():
            cases = self.case_service.list_cases()
            for case in cases:
                self.tree.insert("", tk.END, values=(case.case_number, case.title, case.status), iid=str(case.id))
        
        threading.Thread(target=load, daemon=True).start()

    def _on_case_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        case_id = int(selection[0])
        self.active_case_id = case_id
        self._show_case_details(case_id)

    def _show_case_details(self, case_id: int):
        for widget in self.details_container.winfo_children():
            widget.destroy()
            
        case = self.case_service.get_case(case_id)
        if not case:
            create_empty_state(self.details_container, "Case not found.")
            return

        header = ttk.Frame(self.details_container)
        header.pack(fill=X, pady=(0, 10))
        
        ttk.Label(header, text=f"{case.case_number}: {case.title}", font=("Helvetica", 16, "bold")).pack(side=LEFT)
        
        status_color = SUCCESS if case.status == "OPEN" else SECONDARY
        ttk.Label(header, text=case.status, bootstyle=status_color).pack(side=LEFT, padx=10)
        
        ttk.Button(header, text="Close Case", bootstyle=DANGER, command=lambda: self._close_case(case.id)).pack(side=RIGHT)
        
        # Notebook for sections
        notebook = ttk.Notebook(self.details_container)
        notebook.pack(fill=BOTH, expand=True)
        
        # Tab 1: Info & Wallets
        tab_info = ttk.Frame(notebook)
        notebook.add(tab_info, text="Information")
        
        ttk.Label(tab_info, text=f"Priority: {case.priority}").pack(anchor=W, pady=5)
        ttk.Label(tab_info, text=f"Created At: {case.created_at}").pack(anchor=W, pady=5)
        ttk.Label(tab_info, text=f"Description: {case.description}").pack(anchor=W, pady=5)
        
        create_section_header(tab_info, "Wallets")
        for w in case.wallets:
            ttk.Label(tab_info, text=f"• {w.wallet_address} ({w.blockchain}) - {w.role}").pack(anchor=W)
            
        # Tab 2: Evidence
        tab_evidence = ttk.Frame(notebook)
        notebook.add(tab_evidence, text="Evidence")
        if not case.evidence:
            create_empty_state(tab_evidence, "No evidence attached.")
        else:
            cols = ("Type", "Title", "Source")
            ev_tree = ttk.Treeview(tab_evidence, columns=cols, show="headings")
            for col in cols: ev_tree.heading(col, text=col)
            ev_tree.pack(fill=BOTH, expand=True, pady=5)
            for ev in case.evidence:
                ev_tree.insert("", tk.END, values=(ev.evidence_type, ev.title, ev.source))

    def _open_new_case_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("New Case")
        dialog.geometry("400x500")
        
        ttk.Label(dialog, text="Title *").pack(anchor=W, padx=10, pady=(10,0))
        entry_title = ttk.Entry(dialog)
        entry_title.pack(fill=X, padx=10, pady=5)
        
        ttk.Label(dialog, text="Description").pack(anchor=W, padx=10)
        entry_desc = ttk.Entry(dialog)
        entry_desc.pack(fill=X, padx=10, pady=5)
        
        ttk.Label(dialog, text="Priority").pack(anchor=W, padx=10)
        cb_priority = ttk.Combobox(dialog, values=["LOW", "MEDIUM", "HIGH"], state="readonly")
        cb_priority.current(1)
        cb_priority.pack(fill=X, padx=10, pady=5)
        
        ttk.Label(dialog, text="Primary Wallet Address (Optional)").pack(anchor=W, padx=10)
        entry_wallet = ttk.Entry(dialog)
        entry_wallet.pack(fill=X, padx=10, pady=5)
        
        def save():
            title = entry_title.get().strip()
            if not title:
                messagebox.showerror("Error", "Title is required.")
                return
                
            wallet = entry_wallet.get().strip()
            blockchain = None
            if wallet:
                result = detect_and_validate(wallet)
                if not result.is_valid:
                    messagebox.showerror("Validation Error", "Invalid wallet address format.")
                    return
                blockchain = result.cryptocurrency.upper()
                
            def _do_save():
                case = self.case_service.create_case(
                    title=title,
                    description=entry_desc.get().strip(),
                    priority=cb_priority.get(),
                    primary_wallet=wallet if wallet else None,
                    primary_blockchain=blockchain
                )
                dialog.destroy()
                self.refresh_cases()
                if case:
                    self._show_case_details(case.id)
                    
            threading.Thread(target=_do_save, daemon=True).start()
            
        ttk.Button(dialog, text="Create Case", bootstyle=SUCCESS, command=save).pack(pady=20)

    def _close_case(self, case_id: int):
        if messagebox.askyesno("Close Case", "Are you sure you want to close this case?"):
            self.case_service.close_case(case_id)
            self.refresh_cases()
            self._show_case_details(case_id)
