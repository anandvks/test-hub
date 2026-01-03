"""
Data Review Tab

Browse historical test data, view plots, and export results.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from data.session import SessionManager
from data.exporter import DataExporter, BatchExporter, create_analysis_summary
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ReviewTab(ttk.Frame):
    """Data review and export tab."""

    def __init__(self, parent):
        """
        Initialize review tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.session_manager = SessionManager()
        self.current_session = None
        self.current_test = None

        self._create_widgets()
        self.refresh_sessions()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main container with two panes
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left pane: Session browser
        left_frame = ttk.Frame(paned, width=300)
        paned.add(left_frame, weight=1)

        self._create_browser(left_frame)

        # Right pane: Detail view
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)

        self._create_detail_view(right_frame)

    def _create_browser(self, parent):
        """Create session/test browser."""
        # Header with refresh button
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(header, text="Sessions", font=('', 11, 'bold')).pack(side=tk.LEFT)

        ttk.Button(header, text="↻ Refresh", command=self.refresh_sessions,
                  width=10).pack(side=tk.RIGHT)

        # Session tree view
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('type', 'count'),
            show='tree headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Configure columns
        self.tree.heading('#0', text='Session / Test')
        self.tree.heading('type', text='Type')
        self.tree.heading('count', text='Count/Status')

        self.tree.column('#0', width=180)
        self.tree.column('type', width=60)
        self.tree.column('count', width=50)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Context menu
        self.tree.bind('<Button-3>', self.show_context_menu)

        # Action buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="Export Session",
                  command=self.export_session).pack(fill=tk.X, pady=2)

        ttk.Button(btn_frame, text="Delete Session",
                  command=self.delete_session).pack(fill=tk.X, pady=2)

    def _create_detail_view(self, parent):
        """Create detail view panel."""
        # Notebook for different views
        self.detail_notebook = ttk.Notebook(parent)
        self.detail_notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Information
        info_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(info_frame, text="Information")
        self._create_info_view(info_frame)

        # Tab 2: Data
        data_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(data_frame, text="Data")
        self._create_data_view(data_frame)

        # Tab 3: Plots
        plot_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(plot_frame, text="Plots")
        self._create_plot_view(plot_frame)

        # Tab 4: Export
        export_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(export_frame, text="Export")
        self._create_export_view(export_frame)

    def _create_info_view(self, parent):
        """Create information view."""
        # Scrollable text widget
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.info_text = tk.Text(text_frame, wrap=tk.WORD, height=20,
                                font=('Courier', 9))

        scrollbar = ttk.Scrollbar(text_frame, command=self.info_text.yview)
        self.info_text.config(yscrollcommand=scrollbar.set)

        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Make read-only
        self.info_text.config(state=tk.DISABLED)

    def _create_data_view(self, parent):
        """Create data table view."""
        # Table with scrollbars
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")

        self.data_table = ttk.Treeview(
            table_frame,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.data_table.yview)
        hsb.config(command=self.data_table.xview)

        self.data_table.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Export data button
        ttk.Button(parent, text="Export Data as CSV",
                  command=self.export_data_csv).pack(pady=5)

    def _create_plot_view(self, parent):
        """Create plot display view."""
        self.plot_canvas_frame = ttk.Frame(parent)
        self.plot_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Plot will be created dynamically
        self.plot_canvas = None

        # Save plot button
        ttk.Button(parent, text="Save Plot as PNG",
                  command=self.save_plot).pack(pady=5)

    def _create_export_view(self, parent):
        """Create export options view."""
        export_frame = ttk.LabelFrame(parent, text="Export Options", padding=20)
        export_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Format selection
        ttk.Label(export_frame, text="Export Format:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )

        self.export_format = tk.StringVar(value='csv')
        formats = [
            ('CSV Data', 'csv'),
            ('JSON Data', 'json'),
            ('Text Report', 'txt'),
            ('All Formats', 'all')
        ]

        for i, (text, value) in enumerate(formats):
            ttk.Radiobutton(
                export_frame,
                text=text,
                variable=self.export_format,
                value=value
            ).grid(row=i+1, column=0, sticky=tk.W, padx=20)

        # Include options
        ttk.Separator(export_frame, orient=tk.HORIZONTAL).grid(
            row=len(formats)+1, column=0, columnspan=2, sticky='ew', pady=10
        )

        ttk.Label(export_frame, text="Include:").grid(
            row=len(formats)+2, column=0, sticky=tk.W, pady=5
        )

        self.include_plots = tk.BooleanVar(value=True)
        self.include_config = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            export_frame,
            text="Plot Images",
            variable=self.include_plots
        ).grid(row=len(formats)+3, column=0, sticky=tk.W, padx=20)

        ttk.Checkbutton(
            export_frame,
            text="Configuration Files",
            variable=self.include_config
        ).grid(row=len(formats)+4, column=0, sticky=tk.W, padx=20)

        # Export button
        ttk.Button(
            export_frame,
            text="Export Selected",
            command=self.export_selected,
            style='Accent.TButton'
        ).grid(row=len(formats)+5, column=0, pady=20)

    def refresh_sessions(self):
        """Refresh session list."""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load sessions
        sessions = self.session_manager.list_sessions(sort_by='created')

        for session_data in sessions:
            session_id = session_data['session_id']

            # Add session node
            session_node = self.tree.insert(
                '',
                'end',
                text=session_id,
                values=(session_data.get('platform', 'Unknown'),
                       f"{session_data.get('num_tests', 0)} tests")
            )

            # Load full session to get tests
            session = self.session_manager.load_session(session_id)
            if session:
                for test in session.metadata.get('tests', []):
                    self.tree.insert(
                        session_node,
                        'end',
                        text=test.get('test_id', 'Unknown'),
                        values=(test.get('test_type', 'Unknown'),
                               test.get('status', 'Unknown'))
                    )

    def on_tree_select(self, event):
        """Handle tree selection."""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        parent = self.tree.parent(item)

        if not parent:  # Session selected
            session_id = self.tree.item(item, 'text')
            self.current_session = self.session_manager.load_session(session_id)
            self.current_test = None
            self.display_session_info()
        else:  # Test selected
            session_id = self.tree.item(parent, 'text')
            test_id = self.tree.item(item, 'text')

            self.current_session = self.session_manager.load_session(session_id)
            if self.current_session:
                # Find test
                for test in self.current_session.metadata.get('tests', []):
                    if test['test_id'] == test_id:
                        self.current_test = test
                        break

            self.display_test_info()

    def display_session_info(self):
        """Display session information."""
        if not self.current_session:
            return

        # Update info text
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        info = f"""Session Information
{'='*60}

Session ID: {self.current_session.session_id}
Created: {self.current_session.metadata.get('created', 'Unknown')}
Platform: {self.current_session.metadata.get('platform', 'Unknown')}
Number of Tests: {len(self.current_session.metadata.get('tests', []))}

Hardware Configuration:
"""
        for key, value in self.current_session.metadata.get('hardware', {}).items():
            info += f"  {key}: {value}\n"

        info += f"\nNotes:\n{self.current_session.metadata.get('notes', 'None')}\n"

        info += "\n\nTests in this session:\n"
        info += "-" * 60 + "\n"

        for i, test in enumerate(self.current_session.metadata.get('tests', []), 1):
            info += f"\n{i}. {test.get('test_type', 'Unknown')} ({test.get('test_id', 'Unknown')})\n"
            info += f"   Time: {test.get('timestamp', 'Unknown')}\n"
            info += f"   Status: {test.get('status', 'Unknown')}\n"

        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)

    def display_test_info(self):
        """Display test information."""
        if not self.current_test:
            return

        # Update info text
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        info = f"""Test Information
{'='*60}

Test ID: {self.current_test.get('test_id', 'Unknown')}
Test Type: {self.current_test.get('test_type', 'Unknown')}
Timestamp: {self.current_test.get('timestamp', 'Unknown')}
Status: {self.current_test.get('status', 'Unknown')}

Configuration:
"""
        for key, value in self.current_test.get('config', {}).items():
            info += f"  {key}: {value}\n"

        if 'results' in self.current_test:
            info += "\nResults:\n"
            for key, value in self.current_test['results'].items():
                info += f"  {key}: {value}\n"

        info += f"\nData File: {self.current_test.get('data_file', 'None')}\n"
        info += f"Plot Files: {len(self.current_test.get('plot_files', []))}\n"

        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)

        # Load data into table
        self.load_test_data()

    def load_test_data(self):
        """Load test data into table."""
        # Clear current table
        for item in self.data_table.get_children():
            self.data_table.delete(item)

        if not self.current_test or not self.current_session:
            return

        data_file = self.current_test.get('data_file')
        if not data_file:
            return

        filepath = self.current_session.session_dir / data_file

        if not filepath.exists():
            return

        # Read CSV
        try:
            from data.exporter import DataExporter
            data, metadata = DataExporter.read_csv(filepath)

            if data:
                # Configure columns
                columns = list(data[0].keys())
                self.data_table.config(columns=columns)

                for col in columns:
                    self.data_table.heading(col, text=col)
                    self.data_table.column(col, width=100)

                # Add rows (limit to first 1000 for performance)
                for row in data[:1000]:
                    values = [row.get(col, '') for col in columns]
                    self.data_table.insert('', 'end', values=values)

        except Exception as e:
            print(f"Error loading data: {e}")

    def export_session(self):
        """Export entire session."""
        if not self.current_session:
            messagebox.showwarning("No Selection", "Please select a session to export")
            return

        # Ask for output directory
        output_dir = filedialog.askdirectory(title="Select Export Directory")
        if not output_dir:
            return

        # Export
        exporter = BatchExporter(self.current_session)
        exporter.export_session(Path(output_dir), formats=['csv', 'json', 'txt'])

        messagebox.showinfo("Export Complete",
                          f"Session exported to:\n{output_dir}")

    def export_selected(self):
        """Export selected session or test."""
        # Implementation for custom export options
        pass

    def export_data_csv(self):
        """Export current data table as CSV."""
        # Implementation
        pass

    def save_plot(self):
        """Save current plot as image."""
        # Implementation
        pass

    def delete_session(self):
        """Delete selected session."""
        if not self.current_session:
            messagebox.showwarning("No Selection", "Please select a session to delete")
            return

        # Confirm deletion
        response = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete session:\n{self.current_session.session_id}?\n\nThis cannot be undone."
        )

        if response:
            self.session_manager.delete_session(self.current_session.session_id)
            self.current_session = None
            self.current_test = None
            self.refresh_sessions()
            messagebox.showinfo("Deleted", "Session deleted successfully")

    def show_context_menu(self, event):
        """Show context menu on right-click."""
        # Implementation for context menu
        pass
