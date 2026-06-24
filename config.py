import os
import customtkinter as ctk

# config

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "@YvesJerico23",   # change this
    "database": "plv_DB"
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# brand palette
CLR_BG        = "#0F1117"   # near-black page background
CLR_SIDEBAR   = "#161B27"   # sidebar
CLR_CARD      = "#1E2433"   # metric cards / panels
CLR_ACCENT    = "#4F8EF7"   # PLV blue
CLR_ACCENT2   = "#3DDC97"   # green for passing
CLR_RED       = "#F75F5F"   # failing / danger
CLR_YELLOW    = "#F7C94F"   # warning / enrolled
CLR_TEXT      = "#E8ECF4"
CLR_SUBTEXT   = "#7A849E"
CLR_BORDER    = "#2A3148"
CLR_HOVER     = "#253050"
CLR_SEL       = "#1F3A6E"   # selected sidebar item

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_CARD   = ("Segoe UI", 28, "bold")
FONT_LABEL  = ("Segoe UI", 12)
FONT_SMALL  = ("Segoe UI", 10)
FONT_BTN    = ("Segoe UI", 12, "bold")
FONT_HEAD   = ("Segoe UI", 14, "bold")