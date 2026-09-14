import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import networkx as nx
import threading
import logging
from decimal import Decimal
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from gui.components import create_empty_state
from analysis.graph_engine import build_graph
from analysis.tracing_engine import trace_path

logger = logging.getLogger(__name__)

class GraphPage(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.transactions = []
        self.graph = None
        
        lbl_title = ttk.Label(self, text="Transaction Graph", font=("Helvetica", 18, "bold"))
        lbl_title.pack(anchor=NW, pady=(0, 10))
        
        # Controls Frame
        controls_frame = ttk.Frame(self, bootstyle=SECONDARY)
        controls_frame.pack(fill=X, pady=5)
        
        # Row 1
        row1 = ttk.Frame(controls_frame, bootstyle=SECONDARY)
        row1.pack(fill=X, pady=5)
        
        ttk.Label(row1, text="Source Wallet:", bootstyle="inverse-secondary").pack(side=LEFT, padx=(10, 5))
        self.entry_source = ttk.Entry(row1, width=25)
        self.entry_source.pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(row1, text="Target Wallet:", bootstyle="inverse-secondary").pack(side=LEFT, padx=(10, 5))
        self.entry_target = ttk.Entry(row1, width=25)
        self.entry_target.pack(side=LEFT, padx=(0, 10))
        
        # Row 2
        row2 = ttk.Frame(controls_frame, bootstyle=SECONDARY)
        row2.pack(fill=X, pady=5)
        
        ttk.Label(row2, text="Max Hops:", bootstyle="inverse-secondary").pack(side=LEFT, padx=(10, 5))
        self.entry_hops = ttk.Entry(row2, width=10)
        self.entry_hops.pack(side=LEFT, padx=(0, 10))
        self.entry_hops.insert(0, "5")
        
        ttk.Label(row2, text="Min Amount:", bootstyle="inverse-secondary").pack(side=LEFT, padx=(10, 5))
        self.entry_min = ttk.Entry(row2, width=15)
        self.entry_min.pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(row2, text="Direction:", bootstyle="inverse-secondary").pack(side=LEFT, padx=(10, 5))
        self.combo_dir = ttk.Combobox(row2, values=["ALL", "INCOMING", "OUTGOING", "INTERNAL", "RELATED"], state="readonly", width=12)
        self.combo_dir.pack(side=LEFT, padx=(0, 10))
        self.combo_dir.current(0)
        
        # Row 3
        row3 = ttk.Frame(controls_frame, bootstyle=SECONDARY)
        row3.pack(fill=X, pady=5)
        
        self.btn_build = ttk.Button(row3, text="Build Graph", bootstyle=INFO, command=self.build_graph_ui)
        self.btn_build.pack(side=LEFT, padx=(10, 5))
        
        self.btn_trace = ttk.Button(row3, text="Trace Path", bootstyle=PRIMARY, command=self.trace_path_ui)
        self.btn_trace.pack(side=LEFT, padx=5)
        
        self.btn_reset = ttk.Button(row3, text="Reset", bootstyle=SECONDARY, command=self.reset_graph_ui)
        self.btn_reset.pack(side=LEFT, padx=5)
        
        self.lbl_status = ttk.Label(row3, text="", font=("Helvetica", 10, "italic"), bootstyle="warning")
        self.lbl_status.pack(side=LEFT, padx=10)
        
        # Main Display Area
        display_frame = ttk.Frame(self)
        display_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Left: Graph
        self.graph_frame = ttk.Frame(display_frame, bootstyle=DARK)
        self.graph_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        self.empty_label = ttk.Label(self.graph_frame, text="Transaction graph will appear here after blockchain data is loaded.", bootstyle="inverse-dark")
        self.empty_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        self.canvas_widget = None
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        
        # Right: Details Panel
        details_frame = ttk.Frame(display_frame, width=250, bootstyle=SECONDARY)
        details_frame.pack(side=RIGHT, fill=Y)
        details_frame.pack_propagate(False)
        
        ttk.Label(details_frame, text="Details", font=("Helvetica", 14, "bold"), bootstyle="inverse-secondary").pack(anchor=NW, pady=10, padx=10)
        self.text_details = tk.Text(details_frame, wrap=WORD, font=("Helvetica", 10), bg="#222222", fg="white")
        self.text_details.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        self.text_details.insert(END, "Select a node or edge to view details.")
        self.text_details.config(state=DISABLED)
        
    def load_transactions(self, tx_list):
        """Called by MainWindow to update the underlying investigation data."""
        self.transactions = tx_list
        self.lbl_status.config(text=f"Loaded {len(tx_list)} normalized transactions.")
        
    def _set_status(self, msg, style=INFO):
        self.lbl_status.config(text=msg, bootstyle=style)
        
    def _update_details(self, msg):
        self.text_details.config(state=NORMAL)
        self.text_details.delete("1.0", END)
        self.text_details.insert(END, msg)
        self.text_details.config(state=DISABLED)

    def build_graph_ui(self):
        if not self.transactions:
            self._set_status("No transactions loaded. Perform an investigation first.", DANGER)
            return
            
        direction = self.combo_dir.get()
        min_amt_str = self.entry_min.get().strip()
        min_amt = None
        if min_amt_str:
            try:
                min_amt = Decimal(min_amt_str)
            except:
                self._set_status("Invalid minimum amount.", DANGER)
                return
                
        self.btn_build.config(state=DISABLED)
        self.btn_trace.config(state=DISABLED)
        self._set_status("Building graph...", WARNING)
        
        thread = threading.Thread(target=self._worker_build_graph, args=(direction, min_amt))
        thread.daemon = True
        thread.start()
        
    def _worker_build_graph(self, direction, min_amt):
        try:
            self.graph = build_graph(self.transactions, direction, min_amt)
            self.after(0, self._render_graph, None, None)
        except Exception as e:
            logger.error(f"Error building graph: {e}")
            self.after(0, self._set_status, f"Error: {e}", "danger")
            self.after(0, lambda: self.btn_build.config(state=NORMAL))
            self.after(0, lambda: self.btn_trace.config(state=NORMAL))

    def _render_graph(self, highlighted_edges=None, highlighted_nodes=None):
        try:
            if not self.graph or self.graph.number_of_nodes() == 0:
                self._set_status("Graph is empty.", WARNING)
                self.btn_build.config(state=NORMAL)
                self.btn_trace.config(state=NORMAL)
                return
                
            n_nodes = self.graph.number_of_nodes()
            n_edges = self.graph.number_of_edges()
            
            if n_nodes > 500 or n_edges > 1000:
                self._set_status(f"Large graph ({n_nodes} nodes, {n_edges} edges). Visual capped. Use trace.", DANGER)
                
            self.empty_label.place_forget()
            
            if self.canvas_widget:
                self.canvas_widget.destroy()
                
            self.ax.clear()
            
            # Simple layout
            pos = nx.spring_layout(self.graph, seed=42)
            
            # Draw nodes
            node_colors = []
            for node in self.graph.nodes():
                if highlighted_nodes and node in highlighted_nodes:
                    if node == highlighted_nodes[0]:
                        node_colors.append("green") # Source
                    elif node == highlighted_nodes[-1]:
                        node_colors.append("red") # Target
                    else:
                        node_colors.append("orange") # Intermediate
                else:
                    node_colors.append("lightblue")
                    
            nx.draw_networkx_nodes(
                self.graph, pos, ax=self.ax, 
                node_color=node_colors, 
                node_size=300, alpha=0.8
            )
            
            # Draw edges
            if highlighted_edges:
                # Draw normal edges light
                nx.draw_networkx_edges(self.graph, pos, ax=self.ax, alpha=0.2, arrows=True)
                # Draw highlighted
                nx.draw_networkx_edges(self.graph, pos, ax=self.ax, edgelist=highlighted_edges, edge_color="red", width=2.0, arrows=True)
            else:
                nx.draw_networkx_edges(self.graph, pos, ax=self.ax, alpha=0.6, arrows=True)
                
            # Labels (truncated for display)
            labels = {n: n[:8]+"..." if len(n)>8 else n for n in self.graph.nodes()}
            nx.draw_networkx_labels(self.graph, pos, labels=labels, ax=self.ax, font_size=8)
            
            self.ax.set_title(f"Transaction Graph ({n_nodes} nodes, {n_edges} edges)", color="white")
            self.fig.patch.set_facecolor('#222222')
            self.ax.set_facecolor('#222222')
            
            canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
            canvas.draw()
            self.canvas_widget = canvas.get_tk_widget()
            self.canvas_widget.pack(fill=BOTH, expand=True)
            
            # Matplotlib event bindings
            self.fig.canvas.mpl_connect('button_press_event', lambda e: self._on_click(e, pos))
            
            self._set_status(f"Graph rendered.", SUCCESS)
        except Exception as e:
            logger.error(f"Error rendering graph: {e}")
            self._set_status(f"Error rendering: {e}", DANGER)
            
        self.btn_build.config(state=NORMAL)
        self.btn_trace.config(state=NORMAL)
        
    def _on_click(self, event, pos):
        if event.inaxes != self.ax:
            return
            
        # Very crude hit testing for nodes
        click_x, click_y = event.xdata, event.ydata
        if click_x is None or click_y is None:
            return
            
        closest_node = None
        min_dist = float('inf')
        for node, (nx_x, nx_y) in pos.items():
            dist = (nx_x - click_x)**2 + (nx_y - click_y)**2
            if dist < min_dist:
                min_dist = dist
                closest_node = node
                
        if min_dist < 0.05: # threshold
            self._show_node_details(closest_node)
            return
            
    def _show_node_details(self, node):
        if not self.graph or not self.graph.has_node(node):
            return
            
        in_deg = self.graph.in_degree(node)
        out_deg = self.graph.out_degree(node)
        
        info = f"NODE DETAILS\n\nAddress:\n{node}\n\nIncoming Edges: {in_deg}\nOutgoing Edges: {out_deg}\n"
        
        # Check connected edges for tx details
        edges = list(self.graph.in_edges(node, data=True)) + list(self.graph.out_edges(node, data=True))
        if edges:
            u, v, data = edges[0]
            info += f"\nExample Transaction:\nHash: {data.get('tx_hash', 'N/A')}\nAmount: {data.get('amount', 0)} {data.get('asset', '')}\nProvider: {data.get('provider', '')}"
            
        self._update_details(info)

    def trace_path_ui(self):
        if not self.graph:
            self._set_status("Build a graph first.", WARNING)
            return
            
        source = self.entry_source.get().strip()
        target = self.entry_target.get().strip()
        
        if not source or not target:
            self._set_status("Source and target are required for tracing.", WARNING)
            return
            
        try:
            hops = int(self.entry_hops.get())
        except:
            self._set_status("Invalid Max Hops.", DANGER)
            return
            
        self.btn_build.config(state=DISABLED)
        self.btn_trace.config(state=DISABLED)
        self._set_status("Tracing path...", WARNING)
        
        thread = threading.Thread(target=self._worker_trace_path, args=(source, target, hops))
        thread.daemon = True
        thread.start()
        
    def _worker_trace_path(self, source, target, hops):
        try:
            res = trace_path(self.graph, source, target, max_hops=hops)
            self.after(0, self._handle_trace_result, res)
        except Exception as e:
            logger.error(f"Error tracing path: {e}")
            self.after(0, self._set_status, f"Error: {e}", "danger")
            self.after(0, lambda: self.btn_build.config(state=NORMAL))
            self.after(0, lambda: self.btn_trace.config(state=NORMAL))
            
    def _handle_trace_result(self, res):
        if not res.found:
            self._set_status(res.message, DANGER)
            self.btn_build.config(state=NORMAL)
            self.btn_trace.config(state=NORMAL)
            return
            
        self._set_status(res.message, SUCCESS)
        
        info = f"TRACE RESULT\n\nSource:\n{res.source}\n\nTarget:\n{res.target}\n\nMin Hops: {res.hops}\nCandidate Paths: {len(res.candidate_paths)}\n"
        self._update_details(info)
        
        # Highlight shortest path edges using exact edge identities
        highlighted_edges = []
        highlighted_nodes = [res.source]
        
        for edge_data in res.shortest_path_edges:
            u = edge_data.get("_u")
            v = edge_data.get("_v")
            if u and v:
                highlighted_edges.append((u, v))
                if v not in highlighted_nodes:
                    highlighted_nodes.append(v)
            
        self._render_graph(highlighted_edges, highlighted_nodes)
        
    def reset_graph_ui(self):
        self.entry_source.delete(0, END)
        self.entry_target.delete(0, END)
        self.combo_dir.current(0)
        self.entry_min.delete(0, END)
        self.entry_hops.delete(0, END)
        self.entry_hops.insert(0, "5")
        
        self._update_details("Select a node or edge to view details.")
        self.build_graph_ui()
