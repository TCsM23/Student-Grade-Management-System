import customtkinter as ctk
from tkinter import ttk
from config import CLR_TEXT, CLR_ACCENT, CLR_ACCENT2, CLR_YELLOW, CLR_RED, FONT_TITLE,FONT_HEAD
from db import query, get_stats
from views.widgets import metric_card, styled_table    

# pages
class DashboardPage(ctk. CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build()
    
    def _build(self):
        ctk.CTkLabel(self, text="Dashboard", font=FONT_TITLE,
                     text_color=CLR_TEXT).pack(anchor="w", pady=(0, 20))
        
        stats = get_stats()
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x")
        cards_frame.columnconfigure((0,1,2,3), weight=1, uniform="c")

        data = [
            ("Active Students", stats.get("students", 0), CLR_ACCENT),
            ("Courses", stats.get("courses", 0), CLR_ACCENT2),
            ("Currently Enrolled", stats.get("enrolled", 0), CLR_YELLOW),
            ("Failing", stats.get("failing", 0), CLR_RED),
        ]
        for i, (title, val, color) in enumerate(data):
            card = metric_card(cards_frame, title, val, color)
            card.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")

        # recent enrollments table
        ctk.CTkLabel(self, text="Recent Enrollments", font=FONT_HEAD,
                     text_color=CLR_TEXT).pack(anchor="w", pady=(28, 8))
        
        cols = ["Stud No", "Name", "Course", "Term", "Raw Score", "Grade", "Status"]
        widths = [90, 160, 180, 120, 90, 70, 90]
        self.tree, _ = styled_table(self, cols, widths)

        rows = query("""
            SELECT s.stud_no, CONCAT(s.stud_fname,' ',s.stud_lname) AS name,
                   c.course_code, CONCAT(t.semester,' ',t.school_year) AS term,
                   e.raw_score, e.final_grade, e.status
            FROM enrollment e
            JOIN student s USING(stud_id)
            JOIN course  c USING(course_id)
            JOIN term    t USING(term_id)
            ORDER BY e.enroll_id DESC LIMIT 20
        """)
        for r in rows:
            self.tree.insert("", "end", values=(
                r["stud_no"], r["name"], r["course_code"], r["term"],
                r["raw_score"] or "—",
                r["final_grade"] or "—", r["status"]
            ))