"""
Test Library Tab

GUI for selecting, configuring, and running automated tests.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from typing import Dict, Any


class TestLibraryTab(ttk.Frame):
    """Test Library tab for automated testing."""

    def __init__(self, parent, test_registry):
        """
        Initialize Test Library tab.

        Args:
            parent: Parent widget
            test_registry: TestRegistry instance
        """
        super().__init__(parent)
        self.registry = test_registry
        self.selected_test_id = None
        self.param_widgets = {}
        self.test_thread = None
        self.current_test = None

        self._create_widgets()

    def _create_widgets(self):
        """Create GUI widgets."""
        # Main layout: left catalog + right config
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Left: Test catalog
        self._create_test_catalog(left_frame)

        # Right: Configuration panel
        self._create_config_panel(right_frame)

    def _create_test_catalog(self, parent):
        """Create test selection catalog."""
        ttk.Label(parent, text="Available Tests", font=('Arial', 12, 'bold')).pack(pady=5)

        # Test list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        # Listbox for tests
        self.test_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                       selectmode='single', font=('Arial', 10))
        self.test_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.test_listbox.yview)

        # Populate test list
        self.test_data = []
        for test_id, name, description in self.registry.get_test_list():
            self.test_listbox.insert('end', name)
            self.test_data.append({'id': test_id, 'name': name, 'description': description})

        self.test_listbox.bind('<<ListboxSelect>>', self._on_test_selected)

        # Description panel
        desc_frame = ttk.LabelFrame(parent, text="Description")
        desc_frame.pack(fill='both', pady=10)

        self.description_text = tk.Text(desc_frame, height=4, wrap='word', font=('Arial', 9))
        self.description_text.pack(fill='both', padx=5, pady=5)
        self.description_text.config(state='disabled')

        # Estimated duration
        self.duration_label = ttk.Label(parent, text="Estimated duration: --")
        self.duration_label.pack(pady=5)

    def _create_config_panel(self, parent):
        """Create configuration panel."""
        ttk.Label(parent, text="Test Configuration", font=('Arial', 12, 'bold')).pack(pady=5)

        # Scrollable config frame
        canvas = tk.Canvas(parent, height=400)
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        self.config_frame = ttk.Frame(canvas)

        self.config_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.config_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=10)

        self.run_button = ttk.Button(button_frame, text="Run Test", command=self._run_test)
        self.run_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self._stop_test, state='disabled')
        self.stop_button.pack(side='left', padx=5)

        self.pause_button = ttk.Button(button_frame, text="Pause", command=self._pause_test, state='disabled')
        self.pause_button.pack(side='left', padx=5)

        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_params).pack(side='left', padx=5)

        # Progress
        progress_frame = ttk.LabelFrame(parent, text="Progress")
        progress_frame.pack(fill='x', pady=10)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill='x', padx=5, pady=5)

        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.pack(pady=5)

        # Results
        results_frame = ttk.LabelFrame(parent, text="Results")
        results_frame.pack(fill='both', expand=True, pady=10)

        self.results_text = scrolledtext.ScrolledText(results_frame, height=10, wrap='word', font=('Courier', 9))
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)

    def _on_test_selected(self, event):
        """Handle test selection."""
        selection = self.test_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        test_info = self.test_data[idx]
        self.selected_test_id = test_info['id']

        # Update description
        self.description_text.config(state='normal')
        self.description_text.delete('1.0', 'end')
        self.description_text.insert('1.0', test_info['description'])
        self.description_text.config(state='disabled')

        # Generate parameter widgets
        self._generate_param_widgets()

        # Update estimated duration
        self._update_duration_estimate()

    def _generate_param_widgets(self):
        """Generate parameter input widgets based on test definition."""
        # Clear existing widgets
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        self.param_widgets.clear()

        if not self.selected_test_id:
            return

        test = self.registry.get_test(self.selected_test_id)
        if not test:
            return

        params = test.get_parameters()

        row = 0
        for param_name, param_def in params.items():
            # Label
            label_text = param_name.replace('_', ' ').title()
            if 'unit' in param_def:
                label_text += f" ({param_def['unit']})"
            ttk.Label(self.config_frame, text=label_text).grid(row=row, column=0, sticky='w', padx=5, pady=5)

            # Input widget based on type
            param_type = param_def['type']

            if param_type in ['int', 'float']:
                # Create slider + entry
                widget_frame = ttk.Frame(self.config_frame)
                widget_frame.grid(row=row, column=1, sticky='ew', padx=5, pady=5)

                var = tk.DoubleVar(value=param_def['default']) if param_type == 'float' else tk.IntVar(value=param_def['default'])

                # Entry
                entry = ttk.Entry(widget_frame, textvariable=var, width=10)
                entry.pack(side='left', padx=(0, 5))

                # Slider (if min/max defined)
                if 'min' in param_def and 'max' in param_def:
                    scale = ttk.Scale(widget_frame, from_=param_def['min'], to=param_def['max'],
                                     variable=var, orient='horizontal')
                    scale.pack(side='left', fill='x', expand=True)

                self.param_widgets[param_name] = var

            elif param_type == 'bool':
                var = tk.BooleanVar(value=param_def.get('default', False))
                checkbox = ttk.Checkbutton(self.config_frame, variable=var)
                checkbox.grid(row=row, column=1, sticky='w', padx=5, pady=5)
                self.param_widgets[param_name] = var

            elif param_type == 'str':
                var = tk.StringVar(value=param_def.get('default', ''))
                entry = ttk.Entry(self.config_frame, textvariable=var, width=30)
                entry.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
                self.param_widgets[param_name] = var

            # Description tooltip
            if 'description' in param_def:
                desc_label = ttk.Label(self.config_frame, text=param_def['description'],
                                      font=('Arial', 8), foreground='gray')
                desc_label.grid(row=row, column=2, sticky='w', padx=5)

            row += 1

        self.config_frame.grid_columnconfigure(1, weight=1)

        # Bind value changes to update duration
        for var in self.param_widgets.values():
            if isinstance(var, (tk.IntVar, tk.DoubleVar, tk.StringVar, tk.BooleanVar)):
                var.trace_add('write', lambda *args: self._update_duration_estimate())

    def _update_duration_estimate(self):
        """Update estimated duration label."""
        if not self.selected_test_id:
            return

        test = self.registry.get_test(self.selected_test_id)
        if not test:
            return

        try:
            config = self._get_config()
            duration_sec = test.estimate_duration(config)

            if duration_sec < 60:
                duration_str = f"{duration_sec:.0f} seconds"
            elif duration_sec < 3600:
                duration_str = f"{duration_sec/60:.1f} minutes"
            else:
                duration_str = f"{duration_sec/3600:.1f} hours"

            self.duration_label.config(text=f"Estimated duration: {duration_str}")
        except:
            self.duration_label.config(text="Estimated duration: --")

    def _get_config(self) -> Dict[str, Any]:
        """Get current configuration from widgets."""
        config = {}
        for param_name, var in self.param_widgets.items():
            config[param_name] = var.get()
        return config

    def _reset_params(self):
        """Reset parameters to defaults."""
        if not self.selected_test_id:
            return

        test = self.registry.get_test(self.selected_test_id)
        if not test:
            return

        params = test.get_parameters()
        for param_name, param_def in params.items():
            if param_name in self.param_widgets:
                self.param_widgets[param_name].set(param_def['default'])

    def _run_test(self):
        """Run selected test."""
        if not self.selected_test_id:
            messagebox.showwarning("No Test Selected", "Please select a test from the list.")
            return

        # Get test instance
        test = self.registry.get_test(self.selected_test_id)
        if not test:
            messagebox.showerror("Error", "Failed to get test instance.")
            return

        # Get configuration
        config = self._get_config()

        # Validate configuration
        valid, error = test.validate_config(config)
        if not valid:
            messagebox.showerror("Invalid Configuration", f"Configuration error:\n{error}")
            return

        # Confirm long tests
        duration_sec = test.estimate_duration(config)
        if duration_sec > 3600:  # > 1 hour
            hours = duration_sec / 3600
            if not messagebox.askyesno("Long Test",
                                      f"This test will take approximately {hours:.1f} hours.\n\nContinue?"):
                return

        # Update UI state
        self.run_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.pause_button.config(state='normal')
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting test...")
        self.results_text.delete('1.0', 'end')
        self.results_text.insert('end', f"Starting {test.get_name()}...\n")

        # Store current test
        self.current_test = test

        # Run in background thread
        def run_thread():
            try:
                results = test.run(config, progress_callback=self._progress_callback)
                self.after(0, lambda: self._test_completed(results))
            except Exception as e:
                self.after(0, lambda: self._test_error(str(e)))

        self.test_thread = threading.Thread(target=run_thread, daemon=True)
        self.test_thread.start()

    def _progress_callback(self, progress: float, message: str):
        """Progress callback from test."""
        def update():
            self.progress_bar['value'] = max(0, min(100, progress))
            self.progress_label.config(text=message)
            self.results_text.insert('end', f"{message}\n")
            self.results_text.see('end')

        self.after(0, update)

    def _test_completed(self, results: dict):
        """Handle test completion."""
        self.run_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.pause_button.config(state='disabled')
        self.progress_bar['value'] = 100
        self.progress_label.config(text="Test completed")

        # Display results
        self.results_text.insert('end', "\n" + "="*50 + "\n")
        self.results_text.insert('end', "TEST RESULTS\n")
        self.results_text.insert('end', "="*50 + "\n\n")

        if 'error' in results:
            self.results_text.insert('end', f"ERROR: {results['error']}\n")
        elif 'summary' in results:
            self.results_text.insert('end', "Summary:\n")
            for key, value in results['summary'].items():
                if isinstance(value, dict):
                    self.results_text.insert('end', f"  {key}:\n")
                    for k, v in value.items():
                        self.results_text.insert('end', f"    {k}: {v}\n")
                else:
                    self.results_text.insert('end', f"  {key}: {value}\n")

        if 'log_file' in results:
            self.results_text.insert('end', f"\nData logged to: {results['log_file']}\n")

        self.results_text.see('end')

    def _test_error(self, error_msg: str):
        """Handle test error."""
        self.run_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.pause_button.config(state='disabled')
        self.progress_label.config(text="Test failed")

        self.results_text.insert('end', f"\nERROR: {error_msg}\n")
        self.results_text.see('end')

        messagebox.showerror("Test Failed", f"Test failed with error:\n{error_msg}")

    def _stop_test(self):
        """Stop running test."""
        if self.current_test:
            self.current_test.stop()
            self.results_text.insert('end', "\nTest stopped by user.\n")
            self.results_text.see('end')

    def _pause_test(self):
        """Pause/resume running test."""
        if not self.current_test:
            return

        if self.current_test.is_paused:
            self.current_test.resume()
            self.pause_button.config(text="Pause")
            self.results_text.insert('end', "Test resumed.\n")
        else:
            self.current_test.pause()
            self.pause_button.config(text="Resume")
            self.results_text.insert('end', "Test paused.\n")

        self.results_text.see('end')
