# views/login.py
import customtkinter as ctk
from tkinter import messagebox
from models.user import User


# ══════════════════════════════════════════════════════════════
# SHARED HELPERS
# ══════════════════════════════════════════════════════════════

def _entry(parent, placeholder, show=None):
    return ctk.CTkEntry(
        parent, placeholder_text=placeholder,
        height=40, fg_color="#0F1117",
        border_color="#2A3148", text_color="#E8ECF4",
        corner_radius=8, font=("Segoe UI", 12),
        show=show or ""
    )

def _label(parent, text, size=11, color="#7A849E", bold=False):
    font = ("Segoe UI", size, "bold") if bold else ("Segoe UI", size)
    return ctk.CTkLabel(parent, text=text, font=font, text_color=color)

def _logo_block(parent):
    """Reusable PLV logo + title block."""
    top = ctk.CTkFrame(parent, fg_color="transparent")
    top.pack(pady=(48, 0), padx=40, fill="x")
    _label(top, "◈", size=48, color="#4F8EF7").pack()
    _label(top, "PLV — SGMS", size=20, color="#E8ECF4", bold=True).pack(pady=(6, 2))
    _label(top, "Student Grade Management System", size=11).pack()
    ctk.CTkFrame(parent, fg_color="#2A3148", height=1).pack(fill="x", padx=40, pady=(24, 0))


# ══════════════════════════════════════════════════════════════
# REGISTER WINDOW
# ══════════════════════════════════════════════════════════════

