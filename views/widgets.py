import customtkinter as ctk
from tkinter import ttk
from config import CLR_BG, CLR_CARD, CLR_BORDER, CLR_TEXT, CLR_SUBTEXT, CLR_ACCENT, CLR_HOVER, CLR_SEL, CLR_SIDEBAR, FONT_CARD, FONT_SMALL, FONT_BTN, FONT_HEAD

# reusable widgets
def metric_card(parent, title, value, accent):
    card = ctk.CTkFrame(parent, fg_color=CLR_CARD, corner_radius=12,
                        border_width=1, border_color=CLR_BORDER)
    indicator = ctk.CTkFrame(card, fg_color=accent, corner_radius=6,
                             width=4, height=40)
    indicator.pack(side="left", padx=(14, 10), pady=18)
    indicator.pack_propagate(False)
    txt = ctk.CTkFrame(card, fg_color="transparent")
    txt.pack(side="left", fill="both", expand=True, pady=14, padx=(0, 14))
    ctk.CTkLabel(txt, text=str(value), font=FONT_CARD,
                 text_color=accent).pack(anchor="w")
    ctk.CTkLabel(txt, text=title, font=FONT_SMALL,
                 text_color=CLR_SUBTEXT).pack(anchor="w")
    return card

def section_header(parent, text):
    ctk.CTkLabel(parent, text=text, font=FONT_HEAD,
                 text_color=CLR_TEXT).pack(anchor="w", pady=(0, 10))

def styled_table(parent, columns, col_widths=None):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background=CLR_CARD, foreground=CLR_TEXT,
                    fieldbackground=CLR_CARD, borderwidth=0,
                    rowheight=34, font=("Segoe UI", 11))
    style.configure("Custom.Treeview.Heading",
                    background=CLR_SIDEBAR, foreground=CLR_ACCENT,
                    relief="flat", font=("Segoe UI", 11, "bold"))
    style.map("Custom.Treeview",
              background=[("selected", CLR_SEL)],
              foreground=[("selected", "#FFFFFF")])
    style.map("Custom.Treeview.Heading",
              background=[("active", CLR_HOVER)])

    frame = ctk.CTkFrame(parent, fg_color=CLR_CARD,
                         corner_radius=12, border_width=1,
                         border_color=CLR_BORDER)
    frame.pack(fill="both", expand=True)

    sb = ctk.CTkScrollbar(frame)
    sb.pack(side="right", fill="y", padx=(0, 4), pady=4)

    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        style="Custom.Treeview",
                        yscrollcommand=sb.set)
    sb.configure(command=tree.yview)

    for i, col in enumerate(columns):
        w = col_widths[i] if col_widths else 120
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center", stretch=True)

    tree.pack(fill="both", expand=True, padx=4, pady=4)
    return tree, frame

def form_field(parent, label, row, col=0):
    ctk.CTkLabel(parent, text=label, font=FONT_SMALL,
                 text_color=CLR_SUBTEXT).grid(row=row, column=col*2,
                 sticky="w", padx=(10, 4), pady=4)
    entry = ctk.CTkEntry(parent, height=34, width=180,
                         fg_color=CLR_BG, border_color=CLR_BORDER,
                         text_color=CLR_TEXT, corner_radius=8)
    entry.grid(row=row, column=col*2+1, padx=(0, 18), pady=4, sticky="w")
    return entry

def accent_btn(parent, text, command, color=None):
    return ctk.CTkButton(parent, text=text, command=command,
                         height=36, corner_radius=8,
                         fg_color=color or CLR_ACCENT,
                         hover_color=CLR_HOVER,
                         font=FONT_BTN, text_color="white")

def combo_field(parent, label, row, values, col=0):
    ctk.CTkLabel(parent, text=label, font=FONT_SMALL,
                 text_color=CLR_SUBTEXT).grid(row=row, column=col*2,
                 sticky="w", padx=(10, 4), pady=4)
    cb = ctk.CTkComboBox(parent, values=values, width=180, height=34,
                         fg_color=CLR_BG, border_color=CLR_BORDER,
                         button_color=CLR_ACCENT, text_color=CLR_TEXT,
                         corner_radius=8, dropdown_fg_color=CLR_CARD)
    cb.grid(row=row, column=col*2+1, padx=(0, 18), pady=4, sticky="w")
    return cb