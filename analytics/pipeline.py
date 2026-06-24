"""
ETL + analysis pipeline for the Grade Management System.
All functions return a matplotlib Figure ready to embed in Tkinter
via FigureCanvasTkAgg.

Pipeline flow:
  MySQL → pd.read_sql() → clean() → aggregate() → plot() → Figure
"""

import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import mysql.connector
from db import get_connection

matplotlib.use("Agg")   # non-interactive backend — required for Tkinter embedding

# ── Seaborn theme (matches the dark app palette) ──────────────
sns.set_theme(
    style="darkgrid",
    palette="muted",
    rc={
        "figure.facecolor":  "#1E2433",
        "axes.facecolor":    "#161B27",
        "axes.edgecolor":    "#2A3148",
        "axes.labelcolor":   "#E8ECF4",
        "xtick.color":       "#7A849E",
        "ytick.color":       "#7A849E",
        "text.color":        "#E8ECF4",
        "grid.color":        "#2A3148",
        "grid.linewidth":    0.6,
    }
)


# ─────────────────────────────────────────────────────────────
# STEP 1 — EXTRACT: load raw data from MySQL into DataFrames
# ─────────────────────────────────────────────────────────────

def _load_enrollments():
    """
    Pull all enrollment data joined with student, course, and term.
    Returns a raw DataFrame.
    """
    conn = get_connection()
    try:
        sql = """
            SELECT
                e.enroll_id,
                e.stud_id,
                e.course_id,
                e.term_id,
                e.raw_score,
                e.final_grade,
                e.letter_grade,
                e.status,
                CONCAT(s.stud_fname, ' ', s.stud_lname) AS full_name,
                s.stud_no,
                s.section,
                s.year_level,
                p.prog_code,
                c.course_code,
                c.course_title,
                c.course_units,
                CONCAT(t.semester, ' ', t.school_year) AS term_label,
                t.semester,
                t.school_year
            FROM enrollment e
            JOIN student  s USING (stud_id)
            JOIN course   c USING (course_id)
            JOIN term     t USING (term_id)
            JOIN program  p ON s.prog_id = p.prog_id
        """
        df = pd.read_sql(sql, conn)
        return df
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────
# STEP 2 — CLEAN: standardize types, remove noise
# ─────────────────────────────────────────────────────────────