class RegisterWindow(ctk.CTkToplevel):
    """
    Registration form — opened from LoginWindow.
    On success, closes itself and pre-fills the login form.
    """

    ROLES = ["admin", "teacher", "student"]

    def __init__(self, parent: "LoginWindow"):
        super().__init__(parent)
        self._parent = parent
        self.title("PLV — Create Account")
        self.geometry("460x620")
        self.resizable(False, False)
        self.configure(fg_color="#0F1117")
        self.grab_set()          # modal — blocks LoginWindow until closed
        self._build()
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        # ── Header ───────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(28, 0))

        _label(hdr, "◈", size=28, color="#4F8EF7").pack(side="left", padx=(0, 10))
        title_box = ctk.CTkFrame(hdr, fg_color="transparent")
        title_box.pack(side="left")
        _label(title_box, "Create Account", size=16, color="#E8ECF4", bold=True).pack(anchor="w")
        _label(title_box, "PLV — Student Grade Management System", size=10).pack(anchor="w")

        ctk.CTkFrame(self, fg_color="#2A3148", height=1).pack(fill="x", padx=28, pady=(16, 0))

        # ── Card ─────────────────────────────────────────────────
        card = ctk.CTkFrame(self, fg_color="#1E2433", corner_radius=16,
                            border_width=1, border_color="#2A3148")
        card.pack(padx=28, pady=16, fill="both", expand=True)

        _label(card, "Fill in your account details", size=12,
               color="#E8ECF4", bold=True).pack(anchor="w", padx=20, pady=(18, 14))

        # Username
        _label(card, "Username", size=11).pack(anchor="w", padx=20)
        self._username = _entry(card, "Choose a username")
        self._username.pack(fill="x", padx=20, pady=(4, 10))

        # Password
        _label(card, "Password", size=11).pack(anchor="w", padx=20)
        self._password = _entry(card, "Choose a password", show="•")
        self._password.pack(fill="x", padx=20, pady=(4, 10))

        # Confirm Password
        _label(card, "Confirm Password", size=11).pack(anchor="w", padx=20)
        self._confirm = _entry(card, "Re-enter your password", show="•")
        self._confirm.pack(fill="x", padx=20, pady=(4, 10))

        # Role
        _label(card, "Role", size=11).pack(anchor="w", padx=20)
        self._role_cb = ctk.CTkComboBox(
            card, values=self.ROLES,
            height=40, width=200,
            fg_color="#0F1117", border_color="#2A3148",
            button_color="#4F8EF7", text_color="#E8ECF4",
            corner_radius=8, dropdown_fg_color="#1E2433",
            font=("Segoe UI", 12)
        )
        self._role_cb.set("admin")
        self._role_cb.pack(anchor="w", padx=20, pady=(4, 10))

        # Show password toggle
        self._show_pw = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            card, text="Show passwords",
            variable=self._show_pw, command=self._toggle_pw,
            font=("Segoe UI", 11), text_color="#7A849E",
            fg_color="#4F8EF7", hover_color="#253050", border_color="#2A3148"
        ).pack(anchor="w", padx=20, pady=(0, 4))

        # Error label
        self._err = _label(card, "", size=11, color="#F75F5F")
        self._err.pack(padx=20, pady=(0, 4))

        # Buttons
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(4, 20))

        ctk.CTkButton(
            btn_row, text="Cancel",
            height=42, corner_radius=10,
            fg_color="#2A3148", hover_color="#1F3A6E",
            font=("Segoe UI", 12, "bold"), text_color="#7A849E",
            command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        self._reg_btn = ctk.CTkButton(
            btn_row, text="Create Account",
            height=42, corner_radius=10,
            fg_color="#4F8EF7", hover_color="#253050",
            font=("Segoe UI", 12, "bold"), text_color="white",
            command=self._attempt_register
        )
        self._reg_btn.pack(side="left", expand=True, fill="x")

        self.bind("<Return>", lambda e: self._attempt_register())
        self._username.focus()

    # ── Logic ─────────────────────────────────────────────────

    def _toggle_pw(self):
        show = "" if self._show_pw.get() else "•"
        self._password.configure(show=show)
        self._confirm.configure(show=show)

    def _show_error(self, msg):
        self._err.configure(text=msg)

    def _attempt_register(self):
        username = self._username.get().strip()
        password = self._password.get().strip()
        confirm  = self._confirm.get().strip()
        role     = self._role_cb.get()

        # Validation
        if not username or not password or not confirm:
            self._show_error("All fields are required.")
            return
        if len(username) < 3:
            self._show_error("Username must be at least 3 characters.")
            return
        if len(password) < 6:
            self._show_error("Password must be at least 6 characters.")
            return
        if password != confirm:
            self._show_error("Passwords do not match.")
            return

        self._reg_btn.configure(text="Creating...", state="disabled")
        self.update()

        try:
            User.create(username, password, role=role)
            messagebox.showinfo(
                "Account Created",
                f"Account '{username}' created successfully!\nYou can now log in."
            )
            # Pre-fill username in login form
            self._parent._username.delete(0, "end")
            self._parent._username.insert(0, username)
            self._parent._password.focus()
            self.destroy()

        except ValueError as e:
            self._reg_btn.configure(text="Create Account", state="normal")
            self._show_error(str(e))
        except Exception as e:
            self._reg_btn.configure(text="Create Account", state="normal")
            self._show_error(f"Unexpected error: {e}")


# ══════════════════════════════════════════════════════════════
# LOGIN WINDOW
# ══════════════════════════════════════════════════════════════

class LoginWindow(ctk.CTk):
    """
    Splash login screen. Has a 'Create Account' link that opens RegisterWindow.
    On successful login: destroys itself and opens App().
    """

    def __init__(self):
        super().__init__()
        self.title("PLV — Student Grade Management System")
        self.geometry("450x620")
        self.resizable(False, False)
        self.configure(fg_color="#0F1117")
        self._build()
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        # Logo
        _logo_block(self)

        # ── Form card ────────────────────────────────────────────
        card = ctk.CTkFrame(self, fg_color="#1E2433", corner_radius=16,
                            border_width=1, border_color="#2A3148")
        card.pack(padx=40, pady=20, fill="x")

        _label(card, "Sign in to your account", size=13,
               color="#E8ECF4", bold=True).pack(anchor="w", padx=20, pady=(20, 14))

        # Username
        _label(card, "Username").pack(anchor="w", padx=20)
        self._username = _entry(card, "Enter username")
        self._username.pack(fill="x", padx=20, pady=(4, 12))

        # Password
        _label(card, "Password").pack(anchor="w", padx=20)
        self._password = _entry(card, "Enter password", show="•")
        self._password.pack(fill="x", padx=20, pady=(4, 6))

        # Show password
        self._show_pw = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            card, text="Show password",
            variable=self._show_pw, command=self._toggle_password,
            font=("Segoe UI", 11), text_color="#7A849E",
            fg_color="#4F8EF7", hover_color="#253050", border_color="#2A3148"
        ).pack(anchor="w", padx=20, pady=(0, 6))

        # Error label
        self._err_label = _label(card, "", size=11, color="#F75F5F")
        self._err_label.pack(padx=20, pady=(0, 4))

        # Sign In button
        self._login_btn = ctk.CTkButton(
            card, text="Sign In", height=42, corner_radius=10,
            fg_color="#4F8EF7", hover_color="#253050",
            font=("Segoe UI", 13, "bold"), text_color="white",
            command=self._attempt_login
        )
        self._login_btn.pack(fill="x", padx=20, pady=(4, 12))

        # ── "Don't have an account?" row ─────────────────────────
        sep = ctk.CTkFrame(card, fg_color="transparent")
        sep.pack(fill="x", padx=20, pady=(0, 16))

        _label(sep, "Don't have an account?", size=11).pack(side="left")
        ctk.CTkButton(
            sep, text="Create one",
            font=("Segoe UI", 11, "bold"),
            text_color="#4F8EF7",
            fg_color="transparent",
            hover_color="#161B27",
            height=24, corner_radius=6,
            command=self._open_register
        ).pack(side="left", padx=(4, 0))

        # Footer
        _label(self, "IM 102 · Advance Database Systems · AY 2025-2026",
               size=10, color="#2A3148").pack(side="bottom", pady=14)

        self.bind("<Return>", lambda e: self._attempt_login())
        self._username.focus()

    # ── Logic ─────────────────────────────────────────────────

    def _toggle_password(self):
        self._password.configure(show="" if self._show_pw.get() else "•")

    def _show_error(self, msg):
        self._err_label.configure(text=msg)

    def _open_register(self):
        RegisterWindow(self)

    def _attempt_login(self):
        username = self._username.get().strip()
        password = self._password.get().strip()

        if not username or not password:
            self._show_error("Please enter both username and password.")
            return

        self._login_btn.configure(text="Signing in...", state="disabled")
        self.update()

        user = User.login(username, password)

        if user:
            self._open_dashboard(user)
        else:
            self._login_btn.configure(text="Sign In", state="normal")
            self._show_error("Incorrect username or password.")
            self._password.delete(0, "end")
            self._password.focus()

    def _open_dashboard(self, user):
        from views.dashboard import App
        self.destroy()
        App(current_user=user).mainloop()