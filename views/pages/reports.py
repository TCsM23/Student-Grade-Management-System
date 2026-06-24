"""
ReportsPage — embeds Seaborn/Matplotlib figures inside Tkinter
using FigureCanvasTkAgg. Calls analytics/pipeline.py for all charts.
"""

import customtkinter as ctk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

from config import (
    CLR_BG, CLR_CARD, CLR_BORDER, CLR_TEXT, CLR_SUBTEXT,
    CLR_ACCENT, CLR_HOVER, CLR_SIDEBAR,
    FONT_TITLE, FONT_HEAD, FONT_LABEL, FONT_SMALL, FONT_BTN
)
from db import query
from analytics.pipeline import (
    get_grade_distribution,
    get_section_avg,
    get_course_avg,
    get_pass_fail_pie,
    get_student_trend,
    get_grade_heatmap,
    get_score_boxplot,
)


# ── Helper: accent button (copied from widgets to keep page self-contained) ──
def _btn(parent, text, command, color=None):
    return ctk.CTkButton(
        parent, text=text, command=command,
        height=34, corner_radius=8,
        fg_color=color or CLR_ACCENT,
        hover_color=CLR_HOVER,
        font=FONT_BTN, text_color="white"
    )


class ReportsPage(ctk.CTkFrame):
    """
    Reports & Analytics page.
    Layout:
      ┌─ left sidebar ──────┬─ chart canvas ───────────────┐
      │  Chart selector     │  Selected chart renders here  │
      │  Term filter        │                               │
      │  Student filter     │                               │
      └─────────────────────┴───────────────────────────────┘
    """

    CHARTS = [
        ("Grade Distribution",         "distribution"),
        ("Section Average",            "section_avg"),
        ("Course Average",             "course_avg"),
        ("Pass / Fail Breakdown",      "pass_fail"),
        ("Score Boxplot per Course",   "boxplot"),
        ("Section × Course Heatmap",   "heatmap"),
        ("Student Grade Trend",        "student_trend"),
    ]

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._current_canvas = None
        self._selected_chart = ctk.StringVar(value="distribution")
        self._build()

    # ─────────────────────────────────────────────────────────
    # BUILD
    # ─────────────────────────────────────────────────────────

    def _build(self):
        # Page title
        ctk.CTkLabel(
            self, text="Reports & Analytics",
            font=FONT_TITLE, text_color=CLR_TEXT
        ).pack(anchor="w", pady=(0, 16))

        # Main split: left controls + right canvas
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_sidebar(body)
        self._build_canvas_area(body)

        # Load default chart
        self._render_chart()

    def _build_sidebar(self, parent):
        side = ctk.CTkFrame(
            parent, fg_color=CLR_CARD,
            corner_radius=12, border_width=1,
            border_color=CLR_BORDER, width=210
        )
        side.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        side.pack_propagate(False)

        ctk.CTkLabel(
            side, text="Charts",
            font=FONT_HEAD, text_color=CLR_TEXT
        ).pack(anchor="w", padx=16, pady=(16, 8))

        # Chart selector buttons
        for label, key in self.CHARTS:
            btn = ctk.CTkButton(
                side,
                text=label,
                anchor="w",
                height=36,
                corner_radius=8,
                fg_color="transparent",
                hover_color=CLR_HOVER,
                text_color=CLR_SUBTEXT,
                font=FONT_SMALL,
                command=lambda k=key: self._select_chart(k)
            )
            btn.pack(fill="x", padx=10, pady=2)

        # Divider
        ctk.CTkFrame(side, fg_color=CLR_BORDER, height=1).pack(
            fill="x", padx=16, pady=(12, 12)
        )

        # ── Term filter ──────────────────────────────────────
        ctk.CTkLabel(
            side, text="Filter by Term",
            font=FONT_SMALL, text_color=CLR_SUBTEXT
        ).pack(anchor="w", padx=16)

        terms = query(
            "SELECT term_id, CONCAT(semester,' ',school_year) AS label FROM term ORDER BY term_id DESC"
        )
        term_options = ["All Terms"] + [f"{t['term_id']} — {t['label']}" for t in terms]

        self._term_cb = ctk.CTkComboBox(
            side, values=term_options,
            width=180, height=32,
            fg_color=CLR_BG, border_color=CLR_BORDER,
            button_color=CLR_ACCENT, text_color=CLR_TEXT,
            dropdown_fg_color=CLR_CARD, corner_radius=8,
            command=lambda _: self._render_chart()
        )
        self._term_cb.set("All Terms")
        self._term_cb.pack(padx=16, pady=(4, 12))

        # ── Student filter (for trend chart) ─────────────────
        ctk.CTkLabel(
            side, text="Student (for Trend chart)",
            font=FONT_SMALL, text_color=CLR_SUBTEXT
        ).pack(anchor="w", padx=16)

        students = query(
            "SELECT stud_id, CONCAT(stud_no,' - ',stud_fname,' ',stud_lname) AS label "
            "FROM student WHERE stud_status='A' ORDER BY stud_lname"
        )
        self._stud_map = {s["label"]: s["stud_id"] for s in students}
        stud_options  = list(self._stud_map.keys())

        self._stud_cb = ctk.CTkComboBox(
            side, values=stud_options or ["No students"],
            width=180, height=32,
            fg_color=CLR_BG, border_color=CLR_BORDER,
            button_color=CLR_ACCENT, text_color=CLR_TEXT,
            dropdown_fg_color=CLR_CARD, corner_radius=8,
            command=lambda _: self._render_chart()
        )
        if stud_options:
            self._stud_cb.set(stud_options[0])
        self._stud_cb.pack(padx=16, pady=(4, 12))

        # Refresh button
        _btn(side, "🔄  Refresh", self._render_chart, color=CLR_SIDEBAR).pack(
            fill="x", padx=16, pady=(4, 16)
        )

    def _build_canvas_area(self, parent):
        """Right side: loading label + chart frame."""
        right = ctk.CTkFrame(
            parent, fg_color=CLR_CARD,
            corner_radius=12, border_width=1,
            border_color=CLR_BORDER
        )
        right.grid(row=0, column=1, sticky="nsew")

        self._loading_label = ctk.CTkLabel(
            right, text="Loading chart...",
            font=FONT_LABEL, text_color=CLR_SUBTEXT
        )
        self._loading_label.pack(expand=True)

        self._chart_frame = right

    # ─────────────────────────────────────────────────────────
    # CHART SELECTION + RENDERING
    # ─────────────────────────────────────────────────────────

    def _select_chart(self, key):
        self._selected_chart.set(key)
        self._render_chart()

    def _get_term_id(self):
        sel = self._term_cb.get()
        if sel == "All Terms":
            return None
        try:
            return int(sel.split("—")[0].strip())
        except (ValueError, IndexError):
            return None

    def _render_chart(self):
        """Run chart generation in a background thread, then embed result."""
        self._show_loading()
        thread = threading.Thread(target=self._generate_and_embed, daemon=True)
        thread.start()

    def _show_loading(self):
        if self._current_canvas:
            self._current_canvas.get_tk_widget().destroy()
            self._current_canvas = None
        self._loading_label.configure(text="Loading chart...")
        self._loading_label.pack(expand=True)

    def _generate_and_embed(self):
        """Runs in background thread — generates the figure then schedules UI update."""
        try:
            fig = self._get_figure()
        except Exception as e:
            self.after(0, lambda: self._show_error(str(e)))
            return
        self.after(0, lambda: self._embed_figure(fig))

    def _get_figure(self):
        """Call the correct pipeline function based on selected chart."""
        key     = self._selected_chart.get()
        term_id = self._get_term_id()

        if key == "distribution":
            return get_grade_distribution(term_id)
        elif key == "section_avg":
            return get_section_avg(term_id)
        elif key == "course_avg":
            return get_course_avg()
        elif key == "pass_fail":
            return get_pass_fail_pie(term_id)
        elif key == "boxplot":
            return get_score_boxplot(term_id)
        elif key == "heatmap":
            return get_grade_heatmap(term_id)
        elif key == "student_trend":
            stud_label = self._stud_cb.get()
            stud_id    = self._stud_map.get(stud_label)
            if not stud_id:
                raise ValueError("Please select a student for the trend chart.")
            return get_student_trend(stud_id)
        else:
            raise ValueError(f"Unknown chart key: {key}")

    def _embed_figure(self, fig):
        """Embed a matplotlib Figure into the chart frame (runs on main thread)."""
        self._loading_label.pack_forget()

        if self._current_canvas:
            self._current_canvas.get_tk_widget().destroy()

        canvas = FigureCanvasTkAgg(fig, master=self._chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        self._current_canvas = canvas

    def _show_error(self, message):
        self._loading_label.configure(
            text=f"Chart error:\n{message}", text_color="#F75F5F"
        )
        self._loading_label.pack(expand=True)