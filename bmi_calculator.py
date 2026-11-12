"""
BMI Calculator & Health Analytics with Matplotlib Chart Integration
Built with Python, Tkinter, and Matplotlib.
"""

import os
import sys
import tempfile
import json
import csv
from datetime import datetime

# Configure Matplotlib config directory to avoid directory write warnings
if "MPLCONFIGDIR" not in os.environ:
    mpl_cache = os.path.join(tempfile.gettempdir(), "matplotlib_cache")
    os.makedirs(mpl_cache, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = mpl_cache

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches


# ---------------------------------------------------------
# BMI Classification Data & Standards (WHO Guidelines)
# ---------------------------------------------------------
BMI_CATEGORIES = [
    {
        "name": "Underweight",
        "min": 0.0,
        "max": 18.5,
        "color": "#38bdf8",     # Sky blue
        "risk": "Low / Malnutrition Risk",
        "advice": "Below normal weight range. Consider increasing nutrient-dense caloric intake and consult a physician."
    },
    {
        "name": "Normal Weight",
        "min": 18.5,
        "max": 24.9,
        "color": "#22c55e",     # Emerald green
        "risk": "Optimal Health Zone",
        "advice": "Great job! Your BMI is in the healthy zone. Maintain regular physical activity and balanced nutrition."
    },
    {
        "name": "Overweight",
        "min": 25.0,
        "max": 29.9,
        "color": "#f59e0b",     # Amber yellow
        "risk": "Moderate Risk",
        "advice": "Slightly above the healthy range. Adding 30 minutes of daily cardio and mindful eating can help reach ideal weight."
    },
    {
        "name": "Obesity Class I",
        "min": 30.0,
        "max": 34.9,
        "color": "#f97316",     # Orange
        "risk": "Elevated Risk",
        "advice": "Increased cardiovascular and metabolic risk. A physician or registered dietitian can provide a guided plan."
    },
    {
        "name": "Obesity Class II",
        "min": 35.0,
        "max": 39.9,
        "color": "#ef4444",     # Red
        "risk": "High Risk",
        "advice": "Significantly elevated health risks. Personalized medical guidance, dietary changes, and exercise are advised."
    },
    {
        "name": "Obesity Class III",
        "min": 40.0,
        "max": 60.0,
        "color": "#991b1b",     # Deep crimson
        "risk": "Very High Risk",
        "advice": "Severe obesity range. Clinical evaluation, structured weight management, and comprehensive care are recommended."
    }
]


def classify_bmi(bmi: float):
    """Return category dict corresponding to a given BMI score."""
    for cat in BMI_CATEGORIES:
        if cat["min"] <= bmi < cat["max"]:
            return cat
    # For very extreme BMI values >= 60.0
    return BMI_CATEGORIES[-1]


# ---------------------------------------------------------
# Theme Definitions (Light & Dark)
# ---------------------------------------------------------
THEMES = {
    "dark": {
        "bg_primary": "#0f172a",       # Slate 900
        "bg_secondary": "#1e293b",     # Slate 800
        "bg_card": "#334155",          # Slate 700
        "bg_input": "#1e293b",
        "fg_primary": "#f8fafc",       # Slate 50
        "fg_secondary": "#94a3b8",     # Slate 400
        "accent": "#6366f1",           # Indigo
        "accent_hover": "#4f46e5",
        "chart_bg": "#1e293b",
        "chart_fg": "#f1f5f9",
        "chart_grid": "#334155",
        "tree_bg": "#1e293b",
        "tree_fg": "#f8fafc",
        "tree_select": "#4338ca",
        "border": "#475569"
    },
    "light": {
        "bg_primary": "#f1f5f9",       # Slate 100
        "bg_secondary": "#ffffff",     # White
        "bg_card": "#ffffff",
        "bg_input": "#ffffff",
        "fg_primary": "#0f172a",       # Slate 900
        "fg_secondary": "#64748b",     # Slate 500
        "accent": "#4f46e5",           # Indigo
        "accent_hover": "#4338ca",
        "chart_bg": "#ffffff",
        "chart_fg": "#0f172a",
        "chart_grid": "#e2e8f0",
        "tree_bg": "#ffffff",
        "tree_fg": "#0f172a",
        "tree_select": "#c7d2fe",
        "border": "#cbd5e1"
    }
}


class BMICalculatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("BMI Analytics Pro - Body Mass Index & Health Chart")
        self.root.geometry("1180x820")
        self.root.minsize(1050, 720)

        # Default theme
        self.current_theme = "dark"
        self.theme = THEMES[self.current_theme]

        # History file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.history_file = os.path.join(script_dir, "bmi_history.json")
        self.history_records = []

        # Current calculation state
        self.current_result = None
        self.active_chart_tab = "gauge"   # 'gauge', 'weights', 'trend'

        # Tkinter variables
        self.unit_system = tk.StringVar(value="metric")  # 'metric' or 'imperial'
        self.metric_weight_var = tk.StringVar(value="70.0")
        self.metric_height_var = tk.StringVar(value="175.0")
        
        self.imp_weight_var = tk.StringVar(value="154.0")
        self.imp_height_ft_var = tk.StringVar(value="5")
        self.imp_height_in_var = tk.StringVar(value="9")

        self.age_var = tk.StringVar(value="28")
        self.gender_var = tk.StringVar(value="Female")

        # Load historical records
        self._load_history()

        # Build UI layout
        self._setup_styles()
        self._build_ui()
        self._apply_theme()

        # Initial calculation on launch
        self.calculate_bmi(save=False)

    # ---------------------------------------------------------
    # Styles & Theme Engine
    # ---------------------------------------------------------
    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

    def _apply_theme(self):
        t = THEMES[self.current_theme]
        self.theme = t

        self.root.configure(bg=t["bg_primary"])

        # Configure TTK styles
        self.style.configure(".", background=t["bg_secondary"], foreground=t["fg_primary"])
        self.style.configure("TFrame", background=t["bg_secondary"])
        self.style.configure("Main.TFrame", background=t["bg_primary"])
        self.style.configure("Card.TFrame", background=t["bg_card"], relief="flat")
        
        self.style.configure("Header.TLabel", background=t["bg_primary"], foreground=t["fg_primary"], font=("Segoe UI", 18, "bold"))
        self.style.configure("Subheader.TLabel", background=t["bg_primary"], foreground=t["fg_secondary"], font=("Segoe UI", 9))
        self.style.configure("CardHeader.TLabel", background=t["bg_secondary"], foreground=t["fg_primary"], font=("Segoe UI", 12, "bold"))
        self.style.configure("FieldLabel.TLabel", background=t["bg_secondary"], foreground=t["fg_primary"], font=("Segoe UI", 10))
        self.style.configure("Muted.TLabel", background=t["bg_secondary"], foreground=t["fg_secondary"], font=("Segoe UI", 9))

        self.style.configure("TRadiobutton", background=t["bg_secondary"], foreground=t["fg_primary"], font=("Segoe UI", 10, "bold"))
        self.style.map("TRadiobutton", background=[("active", t["bg_secondary"])])

        # Treeview styling
        self.style.configure("Treeview",
                             background=t["tree_bg"],
                             foreground=t["tree_fg"],
                             fieldbackground=t["tree_bg"],
                             rowheight=26,
                             font=("Segoe UI", 9))
        self.style.map("Treeview", background=[("selected", t["tree_select"])], foreground=[("selected", "#ffffff")])
        self.style.configure("Treeview.Heading",
                             background=t["bg_card"],
                             foreground=t["fg_primary"],
                             font=("Segoe UI", 9, "bold"))

        # Update pure Tkinter containers recursively
        self._apply_theme_to_hierarchy(self.root, t)

        # Re-render active chart with updated theme colors
        self.render_chart()

    def _apply_theme_to_hierarchy(self, widget, t):
        """Recursively update standard Tkinter frames, labels, and entries."""
        try:
            w_class = widget.winfo_class()
            tag = getattr(widget, "_theme_role", None)

            if w_class in ("Frame", "Labelframe"):
                if tag == "primary":
                    widget.configure(bg=t["bg_primary"])
                elif tag == "card":
                    widget.configure(bg=t["bg_card"])
                elif tag == "nav":
                    widget.configure(bg=t["bg_card"])
                else:
                    widget.configure(bg=t["bg_secondary"])

                if w_class == "Labelframe":
                    widget.configure(fg=t["fg_primary"], bg=t["bg_secondary"])

            elif w_class == "Label":
                if tag == "primary_header":
                    widget.configure(bg=t["bg_primary"], fg=t["fg_primary"])
                elif tag == "primary_sub":
                    widget.configure(bg=t["bg_primary"], fg=t["fg_secondary"])
                elif tag == "quote":
                    widget.configure(bg=t["bg_primary"], fg=t["fg_primary"])
                elif tag in ("badge", "score"):
                    # Dynamic colors based on BMI classification
                    widget.configure(bg=widget.cget("bg"))
                else:
                    widget.configure(bg=t["bg_secondary"], fg=t["fg_primary"])

            elif w_class == "Entry":
                widget.configure(bg=t["bg_input"], fg=t["fg_primary"], insertbackground=t["fg_primary"])

        except Exception:
            pass

        for child in widget.winfo_children():
            self._apply_theme_to_hierarchy(child, t)

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.theme_btn.config(
            text="☀️ Light Mode" if self.current_theme == "dark" else "🌙 Dark Mode"
        )
        self._apply_theme()

    # ---------------------------------------------------------
    # Layout Builder
    # ---------------------------------------------------------
    def _build_ui(self):
        # Header banner
        header_frame = tk.Frame(self.root, bg=self.theme["bg_primary"], pady=12, padx=20)
        header_frame._theme_role = "primary"
        header_frame.pack(fill=tk.X)

        title_box = tk.Frame(header_frame, bg=self.theme["bg_primary"])
        title_box._theme_role = "primary"
        title_box.pack(side=tk.LEFT)

        app_title = ttk.Label(title_box, text="⚖️  BMI Analytics Pro", style="Header.TLabel")
        app_title.pack(anchor="w")

        app_subtitle = ttk.Label(title_box, text="Comprehensive Body Mass Index Calculator & Interactive Visualization", style="Subheader.TLabel")
        app_subtitle.pack(anchor="w")

        # Top-right controls: Theme toggle & Sample data loader
        top_ctrls = tk.Frame(header_frame, bg=self.theme["bg_primary"])
        top_ctrls._theme_role = "primary"
        top_ctrls.pack(side=tk.RIGHT)

        sample_btn = tk.Button(
            top_ctrls,
            text="📊 Load Sample History",
            command=self.load_sample_history,
            font=("Segoe UI", 9),
            bg="#0284c7",
            fg="white",
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2"
        )
        sample_btn.pack(side=tk.LEFT, padx=6)

        self.theme_btn = tk.Button(
            top_ctrls,
            text="☀️ Light Mode" if self.current_theme == "dark" else "🌙 Dark Mode",
            command=self.toggle_theme,
            font=("Segoe UI", 9, "bold"),
            bg="#475569",
            fg="white",
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.theme_btn.pack(side=tk.LEFT, padx=6)

        # Main 2-column container
        main_content = tk.Frame(self.root, bg=self.theme["bg_primary"], padx=16, pady=4)
        main_content._theme_role = "primary"
        main_content.pack(fill=tk.BOTH, expand=True)

        # Left Column: Inputs & History (approx 440px)
        left_col = tk.Frame(main_content, bg=self.theme["bg_primary"], width=440)
        left_col._theme_role = "primary"
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_col.pack_propagate(False)

        # Right Column: Results & Charts (remaining width)
        right_col = tk.Frame(main_content, bg=self.theme["bg_primary"])
        right_col._theme_role = "primary"
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Populate columns
        self._build_input_panel(left_col)
        self._build_history_panel(left_col)
        self._build_results_panel(right_col)
        self._build_chart_panel(right_col)

    # ---------------------------------------------------------
    # Left Column: Input Form
    # ---------------------------------------------------------
    def _build_input_panel(self, parent):
        card = tk.LabelFrame(
            parent,
            text=" Personal Measurements ",
            bg=self.theme["bg_secondary"],
            fg=self.theme["fg_primary"],
            font=("Segoe UI", 11, "bold"),
            padx=14,
            pady=10,
            relief="groove"
        )
        card.pack(fill=tk.X, pady=(0, 10))
        self.input_card = card

        # Unit selection radio buttons
        unit_frame = tk.Frame(card, bg=self.theme["bg_secondary"])
        unit_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(unit_frame, text="Unit System:", style="FieldLabel.TLabel").pack(side=tk.LEFT, padx=(0, 12))
        
        rb_metric = ttk.Radiobutton(
            unit_frame,
            text="Metric (kg, cm)",
            value="metric",
            variable=self.unit_system,
            command=self._on_unit_change
        )
        rb_metric.pack(side=tk.LEFT, padx=6)

        rb_imp = ttk.Radiobutton(
            unit_frame,
            text="Imperial (lbs, ft/in)",
            value="imperial",
            variable=self.unit_system,
            command=self._on_unit_change
        )
        rb_imp.pack(side=tk.LEFT, padx=6)

        # Input fields container (dynamic swap between Metric & Imperial)
        self.dynamic_input_frame = tk.Frame(card, bg=self.theme["bg_secondary"])
        self.dynamic_input_frame.pack(fill=tk.X, pady=2)

        # Optional demographic info (Age & Gender for BMR calculation)
        demo_frame = tk.Frame(card, bg=self.theme["bg_secondary"])
        demo_frame.pack(fill=tk.X, pady=(8, 12))

        # Age
        age_box = tk.Frame(demo_frame, bg=self.theme["bg_secondary"])
        age_box.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))
        ttk.Label(age_box, text="Age (yrs):", style="FieldLabel.TLabel").pack(anchor="w")
        self.age_entry = tk.Entry(age_box, textvariable=self.age_var, font=("Segoe UI", 10), width=8, justify="center")
        self.age_entry.pack(fill=tk.X, pady=2)

        # Gender
        gender_box = tk.Frame(demo_frame, bg=self.theme["bg_secondary"])
        gender_box.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(6, 0))
        ttk.Label(gender_box, text="Biological Sex:", style="FieldLabel.TLabel").pack(anchor="w")
        gender_cb = ttk.Combobox(
            gender_box,
            textvariable=self.gender_var,
            values=["Female", "Male", "Other / Prefer not to say"],
            state="readonly",
            font=("Segoe UI", 9)
        )
        gender_cb.pack(fill=tk.X, pady=2)

        self._render_unit_fields()

        # Action Buttons: Calculate, Save, Clear
        btn_frame = tk.Frame(card, bg=self.theme["bg_secondary"])
        btn_frame.pack(fill=tk.X, pady=(6, 4))

        calc_btn = tk.Button(
            btn_frame,
            text="⚡ Calculate BMI",
            command=lambda: self.calculate_bmi(save=False),
            bg="#4f46e5",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            pady=6,
            cursor="hand2"
        )
        calc_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        save_btn = tk.Button(
            btn_frame,
            text="💾 Save Log",
            command=lambda: self.calculate_bmi(save=True),
            bg="#059669",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            pady=6,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

        reset_btn = tk.Button(
            btn_frame,
            text="🔄 Reset",
            command=self.reset_inputs,
            bg="#64748b",
            fg="white",
            font=("Segoe UI", 10),
            relief="flat",
            pady=6,
            cursor="hand2"
        )
        reset_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))

    def _render_unit_fields(self):
        """Render either Metric or Imperial input widgets."""
        for widget in self.dynamic_input_frame.winfo_children():
            widget.destroy()

        unit = self.unit_system.get()

        if unit == "metric":
            # Weight (kg)
            w_frame = tk.Frame(self.dynamic_input_frame, bg=self.theme["bg_secondary"])
            w_frame.pack(fill=tk.X, pady=3)
            ttk.Label(w_frame, text="Weight (kg):", style="FieldLabel.TLabel", width=14).pack(side=tk.LEFT)
            w_ent = tk.Entry(w_frame, textvariable=self.metric_weight_var, font=("Segoe UI", 10), justify="center")
            w_ent.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Height (cm)
            h_frame = tk.Frame(self.dynamic_input_frame, bg=self.theme["bg_secondary"])
            h_frame.pack(fill=tk.X, pady=3)
            ttk.Label(h_frame, text="Height (cm):", style="FieldLabel.TLabel", width=14).pack(side=tk.LEFT)
            h_ent = tk.Entry(h_frame, textvariable=self.metric_height_var, font=("Segoe UI", 10), justify="center")
            h_ent.pack(side=tk.LEFT, fill=tk.X, expand=True)

        else:
            # Weight (lbs)
            w_frame = tk.Frame(self.dynamic_input_frame, bg=self.theme["bg_secondary"])
            w_frame.pack(fill=tk.X, pady=3)
            ttk.Label(w_frame, text="Weight (lbs):", style="FieldLabel.TLabel", width=14).pack(side=tk.LEFT)
            w_ent = tk.Entry(w_frame, textvariable=self.imp_weight_var, font=("Segoe UI", 10), justify="center")
            w_ent.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Height (ft & in)
            h_frame = tk.Frame(self.dynamic_input_frame, bg=self.theme["bg_secondary"])
            h_frame.pack(fill=tk.X, pady=3)
            ttk.Label(h_frame, text="Height (ft / in):", style="FieldLabel.TLabel", width=14).pack(side=tk.LEFT)

            ft_ent = tk.Entry(h_frame, textvariable=self.imp_height_ft_var, font=("Segoe UI", 10), width=6, justify="center")
            ft_ent.pack(side=tk.LEFT, padx=(0, 4))
            ttk.Label(h_frame, text="ft", style="Muted.TLabel").pack(side=tk.LEFT, padx=(0, 8))

            in_ent = tk.Entry(h_frame, textvariable=self.imp_height_in_var, font=("Segoe UI", 10), width=6, justify="center")
            in_ent.pack(side=tk.LEFT, padx=(0, 4))
            ttk.Label(h_frame, text="in", style="Muted.TLabel").pack(side=tk.LEFT)

    def _on_unit_change(self):
        # Auto-convert values when switching units to preserve context
        is_metric = (self.unit_system.get() == "metric")
        try:
            if is_metric:
                # Switched to metric from imperial
                lbs = float(self.imp_weight_var.get())
                ft = float(self.imp_height_ft_var.get())
                inch = float(self.imp_height_in_var.get())
                total_in = ft * 12 + inch
                
                kg = lbs * 0.45359237
                cm = total_in * 2.54
                self.metric_weight_var.set(f"{kg:.1f}")
                self.metric_height_var.set(f"{cm:.1f}")
            else:
                # Switched to imperial from metric
                kg = float(self.metric_weight_var.get())
                cm = float(self.metric_height_var.get())
                lbs = kg * 2.20462262
                total_in = cm / 2.54
                ft = int(total_in // 12)
                inch = round(total_in % 12, 1)
                self.imp_weight_var.set(f"{lbs:.1f}")
                self.imp_height_ft_var.set(str(ft))
                self.imp_height_in_var.set(str(inch))
        except (ValueError, TypeError):
            pass

        self._render_unit_fields()
        self.calculate_bmi(save=False)

    # ---------------------------------------------------------
    # Left Column: History Table & Management
    # ---------------------------------------------------------
    def _build_history_panel(self, parent):
        hist_card = tk.LabelFrame(
            parent,
            text=" Progress History ",
            bg=self.theme["bg_secondary"],
            fg=self.theme["fg_primary"],
            font=("Segoe UI", 11, "bold"),
            padx=10,
            pady=8,
            relief="groove"
        )
        hist_card.pack(fill=tk.BOTH, expand=True)
        self.hist_card = hist_card

        # Treeview table
        columns = ("date", "weight", "bmi", "category")
        self.tree = ttk.Treeview(hist_card, columns=columns, show="headings", height=8, selectmode="browse")
        self.tree.heading("date", text="Date / Time")
        self.tree.heading("weight", text="Weight")
        self.tree.heading("bmi", text="BMI")
        self.tree.heading("category", text="Classification")

        self.tree.column("date", width=110, anchor="center")
        self.tree.column("weight", width=70, anchor="center")
        self.tree.column("bmi", width=60, anchor="center")
        self.tree.column("category", width=120, anchor="w")

        # Scrollbar
        scrollbar = ttk.Scrollbar(hist_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, in_=self.tree)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # History action buttons
        hist_btns = tk.Frame(hist_card, bg=self.theme["bg_secondary"])
        hist_btns.pack(fill=tk.X, pady=(8, 2))

        del_btn = tk.Button(
            hist_btns,
            text="🗑️ Delete Entry",
            command=self.delete_selected_history,
            font=("Segoe UI", 9),
            bg="#ef4444",
            fg="white",
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2"
        )
        del_btn.pack(side=tk.LEFT, padx=3)

        export_btn = tk.Button(
            hist_btns,
            text="📤 Export CSV",
            command=self.export_csv,
            font=("Segoe UI", 9),
            bg="#3b82f6",
            fg="white",
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2"
        )
        export_btn.pack(side=tk.LEFT, padx=3)

        clear_btn = tk.Button(
            hist_btns,
            text="🧹 Clear All",
            command=self.clear_all_history,
            font=("Segoe UI", 9),
            bg="#64748b",
            fg="white",
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.RIGHT, padx=3)

        self._refresh_history_table()

    # ---------------------------------------------------------
    # Right Column: Calculation Result Card
    # ---------------------------------------------------------
    def _build_results_panel(self, parent):
        card = tk.Frame(parent, bg=self.theme["bg_secondary"], padx=16, pady=12, relief="groove", bd=1)
        card.pack(fill=tk.X, pady=(0, 10))
        self.results_card = card

        # Top line: Large BMI Score + Category Badge
        top_line = tk.Frame(card, bg=self.theme["bg_secondary"])
        top_line.pack(fill=tk.X)

        score_box = tk.Frame(top_line, bg=self.theme["bg_secondary"])
        score_box.pack(side=tk.LEFT)

        ttk.Label(score_box, text="BODY MASS INDEX", style="Subheader.TLabel").pack(anchor="w")
        self.bmi_number_lbl = tk.Label(
            score_box,
            text="22.9",
            font=("Segoe UI", 36, "bold"),
            bg=self.theme["bg_secondary"],
            fg="#22c55e"
        )
        self.bmi_number_lbl._theme_role = "score"
        self.bmi_number_lbl.pack(anchor="w")

        # Category & Risk pill
        badge_box = tk.Frame(top_line, bg=self.theme["bg_secondary"], padx=20)
        badge_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.category_badge = tk.Label(
            badge_box,
            text=" NORMAL WEIGHT ",
            font=("Segoe UI", 14, "bold"),
            bg="#22c55e",
            fg="#ffffff",
            padx=12,
            pady=4,
            relief="flat"
        )
        self.category_badge._theme_role = "badge"
        self.category_badge.pack(anchor="w", pady=(8, 4))

        self.risk_lbl = tk.Label(
            badge_box,
            text="Health Risk: Lowest Risk",
            font=("Segoe UI", 10, "italic"),
            bg=self.theme["bg_secondary"],
            fg=self.theme["fg_secondary"]
        )
        self.risk_lbl.pack(anchor="w")

        # Bottom row: Target Weight, Ideal Range, Advice
        details_box = tk.Frame(card, bg=self.theme["bg_secondary"], pady=6)
        details_box.pack(fill=tk.X)

        # Left metric block: Healthy range & delta
        m_box = tk.Frame(details_box, bg=self.theme["bg_secondary"])
        m_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.ideal_range_lbl = tk.Label(
            m_box,
            text="Optimal Weight Range: 56.7 kg - 76.3 kg",
            font=("Segoe UI", 10, "bold"),
            bg=self.theme["bg_secondary"],
            fg=self.theme["fg_primary"]
        )
        self.ideal_range_lbl.pack(anchor="w")

        self.weight_diff_lbl = tk.Label(
            m_box,
            text="Difference: You are currently within your optimal weight range.",
            font=("Segoe UI", 9),
            bg=self.theme["bg_secondary"],
            fg="#10b981"
        )
        self.weight_diff_lbl.pack(anchor="w", pady=2)

        # Right metric block: BMR & Ponderal Index
        bmr_box = tk.Frame(details_box, bg=self.theme["bg_secondary"])
        bmr_box.pack(side=tk.RIGHT)

        self.bmr_lbl = tk.Label(
            bmr_box,
            text="Estimated Basal Metabolic Rate: ~1,560 kcal/day",
            font=("Segoe UI", 9),
            bg=self.theme["bg_secondary"],
            fg=self.theme["fg_secondary"],
            justify="right"
        )
        self.bmr_lbl.pack(anchor="e")

        # Advice quote bar
        self.advice_lbl = tk.Label(
            card,
            text="Recommendation: Maintain regular physical activity and balanced nutrition.",
            font=("Segoe UI", 9, "italic"),
            bg=self.theme["bg_primary"],
            fg=self.theme["fg_primary"],
            padx=10,
            pady=6,
            wraplength=640,
            justify="left"
        )
        self.advice_lbl._theme_role = "quote"
        self.advice_lbl.pack(fill=tk.X, pady=(6, 0))

    # ---------------------------------------------------------
    # Right Column: Matplotlib Chart Visualizer
    # ---------------------------------------------------------
    def _build_chart_panel(self, parent):
        chart_card = tk.Frame(parent, bg=self.theme["bg_secondary"], relief="groove", bd=1)
        chart_card.pack(fill=tk.BOTH, expand=True)
        self.chart_card = chart_card

        # Chart selector navigation bar
        nav_bar = tk.Frame(chart_card, bg=self.theme["bg_card"], padx=10, pady=6)
        nav_bar._theme_role = "nav"
        nav_bar.pack(fill=tk.X)

        ttk.Label(nav_bar, text="Visualization Mode:", style="FieldLabel.TLabel").pack(side=tk.LEFT, padx=(0, 10))

        self.tab_gauge_btn = tk.Button(
            nav_bar,
            text="📊 BMI Spectrum Gauge",
            command=lambda: self.switch_chart_tab("gauge"),
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2"
        )
        self.tab_gauge_btn.pack(side=tk.LEFT, padx=3)

        self.tab_weights_btn = tk.Button(
            nav_bar,
            text="⚖️ Weight vs Target Zone",
            command=lambda: self.switch_chart_tab("weights"),
            font=("Segoe UI", 9),
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2"
        )
        self.tab_weights_btn.pack(side=tk.LEFT, padx=3)

        self.tab_trend_btn = tk.Button(
            nav_bar,
            text="📈 Historical Progress Trend",
            command=lambda: self.switch_chart_tab("trend"),
            font=("Segoe UI", 9),
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2"
        )
        self.tab_trend_btn.pack(side=tk.LEFT, padx=3)

        # Matplotlib Figure & Tk Canvas
        self.fig = Figure(figsize=(7, 4.2), dpi=100)
        self.fig.patch.set_facecolor(self.theme["chart_bg"])
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_card)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self._update_tab_buttons()

    def switch_chart_tab(self, tab_name: str):
        self.active_chart_tab = tab_name
        self._update_tab_buttons()
        self.render_chart()

    def _update_tab_buttons(self):
        active_bg = "#4f46e5"
        inactive_bg = "#475569"

        self.tab_gauge_btn.config(
            bg=active_bg if self.active_chart_tab == "gauge" else inactive_bg,
            fg="white"
        )
        self.tab_weights_btn.config(
            bg=active_bg if self.active_chart_tab == "weights" else inactive_bg,
            fg="white"
        )
        self.tab_trend_btn.config(
            bg=active_bg if self.active_chart_tab == "trend" else inactive_bg,
            fg="white"
        )

    # ---------------------------------------------------------
    # Chart Rendering Logic (Matplotlib)
    # ---------------------------------------------------------
    def render_chart(self):
        if not hasattr(self, "ax"):
            return

        t = self.theme
        self.fig.patch.set_facecolor(t["chart_bg"])
        self.ax.clear()
        self.ax.set_facecolor(t["chart_bg"])

        if self.active_chart_tab == "gauge":
            self._render_gauge_chart()
        elif self.active_chart_tab == "weights":
            self._render_weights_chart()
        elif self.active_chart_tab == "trend":
            self._render_trend_chart()

        self.fig.tight_layout()
        self.canvas.draw_idle()

    def _render_gauge_chart(self):
        """Horizontal segmented BMI spectrum gauge with marker pointing to current BMI."""
        t = self.theme
        ax = self.ax

        current_bmi = self.current_result["bmi"] if self.current_result else 22.5
        cat = classify_bmi(current_bmi)

        # Segments: Underweight (10-18.5), Normal (18.5-25), Overweight (25-30), Obese I (30-35), Obese II (35-40), Obese III (40-48)
        segments = [
            ("Underweight\n< 18.5", 10.0, 18.5, "#38bdf8"),
            ("Normal\n18.5 - 24.9", 18.5, 25.0, "#22c55e"),
            ("Overweight\n25 - 29.9", 25.0, 30.0, "#f59e0b"),
            ("Obese I\n30 - 34.9", 30.0, 35.0, "#f97316"),
            ("Obese II\n35 - 39.9", 35.0, 40.0, "#ef4444"),
            ("Obese III\n≥ 40", 40.0, 48.0, "#991b1b"),
        ]

        bar_y = 0.4
        bar_height = 0.28

        for label, start, end, color in segments:
            width = end - start
            # Draw segment bar
            rect = patches.FancyBboxPatch(
                (start, bar_y),
                width,
                bar_height,
                boxstyle="round,pad=0.01,rounding_size=0.15",
                facecolor=color,
                edgecolor=t["chart_bg"],
                linewidth=1.5,
                alpha=0.9
            )
            ax.add_patch(rect)

            # Segment label above bar
            center_x = (start + end) / 2
            ax.text(
                center_x,
                bar_y + bar_height + 0.05,
                label,
                ha="center",
                va="bottom",
                fontsize=8.5,
                color=t["chart_fg"],
                fontweight="bold"
            )

        # Clamp marker for visual display within bounds 10 to 48
        marker_x = max(10.2, min(47.8, current_bmi))

        # Arrow indicator pointing down to user's BMI
        ax.annotate(
            f"You: {current_bmi:.1f} BMI\n({cat['name']})",
            xy=(marker_x, bar_y + bar_height),
            xytext=(marker_x, bar_y + bar_height + 0.32),
            arrowprops=dict(
                facecolor=cat["color"],
                edgecolor=t["chart_fg"],
                shrink=0.05,
                width=3.5,
                headwidth=9,
                headlength=9
            ),
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color=t["chart_fg"],
            bbox=dict(boxstyle="round,pad=0.4", facecolor=t["bg_card"], edgecolor=cat["color"], linewidth=2)
        )

        # Baseline needle tick line
        ax.plot([marker_x, marker_x], [bar_y, bar_y + bar_height], color="#ffffff", linewidth=3)

        ax.set_xlim(8, 50)
        ax.set_ylim(0.0, 1.1)

        # X-axis ticks
        tick_vals = [10, 18.5, 25, 30, 35, 40, 48]
        ax.set_xticks(tick_vals)
        ax.set_xticklabels([str(v) for v in tick_vals], color=t["chart_fg"], fontsize=9)
        ax.set_yticks([])
        ax.set_xlabel("Body Mass Index (kg/m²)", color=t["chart_fg"], fontsize=10, labelpad=8)

        # Title & spines
        ax.set_title("WHO Body Mass Index Classification Spectrum", color=t["chart_fg"], fontsize=12, pad=12, fontweight="bold")
        for spine in ax.spines.values():
            spine.set_color(t["chart_grid"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)

    def _render_weights_chart(self):
        """Bar chart comparing Current Weight vs Minimum & Maximum Healthy Weight."""
        t = self.theme
        ax = self.ax

        if not self.current_result:
            return

        unit = self.unit_system.get()
        unit_lbl = "kg" if unit == "metric" else "lbs"

        curr_wt = self.current_result["weight"]
        min_wt = self.current_result["min_healthy_wt"]
        max_wt = self.current_result["max_healthy_wt"]
        mid_wt = (min_wt + max_wt) / 2.0

        labels = [f"Min Normal\n(BMI 18.5)", f"Your Weight\n({unit_lbl})", f"Max Normal\n(BMI 24.9)"]
        values = [min_wt, curr_wt, max_wt]
        cat_color = self.current_result["category_color"]
        colors = ["#0284c7", cat_color, "#059669"]

        bars = ax.bar(labels, values, color=colors, width=0.48, edgecolor=t["border"], linewidth=1.2)

        # Value annotations on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.1f} {unit_lbl}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 6),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
                color=t["chart_fg"]
            )

        # Shaded background reference zone for healthy weight
        ax.axhspan(min_wt, max_wt, color="#22c55e", alpha=0.15, label="Optimal Target Zone (18.5 - 24.9 BMI)")

        ax.set_ylabel(f"Weight ({unit_lbl})", color=t["chart_fg"], fontsize=10)
        ax.set_title("Current Weight vs. Optimal Healthy Weight Range", color=t["chart_fg"], fontsize=12, pad=12, fontweight="bold")
        
        ax.tick_params(axis="x", colors=t["chart_fg"], labelsize=10)
        ax.tick_params(axis="y", colors=t["chart_fg"], labelsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.3, color=t["chart_grid"])

        # Y limit with margin
        top_val = max(values) * 1.2
        ax.set_ylim(0, top_val)

        for spine in ax.spines.values():
            spine.set_color(t["chart_grid"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.legend(loc="upper left", facecolor=t["bg_card"], edgecolor=t["border"], labelcolor=t["chart_fg"], fontsize=9)

    def _render_trend_chart(self):
        """Historical line chart of BMI readings over time."""
        t = self.theme
        ax = self.ax

        if not self.history_records:
            ax.text(
                0.5, 0.5,
                "No historical records found.\nClick 'Save Log' or 'Load Sample History' to view trends!",
                ha="center", va="center",
                color=t["fg_secondary"],
                fontsize=11,
                transform=ax.transAxes
            )
            ax.set_title("Historical BMI Progress Over Time", color=t["chart_fg"], fontsize=12, pad=12, fontweight="bold")
            return

        # Sort history by date
        sorted_records = sorted(self.history_records, key=lambda x: x.get("timestamp", 0))

        dates = [r.get("short_date", r.get("date", "")[:10]) for r in sorted_records]
        bmis = [r.get("bmi", 22.0) for r in sorted_records]
        categories = [r.get("category", "Normal") for r in sorted_records]

        x_indices = list(range(len(dates)))

        # Plot healthy BMI zone background
        ax.axhspan(18.5, 24.9, color="#22c55e", alpha=0.18, label="Healthy BMI Zone (18.5 - 24.9)")
        ax.axhline(18.5, color="#10b981", linestyle="--", linewidth=1, alpha=0.6)
        ax.axhline(24.9, color="#10b981", linestyle="--", linewidth=1, alpha=0.6)

        # Plot trend line
        ax.plot(x_indices, bmis, color="#6366f1", linewidth=2.5, marker="o", markersize=7, markerfacecolor="#4f46e5", markeredgecolor="#ffffff", label="Your BMI")

        # Point annotations
        for idx, (x, y, cat_name) in enumerate(zip(x_indices, bmis, categories)):
            ax.annotate(
                f"{y:.1f}",
                xy=(x, y),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                color=t["chart_fg"]
            )

        ax.set_xticks(x_indices)
        ax.set_xticklabels(dates, color=t["chart_fg"], fontsize=8.5, rotation=25, ha="right")
        ax.tick_params(axis="y", colors=t["chart_fg"], labelsize=9)

        min_y = min(15.0, min(bmis) - 2.0)
        max_y = max(32.0, max(bmis) + 3.0)
        ax.set_ylim(min_y, max_y)

        ax.set_ylabel("BMI (kg/m²)", color=t["chart_fg"], fontsize=10)
        ax.set_title("Historical BMI Progress & Tracking", color=t["chart_fg"], fontsize=12, pad=12, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.3, color=t["chart_grid"])

        for spine in ax.spines.values():
            spine.set_color(t["chart_grid"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.legend(loc="upper left", facecolor=t["bg_card"], edgecolor=t["border"], labelcolor=t["chart_fg"], fontsize=9)

    # ---------------------------------------------------------
    # Core BMI Calculation Logic
    # ---------------------------------------------------------
    def calculate_bmi(self, save: bool = False):
        try:
            unit = self.unit_system.get()

            if unit == "metric":
                weight = float(self.metric_weight_var.get())
                height_cm = float(self.metric_height_var.get())
                if weight <= 0 or height_cm <= 0:
                    messagebox.showerror("Invalid Input", "Weight and Height must be positive numbers.")
                    return
                height_m = height_cm / 100.0
                weight_kg = weight
                display_wt_str = f"{weight:.1f} kg"
                display_ht_str = f"{height_cm:.1f} cm"
            else:
                weight_lbs = float(self.imp_weight_var.get())
                ft = float(self.imp_height_ft_var.get())
                inch = float(self.imp_height_in_var.get())
                total_in = ft * 12.0 + inch
                if weight_lbs <= 0 or total_in <= 0:
                    messagebox.showerror("Invalid Input", "Weight and Height must be positive numbers.")
                    return
                height_m = total_in * 0.0254
                weight_kg = weight_lbs * 0.45359237
                weight = weight_lbs
                display_wt_str = f"{weight_lbs:.1f} lbs"
                display_ht_str = f"{int(ft)}' {inch:.0f}\""

            if height_m < 0.5 or height_m > 2.8:
                messagebox.showerror("Unrealistic Height", "Please provide a realistic human height (0.5m - 2.8m).")
                return

            if weight_kg < 15.0 or weight_kg > 450.0:
                messagebox.showerror("Unrealistic Weight", "Please provide a realistic human weight (15kg - 450kg).")
                return

            # BMI = kg / m^2
            bmi = weight_kg / (height_m ** 2)
            cat = classify_bmi(bmi)

            # Healthy Weight Range for this height (BMI 18.5 - 24.9)
            min_healthy_kg = 18.5 * (height_m ** 2)
            max_healthy_kg = 24.9 * (height_m ** 2)

            if unit == "metric":
                min_healthy_wt = min_healthy_kg
                max_healthy_wt = max_healthy_kg
                unit_str = "kg"
                diff_to_normal_kg = 0.0
                if weight_kg < min_healthy_kg:
                    diff_to_normal_kg = min_healthy_kg - weight_kg
                    diff_text = f"Gain ~{diff_to_normal_kg:.1f} kg to enter the optimal healthy range."
                    diff_color = "#38bdf8"
                elif weight_kg > max_healthy_kg:
                    diff_to_normal_kg = weight_kg - max_healthy_kg
                    diff_text = f"Lose ~{diff_to_normal_kg:.1f} kg to reach the optimal healthy range."
                    diff_color = "#f97316"
                else:
                    diff_text = "You are currently within your optimal healthy range!"
                    diff_color = "#10b981"
            else:
                min_healthy_wt = min_healthy_kg * 2.20462262
                max_healthy_wt = max_healthy_kg * 2.20462262
                unit_str = "lbs"
                if weight_lbs < min_healthy_wt:
                    diff_lbs = min_healthy_wt - weight_lbs
                    diff_text = f"Gain ~{diff_lbs:.1f} lbs to enter the optimal healthy range."
                    diff_color = "#38bdf8"
                elif weight_lbs > max_healthy_wt:
                    diff_lbs = weight_lbs - max_healthy_wt
                    diff_text = f"Lose ~{diff_lbs:.1f} lbs to reach the optimal healthy range."
                    diff_color = "#f97316"
                else:
                    diff_text = "You are currently within your optimal healthy range!"
                    diff_color = "#10b981"

            # Basal Metabolic Rate (BMR) estimation via Mifflin-St Jeor formula
            bmr_val = None
            try:
                age = float(self.age_var.get())
                gender = self.gender_var.get().lower()
                if "female" in gender:
                    bmr_val = 10 * weight_kg + 6.25 * (height_m * 100) - 5 * age - 161
                elif "male" in gender:
                    bmr_val = 10 * weight_kg + 6.25 * (height_m * 100) - 5 * age + 5
                else:
                    bmr_val = 10 * weight_kg + 6.25 * (height_m * 100) - 5 * age - 78
            except (ValueError, TypeError):
                bmr_val = None

            # Update state dict
            self.current_result = {
                "bmi": bmi,
                "category": cat["name"],
                "category_color": cat["color"],
                "risk": cat["risk"],
                "advice": cat["advice"],
                "weight": weight,
                "height_m": height_m,
                "unit": unit,
                "min_healthy_wt": min_healthy_wt,
                "max_healthy_wt": max_healthy_wt,
                "unit_str": unit_str,
                "diff_text": diff_text,
                "diff_color": diff_color,
                "bmr": bmr_val,
                "display_wt": display_wt_str,
                "display_ht": display_ht_str
            }

            # Update UI labels
            self._update_result_ui()

            # Render Matplotlib Chart
            self.render_chart()

            # Save to history if explicitly requested
            if save:
                self._save_to_history()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for weight and height.")

    def _update_result_ui(self):
        res = self.current_result
        if not res:
            return

        self.bmi_number_lbl.config(text=f"{res['bmi']:.1f}", fg=res["category_color"])
        self.category_badge.config(
            text=f" {res['category'].upper()} ",
            bg=res["category_color"],
            fg="#ffffff"
        )
        self.risk_lbl.config(text=f"Health Risk Category: {res['risk']}")
        self.ideal_range_lbl.config(
            text=f"Optimal Healthy Range: {res['min_healthy_wt']:.1f} {res['unit_str']} - {res['max_healthy_wt']:.1f} {res['unit_str']}"
        )
        self.weight_diff_lbl.config(
            text=res["diff_text"],
            fg=res["diff_color"]
        )

        if res["bmr"]:
            self.bmr_lbl.config(text=f"Estimated Basal Metabolic Rate (BMR): ~{int(res['bmr']):,} kcal/day")
        else:
            self.bmr_lbl.config(text="BMR: Set age & sex to view calorie baseline")

        self.advice_lbl.config(text=f"💡 Health Tip: {res['advice']}")

    # ---------------------------------------------------------
    # History & Persistence
    # ---------------------------------------------------------
    def _save_to_history(self):
        res = self.current_result
        now = datetime.now()
        record = {
            "id": now.strftime("%Y%m%d%H%M%S"),
            "timestamp": now.timestamp(),
            "date": now.strftime("%Y-%m-%d %H:%M"),
            "short_date": now.strftime("%b %d"),
            "weight": res["weight"],
            "unit": res["unit_str"],
            "display_wt": res["display_wt"],
            "display_ht": res["display_ht"],
            "bmi": round(res["bmi"], 2),
            "category": res["category"]
        }
        self.history_records.append(record)
        self._write_history_file()
        self._refresh_history_table()
        messagebox.showinfo("Log Saved", f"Measurement saved! BMI: {record['bmi']} ({record['category']})")

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history_records = json.load(f)
            except Exception:
                self.history_records = []
        else:
            self.history_records = []

    def _write_history_file(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history_records, f, indent=2)
        except Exception as e:
            messagebox.showwarning("File Error", f"Could not persist history: {e}")

    def _refresh_history_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Show newest on top
        for rec in reversed(self.history_records):
            wt_str = rec.get("display_wt", f"{rec.get('weight')} {rec.get('unit', '')}")
            self.tree.insert("", tk.END, iid=rec["id"], values=(
                rec["date"],
                wt_str,
                f"{rec['bmi']:.1f}",
                rec["category"]
            ))

    def _on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        rec_id = selected[0]
        match = next((r for r in self.history_records if str(r["id"]) == str(rec_id)), None)
        if match:
            # We can switch to trend view or preview the record
            if self.active_chart_tab == "trend":
                self.render_chart()

    def delete_selected_history(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a history row to delete.")
            return
        rec_id = selected[0]
        self.history_records = [r for r in self.history_records if str(r["id"]) != str(rec_id)]
        self._write_history_file()
        self._refresh_history_table()
        self.render_chart()

    def clear_all_history(self):
        if not self.history_records:
            return
        confirm = messagebox.askyesno("Confirm Clear", "Are you sure you want to delete all saved BMI records?")
        if confirm:
            self.history_records = []
            self._write_history_file()
            self._refresh_history_table()
            self.render_chart()

    def export_csv(self):
        if not self.history_records:
            messagebox.showinfo("Empty History", "No records to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")],
            title="Export BMI History to CSV"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Date & Time", "Weight", "Height", "BMI", "Classification"])
                for r in self.history_records:
                    writer.writerow([
                        r.get("date"),
                        r.get("display_wt", r.get("weight")),
                        r.get("display_ht", "N/A"),
                        r.get("bmi"),
                        r.get("category")
                    ])
            messagebox.showinfo("Export Successful", f"Saved {len(self.history_records)} records to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred while saving CSV: {e}")

    def load_sample_history(self):
        """Populates realistic sample data to immediately demonstrate trend analytics."""
        sample_data = [
            {"id": "20260501090000", "timestamp": 1777604400, "date": "2026-05-01 09:00", "short_date": "May 01", "weight": 79.5, "unit": "kg", "display_wt": "79.5 kg", "display_ht": "175.0 cm", "bmi": 25.96, "category": "Overweight"},
            {"id": "20260601090000", "timestamp": 1780282800, "date": "2026-06-01 09:00", "short_date": "Jun 01", "weight": 77.8, "unit": "kg", "display_wt": "77.8 kg", "display_ht": "175.0 cm", "bmi": 25.40, "category": "Overweight"},
            {"id": "20260701090000", "timestamp": 1782874800, "date": "2026-07-01 09:00", "short_date": "Jul 01", "weight": 75.6, "unit": "kg", "display_wt": "75.6 kg", "display_ht": "175.0 cm", "bmi": 24.69, "category": "Normal Weight"},
            {"id": "20260801090000", "timestamp": 1785553200, "date": "2026-08-01 09:00", "short_date": "Aug 01", "weight": 74.0, "unit": "kg", "display_wt": "74.0 kg", "display_ht": "175.0 cm", "bmi": 24.16, "category": "Normal Weight"},
            {"id": "20260901090000", "timestamp": 1788231600, "date": "2026-09-01 09:00", "short_date": "Sep 01", "weight": 72.5, "unit": "kg", "display_wt": "72.5 kg", "display_ht": "175.0 cm", "bmi": 23.67, "category": "Normal Weight"},
            {"id": "20261001090000", "timestamp": 1790823600, "date": "2026-10-01 09:00", "short_date": "Oct 01", "weight": 71.0, "unit": "kg", "display_wt": "71.0 kg", "display_ht": "175.0 cm", "bmi": 23.18, "category": "Normal Weight"},
        ]
        self.history_records = sample_data
        self._write_history_file()
        self._refresh_history_table()
        self.switch_chart_tab("trend")
        messagebox.showinfo("Sample Loaded", "Sample 6-month progress data loaded! Check the 'Historical Progress Trend' chart.")

    def reset_inputs(self):
        if self.unit_system.get() == "metric":
            self.metric_weight_var.set("70.0")
            self.metric_height_var.set("175.0")
        else:
            self.imp_weight_var.set("154.0")
            self.imp_height_ft_var.set("5")
            self.imp_height_in_var.set("9")
        self.calculate_bmi(save=False)


def main():
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
