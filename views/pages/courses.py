import customtkinter as ctk
from tkinter import messagebox
from config import CLR_BG, CLR_CARD, CLR_BORDER, CLR_TEXT, CLR_RED, FONT_TITLE, FONT_HEAD, FONT_SMALL
from db import query, execute
from views.widgets import styled_table, accent_btn, form_field


class CoursesPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._selected_id = None
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(header, text="Courses", font=FONT_TITLE,
                     text_color=CLR_TEXT).pack(side="left")
        accent_btn(header, "+ Add Course", self._open_add).pack(side="right")

        cols = ["ID", "Code", "Title", "Units"]
        widths = [50, 100, 300, 60]
        self.tree, _ = styled_table(self, cols, widths)
        self.tree.bind("<<TreeviewSelect>>",
                       lambda e: setattr(self, "_selected_id",
                                         int(self.tree.selection()[0]) if self.tree.selection() else None))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", pady=(10, 0))
        accent_btn(btn_row, "✏️  Edit",   self._open_edit).pack(side="left", padx=(0, 8))
        accent_btn(btn_row, "🗑  Delete", self._delete, color=CLR_RED).pack(side="left")
        accent_btn(btn_row, "🔄 Refresh", self._load, color=CLR_CARD).pack(side="right")
        self._load()

    def _load(self):
        rows = query("SELECT * FROM course ORDER BY course_code")
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", iid=r["course_id"], values=(
                r["course_id"], r["course_code"], r["course_title"], r["course_units"]
            ))

    def _open_add(self):
        CourseForm(self, mode="add", on_save=self._load)

    def _open_edit(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Please select a course first.")
            return
        row = query("SELECT * FROM course WHERE course_id=%s",
                    (self._selected_id,), fetch="one")
        CourseForm(self, mode="edit", data=row, on_save=self._load)

    def _delete(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Please select a course first.")
            return
        if messagebox.askyesno("Confirm", "Delete this course?"):
            execute("DELETE FROM course WHERE course_id=%s", (self._selected_id,))
            self._load()


class CourseForm(ctk.CTkToplevel):
    def __init__(self, parent, mode="add", data=None, on_save=None):
        super().__init__(parent)
        self.title("Add Course" if mode=="add" else "Edit Course")
        self.geometry("400x260")
        self.configure(fg_color=CLR_BG)
        self.grab_set()
        self._mode = mode
        self._data = data or {}
        self._on_save = on_save
        self._build()

    def _build(self):
        ctk.CTkLabel(self,
                     text="Add Course" if self._mode=="add" else "Edit Course",
                     font=FONT_HEAD, text_color=CLR_TEXT).pack(
                     anchor="w", padx=20, pady=(16, 10))
        form = ctk.CTkFrame(self, fg_color=CLR_CARD, corner_radius=12)
        form.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.e_code  = form_field(form, "Course Code",  0)
        self.e_title = form_field(form, "Course Title", 1)
        self.e_units = form_field(form, "Units",        2)

        if self._data:
            for e, k in [(self.e_code, "course_code"),
                         (self.e_title, "course_title"),
                         (self.e_units, "course_units")]:
                e.insert(0, self._data.get(k) or "")

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.grid(row=4, column=0, columnspan=2, pady=14, padx=10, sticky="e")
        accent_btn(btn_row, "Cancel", self.destroy, color=CLR_CARD).pack(side="left", padx=(0,8))
        accent_btn(btn_row, "Save",   self._save).pack(side="left")

    def _save(self):
        code  = self.e_code.get().strip()
        title = self.e_title.get().strip()
        try:
            units = int(self.e_units.get().strip())
        except ValueError:
            messagebox.showwarning("Validation", "Units must be a number.")
            return
        if not code or not title:
            messagebox.showwarning("Validation", "Code and title are required.")
            return
        if self._mode == "add":
            execute("INSERT INTO course (course_code, course_title, course_units) VALUES (%s,%s,%s)",
                    (code, title, units))
        else:
            execute("UPDATE course SET course_code=%s, course_title=%s, course_units=%s WHERE course_id=%s",
                    (code, title, units, self._data["course_id"]))
        if self._on_save:
            self._on_save()
        self.destroy()