def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Data cleaning pipeline using .pipe() chaining.
    Returns a cleaned DataFrame.
    """
    return (
        df
        .pipe(_cast_types)
        .pipe(_remove_outliers)
        .pipe(_drop_duplicates)
        .pipe(_fill_derived)
    )


def _cast_types(df):
    df["raw_score"]   = pd.to_numeric(df["raw_score"],   errors="coerce")
    df["final_grade"] = pd.to_numeric(df["final_grade"], errors="coerce")
    df["course_units"]= pd.to_numeric(df["course_units"],errors="coerce")
    df["year_level"]  = pd.to_numeric(df["year_level"],  errors="coerce")
    return df


def _remove_outliers(df):
    # Remove rows where raw_score is outside valid range
    mask = df["raw_score"].isna() | df["raw_score"].between(0, 100)
    return df[mask].copy()


def _drop_duplicates(df):
    # Keep only the latest record per student+course+term
    return df.drop_duplicates(
        subset=["stud_id", "course_id", "term_id"],
        keep="last"
    ).reset_index(drop=True)


def _fill_derived(df):
    # Add pass/fail column based on PLV scale (3.00 = passing threshold)
    df["passed"] = df["final_grade"].apply(
        lambda g: "Pass" if pd.notna(g) and g <= 3.00 else ("Fail" if pd.notna(g) else "No Grade")
    )
    return df


# ─────────────────────────────────────────────────────────────
# STEP 3 — AGGREGATE + PLOT (one function per chart)
# ─────────────────────────────────────────────────────────────

def get_grade_distribution(term_id=None):
    """
    Histogram of raw_score distribution across all students.
    Optional: filter by term_id.
    Returns: matplotlib Figure
    """
    df = _clean(_load_enrollments())
    df = df[df["raw_score"].notna()]

    if term_id:
        df = df[df["term_id"] == term_id]

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.histplot(
        data=df, x="raw_score",
        bins=20, kde=True,
        color="#4F8EF7", ax=ax
    )
    ax.set_title("Grade Distribution", fontsize=13, pad=12)
    ax.set_xlabel("Raw Score")
    ax.set_ylabel("Number of Students")
    ax.axvline(75, color="#F75F5F", linestyle="--", linewidth=1.2, label="Passing (75)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


def get_section_avg(term_id=None):
    """
    Bar chart: average raw_score per section.
    Returns: matplotlib Figure
    """
    df = _clean(_load_enrollments())
    df = df[df["raw_score"].notna()]

    if term_id:
        df = df[df["term_id"] == term_id]

    agg = (
        df.groupby("section")["raw_score"]
        .mean()
        .reset_index()
        .rename(columns={"raw_score": "avg_score"})
        .sort_values("avg_score", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(
        data=agg, x="section", y="avg_score",
        palette="Blues_d", ax=ax
    )
    ax.set_title("Average Score per Section", fontsize=13, pad=12)
    ax.set_xlabel("Section")
    ax.set_ylabel("Average Raw Score")
    ax.axhline(75, color="#F75F5F", linestyle="--", linewidth=1.2, label="Passing (75)")
    ax.tick_params(axis="x", rotation=30)
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


def get_course_avg():
    """
    Horizontal bar chart: average raw_score per course.
    Returns: matplotlib Figure
    """
    df = _clean(_load_enrollments())
    df = df[df["raw_score"].notna()]

    agg = (
        df.groupby("course_code")["raw_score"]
        .mean()
        .reset_index()
        .rename(columns={"raw_score": "avg_score"})
        .sort_values("avg_score")
    )

    fig, ax = plt.subplots(figsize=(7, max(4, len(agg) * 0.5)))
    sns.barplot(
        data=agg, x="avg_score", y="course_code",
        palette="muted", ax=ax, orient="h"
    )
    ax.set_title("Average Score per Course", fontsize=13, pad=12)
    ax.set_xlabel("Average Raw Score")
    ax.set_ylabel("Course")
    ax.axvline(75, color="#F75F5F", linestyle="--", linewidth=1.2, label="Passing (75)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


def get_pass_fail_pie(term_id=None):
    """
    Pie chart: pass vs fail vs no-grade breakdown.
    Returns: matplotlib Figure
    """
    df = _clean(_load_enrollments())

    if term_id:
        df = df[df["term_id"] == term_id]

    counts = df["passed"].value_counts()

    colors = {
        "Pass":     "#3DDC97",
        "Fail":     "#F75F5F",
        "No Grade": "#7A849E"
    }
    clr = [colors.get(k, "#4F8EF7") for k in counts.index]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(
        counts.values,
        labels=counts.index,
        colors=clr,
        autopct="%1.1f%%",
        startangle=140,
        textprops={"color": "#E8ECF4", "fontsize": 11}
    )
    ax.set_title("Pass / Fail Breakdown", fontsize=13, pad=12)
    fig.tight_layout()
    return fig


def get_student_trend(stud_id):
    """
    Line chart: a single student's raw_score across terms.
    Returns: matplotlib Figure
    """
    df = _clean(_load_enrollments())
    df = df[(df["stud_id"] == stud_id) & df["raw_score"].notna()]

    if df.empty:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.text(0.5, 0.5, "No grade data for this student.",
                ha="center", va="center", color="#7A849E", fontsize=12)
        ax.axis("off")
        return fig

    agg = (
        df.groupby(["term_id", "term_label"])["raw_score"]
        .mean()
        .reset_index()
        .sort_values("term_id")
    )

    name = df["full_name"].iloc[0]
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.lineplot(
        data=agg, x="term_label", y="raw_score",
        marker="o", color="#4F8EF7", linewidth=2, ax=ax
    )
    ax.set_title(f"Grade Trend — {name}", fontsize=13, pad=12)
    ax.set_xlabel("Term")
    ax.set_ylabel("Average Raw Score")
    ax.axhline(75, color="#F75F5F", linestyle="--", linewidth=1.2, label="Passing (75)")
    ax.tick_params(axis="x", rotation=20)
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


def get_grade_heatmap(term_id=None):
    """
    Heatmap: student sections (rows) vs courses (cols), values = avg raw_score.
    Returns: matplotlib Figure
    """
    df = _clean(_load_enrollments())
    df = df[df["raw_score"].notna()]

    if term_id:
        df = df[df["term_id"] == term_id]

    pivot = df.pivot_table(
        values="raw_score",
        index="section",
        columns="course_code",
        aggfunc="mean"
    ).round(1)

    if pivot.empty:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.text(0.5, 0.5, "Not enough data for heatmap.",
                ha="center", va="center", color="#7A849E", fontsize=12)
        ax.axis("off")
        return fig

    fig, ax = plt.subplots(figsize=(max(7, len(pivot.columns) * 1.2),
                                     max(4, len(pivot) * 0.8)))
    sns.heatmap(
        pivot,
        annot=True, fmt=".1f",
        cmap="Blues",
        linewidths=0.5,
        linecolor="#2A3148",
        ax=ax,
        cbar_kws={"shrink": 0.8}
    )
    ax.set_title("Average Score — Section × Course", fontsize=13, pad=12)
    ax.set_xlabel("Course")
    ax.set_ylabel("Section")
    fig.tight_layout()
    return fig


def get_score_boxplot(term_id=None):
    """
    Boxplot: score distribution per course (outliers visible).
    Returns: matplotlib Figure
    """
    df = _clean(_load_enrollments())
    df = df[df["raw_score"].notna()]

    if term_id:
        df = df[df["term_id"] == term_id]

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(
        data=df, x="course_code", y="raw_score",
        palette="muted", ax=ax
    )
    ax.set_title("Score Distribution per Course", fontsize=13, pad=12)
    ax.set_xlabel("Course")
    ax.set_ylabel("Raw Score")
    ax.axhline(75, color="#F75F5F", linestyle="--", linewidth=1.2, label="Passing (75)")
    ax.tick_params(axis="x", rotation=30)
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig