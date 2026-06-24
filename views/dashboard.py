# views/dashboard.py
import customtkinter as ctk
from config import (
    CLR_BG, CLR_SIDEBAR, CLR_BORDER, CLR_TEXT,
    CLR_SUBTEXT, CLR_ACCENT, CLR_HOVER, CLR_SEL,
    FONT_SMALL, FONT_LABEL
)
from views.pages.dashboard import DashboardPage
from views.pages.students  import StudentsPage
from views.pages.grades    import GradesPage
from views.pages.courses   import CoursesPage
from views.pages.reports   import ReportsPage


class App(ctk.CTk):
    """
    Main application window — sidebar nav + page container.
    Receives the logged-in user dict from LoginWindow.
    """

    def __init__(self, current_user=None):
        super().__init__()
        self._user = current_user or {}
        self.title("Student Grade Management System — PLV")
        self.geometry("1200x720")
        self.minsize(900, 600)
        self.configure(fg_color=CLR_BG)
        self._build_sidebar()
        self._build_main()
        self._show_page("Dashboard")

    # ─────────────────────────────────────────────────────────
    # SIDEBAR
    # ─────────────────────────────────────────────────────────

    def _build_sidebar(self):
        self._sidebar = ctk.CTkFrame(
            self, fg_color=CLR_SIDEBAR, width=220, corner_radius=0
        )
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Logo
        logo = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        logo.pack(fill="x", pady=(24, 8), padx=16)
        ctk.CTkLabel(
            logo, text="◈",
            font=("Segoe UI", 28), text_color=CLR_ACCENT
        ).pack(side="left")
        title_box = ctk.CTkFrame(logo, fg_color="transparent")
        title_box.pack(side="left", padx=10)
        ctk.CTkLabel(
            title_box, text="PLV — SGMS",
            font=("Segoe UI", 13, "bold"), text_color=CLR_TEXT
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_box, text="Grade Management",
            font=FONT_SMALL, text_color=CLR_SUBTEXT
        ).pack(anchor="w")

        # Logged-in user chip
        role  = self._user.get("role", "guest").capitalize()
        uname = self._user.get("username", "")
        ctk.CTkLabel(
            self._sidebar,
            text=f"  👤  {uname}  ·  {role}",
            font=("Segoe UI", 10),
            text_color=CLR_SUBTEXT,
            fg_color=CLR_BORDER,
            corner_radius=6
        ).pack(fill="x", padx=16, pady=(0, 4))

        # Divider
        ctk.CTkFrame(
            self._sidebar, fg_color=CLR_BORDER, height=1
        ).pack(fill="x", padx=16, pady=(4, 16))

        # Nav items
        nav_items = [
            ("Dashboard", "⊞"),
            ("Students",  "👤"),
            ("Grades",    "📋"),
            ("Courses",   "📚"),
            ("Reports",   "📊"),
        ]
        self._nav_btns = {}
        for label, icon in nav_items:
            btn = ctk.CTkButton(
                self._sidebar,
                text=f"  {icon}  {label}",
                anchor="w", height=44,
                corner_radius=10,
                fg_color="transparent",
                hover_color=CLR_HOVER,
                text_color=CLR_SUBTEXT,
                font=FONT_LABEL,
                command=lambda l=label: self._show_page(l)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._nav_btns[label] = btn

        # Logout button at bottom
        ctk.CTkButton(
            self._sidebar,
            text="  🚪  Logout",
            anchor="w", height=40,
            corner_radius=10,
            fg_color="transparent",
            hover_color=CLR_HOVER,
            text_color=CLR_SUBTEXT,
            font=FONT_SMALL,
            command=self._logout
        ).pack(side="bottom", fill="x", padx=10, pady=(0, 8))

        ctk.CTkLabel(
            self._sidebar,
            text="IM 102 · AY 2025-2026",
            font=FONT_SMALL, text_color=CLR_BORDER
        ).pack(side="bottom", pady=(0, 4))

    # ─────────────────────────────────────────────────────────
    # MAIN CONTENT AREA
    # ─────────────────────────────────────────────────────────

    def _build_main(self):
        self._main = ctk.CTkFrame(self, fg_color=CLR_BG, corner_radius=0)
        self._main.pack(side="right", fill="both", expand=True, padx=28, pady=24)

    def _show_page(self, name):
        # Highlight active nav button
        for lbl, btn in self._nav_btns.items():
            if lbl == name:
                btn.configure(fg_color=CLR_SEL, text_color=CLR_ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=CLR_SUBTEXT)

        # Destroy previous page
        for w in self._main.winfo_children():
            w.destroy()

        pages = {
            "Dashboard": DashboardPage,
            "Students":  StudentsPage,
            "Grades":    GradesPage,
            "Courses":   CoursesPage,
            "Reports":   ReportsPage,
        }
        if name in pages:
            page = pages[name](self._main)
            page.pack(fill="both", expand=True)

    # ─────────────────────────────────────────────────────────
    # LOGOUT
    # ─────────────────────────────────────────────────────────

    def _logout(self):
        from tkinter import messagebox
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            from views.login import LoginWindow
            self.destroy()
            LoginWindow().mainloop()