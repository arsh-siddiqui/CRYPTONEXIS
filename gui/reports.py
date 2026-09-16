import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.components import create_empty_state
from services.case_service import CaseService
from services.report_service import ReportService
import threading
import os
import subprocess
from tkinter import messagebox

class ReportsPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.case_service = CaseService()
        self.report_service = ReportService(config)
        
        lbl_title = ttk.Label(self, text="Investigation Reports", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 20))
        
        # Case Selection
        case_frame = ttk.Frame(self)
        case_frame.pack(fill=X, pady=10)
        
        ttk.Label(case_frame, text="Select Case:", font=("Helvetica", 12)).pack(side=LEFT, padx=(0, 10))
        
        self.case_var = tk.StringVar()
        self.cb_cases = ttk.Combobox(case_frame, textvariable=self.case_var, state="readonly", width=40)
        self.cb_cases.pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(case_frame, text="Refresh Cases", bootstyle=SECONDARY, command=self._load_cases).pack(side=LEFT, padx=(0, 20))
        
        # Export Actions
        ttk.Button(case_frame, text="Generate PDF", bootstyle=DANGER, command=self._generate_pdf).pack(side=LEFT, padx=(0, 10))
        ttk.Button(case_frame, text="Generate HTML", bootstyle=INFO, command=self._generate_html).pack(side=LEFT, padx=(0, 10))
        ttk.Button(case_frame, text="Open Output Folder", bootstyle=SUCCESS, command=self._open_folder).pack(side=LEFT)
        
        # Table of existing reports (simulation/visualization of cases)
        table_frame = ttk.Frame(self, bootstyle=SECONDARY)
        table_frame.pack(fill=BOTH, expand=True, pady=20)
        
        cols = ("Case ID", "Case Number", "Title", "Status", "Priority", "Data Mode")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.cases_map = {}
        self._load_cases()

    def _load_cases(self):
        def load():
            cases = self.case_service.list_cases()
            self.cases_map = {f"{c.case_number} - {c.title}": c.id for c in cases}
            
            self.cb_cases['values'] = list(self.cases_map.keys())
            if self.cases_map:
                self.cb_cases.current(0)
                
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            mode = self.config.get("DATA_MODE", "LIVE")
            for c in cases:
                self.tree.insert("", tk.END, values=(c.id, c.case_number, c.title, c.status, c.priority, mode))
        threading.Thread(target=load, daemon=True).start()
        
    def _get_selected_case_id(self):
        selection = self.case_var.get()
        return self.cases_map.get(selection)

    def _generate_pdf(self):
        case_id = self._get_selected_case_id()
        if not case_id:
            messagebox.showwarning("No Case", "Please select a case first.")
            return
            
        def run():
            filepath = self.report_service.generate_pdf(case_id)
            if filepath:
                messagebox.showinfo("Success", f"PDF generated successfully:\n{filepath}")
            else:
                messagebox.showerror("Error", "Failed to generate PDF. Check logs.")
        threading.Thread(target=run, daemon=True).start()

    def _generate_html(self):
        case_id = self._get_selected_case_id()
        if not case_id:
            messagebox.showwarning("No Case", "Please select a case first.")
            return
            
        def run():
            filepath = self.report_service.generate_html(case_id)
            if filepath:
                messagebox.showinfo("Success", f"HTML generated successfully:\n{filepath}")
            else:
                messagebox.showerror("Error", "Failed to generate HTML. Check logs.")
        threading.Thread(target=run, daemon=True).start()

    def _open_folder(self):
        folder = self.report_service.output_dir
        if os.name == 'nt':
            os.startfile(folder)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', folder])
        else:
            subprocess.Popen(['xdg-open', folder])
