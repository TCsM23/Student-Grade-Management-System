import customtkinter as ctk
from tkinter import ttk, messagebox
from config import CLR_BG, CLR_CARD, CLR_BORDER, CLR_TEXT, CLR_SUBTEXT, CLR_RED, FONT_TITLE, FONT_HEAD, FONT_LABEL, FONT_SMALL
from db import query, execute
from views.widgets import styled_table, accent_btn, form_field

# student UI
class StudentsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._selected_id = None
        self._build()

    def _build(self):
        # Header row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(header, text="Students", font=FONT_TITLE,
                     text_color=CLR_TEXT).pack(side="left")
        accent_btn(header, "+ Add Student", self._open_add).pack(side="right")

        # Search bar
        search_frame = ctk.CTkFrame(self, fg_color=CLR_CARD,
                                    corner_radius=10, border_width=1,
                                    border_color=CLR_BORDER)
        search_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(search_frame, text="🔍", font=("Segoe UI", 14),
                     text_color=CLR_SUBTEXT).pack(side="left", padx=(14, 4), pady=8)
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._load())
        ctk.CTkEntry(search_frame, textvariable=self._search_var,
                     placeholder_text="Search by name or student number...",
                     height=34, fg_color="transparent", border_width=0,
                     text_color=CLR_TEXT, font=FONT_LABEL).pack(
                     side="left", fill="x", expand=True, padx=4)

        # Table
        cols = ["ID", "Stud No", "First Name", "Last Name",
                "Program", "Year", "Section", "Status"]
        widths = [50, 100, 120, 120, 60, 50, 90, 70]
        self.tree, _ = styled_table(self, cols, widths)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Action buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", pady=(10, 0))
        accent_btn(btn_row, "✏️  Edit",   self._open_edit).pack(side="left", padx=(0, 8))
        accent_btn(btn_row, "🗑  Delete", self._delete,
                   color=CLR_RED).pack(side="left")
        accent_btn(btn_row, "🔄 Refresh", self._load,
                   color=CLR_CARD).pack(side="right")

        self._load()

    def _load(self):
        kw = self._search_var.get().strip()
        if kw:
            rows = query("""
                SELECT stud_id, stud_no, stud_fname, stud_lname,
                       prog_id, year_level, section, stud_status
                FROM student
                WHERE stud_fname LIKE %s OR stud_lname LIKE %s OR stud_no LIKE %s
                ORDER BY stud_lname
            """, (f"%{kw}%", f"%{kw}%", f"%{kw}%"))
        else:
            rows = query("""
                SELECT stud_id, stud_no, stud_fname, stud_lname,
                       prog_id, year_level, section, stud_status
                FROM student ORDER BY stud_lname
            """)
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", iid=r["stud_id"], values=(
                r["stud_id"], r["stud_no"], r["stud_fname"], r["stud_lname"],
                r["prog_id"], r["year_level"], r["section"],
                "Active" if r["stud_status"] == "A" else "Inactive"
            ))

    def _on_select(self, _):
        sel = self.tree.selection()
        self._selected_id = int(sel[0]) if sel else None

    def _open_add(self):
        StudentForm(self, mode="add", on_save=self._load)

    def _open_edit(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Please select a student first.")
            return
        row = query("SELECT * FROM student WHERE stud_id=%s",
                    (self._selected_id,), fetch="one")
        StudentForm(self, mode="edit", data=row, on_save=self._load)

    def _delete(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Please select a student first.")
            return
        if messagebox.askyesno("Confirm", "Set student as Inactive?"):
            execute("UPDATE student SET stud_status='I' WHERE stud_id=%s",
                    (self._selected_id,))
            self._load()


class StudentForm(ctk.CTkToplevel):
    def __init__(self, parent, mode="add", data=None, on_save=None):
        super().__init__(parent)
        self.title("Add Student" if mode == "add" else "Edit Student")
        self.geometry("540x420")
        self.configure(fg_color=CLR_BG)
        self.grab_set()
        self._mode = mode
        self._data = data or {}
        self._on_save = on_save
        self._build()

    def _build(self):
        ctk.CTkLabel(self,
                     text="Add Student" if self._mode=="add" else "Edit Student",
                     font=FONT_HEAD, text_color=CLR_TEXT).pack(
                     anchor="w", padx=20, pady=(16, 10))
        form = ctk.CTkFrame(self, fg_color=CLR_CARD, corner_radius=12)
        form.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.e_no    = form_field(form, "Student No", 0, 0)
        self.e_fname = form_field(form, "First Name", 1, 0)
        self.e_lname = form_field(form, "Last Name",  2, 0)
        self.e_prog  = form_field(form, "Program ID", 0, 1)
        self.e_year  = form_field(form, "Year Level", 1, 1)
        self.e_sec   = form_field(form, "Section",    2, 1)
        self.e_email = form_field(form, "Email",      3, 0)
        self.e_phone = form_field(form, "Phone",      3, 1)

        if self._data:
            for entry, key in [
                (self.e_no,    "stud_no"),
                (self.e_fname, "stud_fname"),
                (self.e_lname, "stud_lname"),
                (self.e_prog,  "prog_id"),
                (self.e_year,  "year_level"),
                (self.e_sec,   "section"),
                (self.e_email, "stud_email"),
                (self.e_phone, "stud_phone"),
            ]:
                entry.insert(0, self._data.get(key) or "")

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.grid(row=5, column=0, columnspan=4, pady=14, padx=10, sticky="e")
        accent_btn(btn_row, "Cancel", self.destroy, color=CLR_CARD).pack(
            side="left", padx=(0, 8))
        accent_btn(btn_row, "Save", self._save).pack(side="left")

    def _save(self):
        vals = (
            self.e_no.get().strip(), self.e_fname.get().strip(),
            self.e_lname.get().strip(), self.e_prog.get().strip() or None,
            self.e_year.get().strip(), self.e_sec.get().strip(),
            self.e_email.get().strip() or None,
            self.e_phone.get().strip() or None,
        )
        if not all([vals[0], vals[1], vals[2], vals[4], vals[5]]):
            messagebox.showwarning("Validation", "Please fill in all required fields.")
            return
        try:
            prog_id   = int(vals[3]) if vals[3] else None
            year_level = int(vals[4])
        except ValueError:
            messagebox.showwarning("Validation", "Program ID and Year Level must be numbers.")
            return

        if self._mode == "add":
            execute("""
                INSERT INTO student
                    (stud_no, stud_fname, stud_lname, prog_id, year_level,
                     section, stud_email, stud_phone)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (vals[0], vals[1], vals[2], prog_id, year_level,
                  vals[5], vals[6], vals[7]))
        else:
            execute("""
                UPDATE student SET stud_no=%s, stud_fname=%s, stud_lname=%s,
                    prog_id=%s, year_level=%s, section=%s,
                    stud_email=%s, stud_phone=%s
                WHERE stud_id=%s
            """, (vals[0], vals[1], vals[2], prog_id, year_level,
                  vals[5], vals[6], vals[7], self._data["stud_id"]))
        if self._on_save:
            self._on_save()
        self.destroy()
