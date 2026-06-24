import customtkinter as ctk
from tkinter import ttk, messagebox
from config import CLR_BG, CLR_CARD, CLR_BORDER, CLR_TEXT, CLR_SUBTEXT, CLR_ACCENT, FONT_TITLE, FONT_HEAD, FONT_SMALL
from db import query, execute, compute_letters, compute_final
from views.widgets import styled_table, accent_btn, form_field, combo_field

# grades UI
class GradesPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._selected_id = None
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(header, text="Grade Entry", font=FONT_TITLE,
                     text_color=CLR_TEXT).pack(side="left")
        accent_btn(header, "+ Record Grade", self._open_add).pack(side="right")

        # Filters
        filter_frame = ctk.CTkFrame(self, fg_color=CLR_CARD,
                                    corner_radius=10, border_width=1,
                                    border_color=CLR_BORDER)
        filter_frame.pack(fill="x", pady=(0, 12))

        terms = query("SELECT term_id, CONCAT(semester,' ',school_year) AS label FROM term")
        term_labels = [f"{t['term_id']} — {t['label']}" for t in terms]

        ctk.CTkLabel(filter_frame, text="Filter by Term:",
                     font=FONT_SMALL, text_color=CLR_SUBTEXT).pack(
                     side="left", padx=(14, 6), pady=8)
        self._term_cb = ctk.CTkComboBox(filter_frame,
                                         values=["All"] + term_labels,
                                         width=200, height=30,
                                         fg_color=CLR_BG,
                                         border_color=CLR_BORDER,
                                         button_color=CLR_ACCENT,
                                         text_color=CLR_TEXT,
                                         dropdown_fg_color=CLR_CARD,
                                         command=lambda _: self._load())
        self._term_cb.set("All")
        self._term_cb.pack(side="left", pady=8)

        # Table
        cols = ["Enroll ID", "Stud No", "Name", "Course",
                "Term", "Raw Score", "Final Grade", "Letter", "Status"]
        widths = [70, 90, 150, 120, 120, 80, 90, 70, 90]
        self.tree, _ = styled_table(self, cols, widths)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._on_select())

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", pady=(10, 0))
        accent_btn(btn_row, "✏️  Edit Grade", self._open_edit).pack(side="left", padx=(0, 8))
        accent_btn(btn_row, "🔄 Refresh",     self._load, color=CLR_CARD).pack(side="right")

        self._load()

    def _load(self):
        term_sel = self._term_cb.get()
        if term_sel == "All":
            rows = query("""
                SELECT e.enroll_id, s.stud_no,
                       CONCAT(s.stud_fname,' ',s.stud_lname) AS name,
                       c.course_code,
                       CONCAT(t.semester,' ',t.school_year) AS term,
                       e.raw_score, e.final_grade, e.letter_grade, e.status
                FROM enrollment e
                JOIN student s USING(stud_id)
                JOIN course  c USING(course_id)
                JOIN term    t USING(term_id)
                ORDER BY e.enroll_id DESC
            """)
        else:
            tid = int(term_sel.split("—")[0].strip())
            rows = query("""
                SELECT e.enroll_id, s.stud_no,
                       CONCAT(s.stud_fname,' ',s.stud_lname) AS name,
                       c.course_code,
                       CONCAT(t.semester,' ',t.school_year) AS term,
                       e.raw_score, e.final_grade, e.letter_grade, e.status
                FROM enrollment e
                JOIN student s USING(stud_id)
                JOIN course  c USING(course_id)
                JOIN term    t USING(term_id)
                WHERE e.term_id = %s
                ORDER BY e.enroll_id DESC
            """, (tid,))

        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", iid=r["enroll_id"], values=(
                r["enroll_id"], r["stud_no"], r["name"], r["course_code"],
                r["term"],
                r["raw_score"] or "—",
                r["final_grade"] or "—",
                r["letter_grade"] or "—",
                r["status"]
            ))

    def _on_select(self):
        sel = self.tree.selection()
        self._selected_id = int(sel[0]) if sel else None

    def _open_add(self):
        GradeForm(self, mode="add", on_save=self._load)

    def _open_edit(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Please select a record first.")
            return
        row = query("SELECT * FROM enrollment WHERE enroll_id=%s",
                    (self._selected_id,), fetch="one")
        GradeForm(self, mode="edit", data=row, on_save=self._load)

class GradeForm(ctk.CTkToplevel):
    def __init__(self, parent, mode="add", data=None, on_save=None):
        super().__init__(parent)
        self.title("Record Grade" if mode == "add" else "Edit Grade")
        self.geometry("460x340")
        self.configure(fg_color=CLR_BG)
        self.grab_set()
        self._mode = mode
        self._data = data or {}
        self._on_save = on_save
        self._build()

    def _build(self):
        ctk.CTkLabel(self,
                     text="Record Grade" if self._mode=="add" else "Edit Grade",
                     font=FONT_HEAD, text_color=CLR_TEXT).pack(
                     anchor="w", padx=20, pady=(16, 10))
        form = ctk.CTkFrame(self, fg_color=CLR_CARD, corner_radius=12)
        form.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        students = query("SELECT stud_id, CONCAT(stud_no,' - ',stud_fname,' ',stud_lname) AS label FROM student WHERE stud_status='A' ORDER BY stud_lname")
        courses  = query("SELECT course_id, CONCAT(course_code,' - ',course_title) AS label FROM course ORDER BY course_code")
        terms    = query("SELECT term_id, CONCAT(semester,' ',school_year) AS label FROM term ORDER BY term_id DESC")

        self._stud_map   = {s["label"]: s["stud_id"] for s in students}
        self._course_map = {c["label"]: c["course_id"] for c in courses}
        self._term_map   = {t["label"]: t["term_id"] for t in terms}

        self.cb_stud  = combo_field(form, "Student",  0, list(self._stud_map.keys()))
        self.cb_course = combo_field(form, "Course",   1, list(self._course_map.keys()))
        self.cb_term  = combo_field(form, "Term",     2, list(self._term_map.keys()))
        self.e_raw    = form_field(form, "Raw Score (0-100)", 3, 0)

        if self._data:
            self.e_raw.insert(0, self._data.get("raw_score") or "")

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.grid(row=5, column=0, columnspan=4, pady=14, padx=10, sticky="e")
        accent_btn(btn_row, "Cancel", self.destroy, color=CLR_CARD).pack(side="left", padx=(0, 8))
        accent_btn(btn_row, "Save",   self._save).pack(side="left")

    def _save(self):
        raw_str = self.e_raw.get().strip()
        try:
            raw = float(raw_str) if raw_str else None
            if raw is not None and not (0 <= raw <= 100):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Raw score must be between 0 and 100.")
            return

        final  = compute_final(raw)
        letter = compute_letters(raw)

        if self._mode == "add":
            stud_id   = self._stud_map.get(self.cb_stud.get())
            course_id = self._course_map.get(self.cb_course.get())
            term_id   = self._term_map.get(self.cb_term.get())
            if not all([stud_id, course_id, term_id]):
                messagebox.showwarning("Validation", "Please select student, course, and term.")
                return
            execute("""
                INSERT INTO enrollment
                    (stud_id, course_id, term_id, raw_score, final_grade, letter_grade, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (stud_id, course_id, term_id, raw, final, letter,
                  "COMPLETED" if raw is not None else "ENROLLED"))
        else:
            execute("""
                UPDATE enrollment
                SET raw_score=%s, final_grade=%s, letter_grade=%s,
                    status=IF(%s IS NULL, 'ENROLLED', 'COMPLETED')
                WHERE enroll_id=%s
            """, (raw, final, letter, raw, self._data["enroll_id"]))

        if self._on_save:
            self._on_save()
        self.destroy()


