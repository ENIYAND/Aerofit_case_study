# src/plots.py
"""
Plotting utilities for Aerofit.

Produces PNGs in `figures/`:
 - product_distribution.png
 - income_by_product_boxplot.png
 - miles_vs_usage.png
 - usage_histogram.png
 - product_gender_bar.png
 - correlation_heatmap.png
 - usage_by_product_boxplot.png
 - education_product_stacked.png (if education present)

Usage:
    python src/plots.py --input data/processed_aerofit.csv
"""
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set(style="whitegrid")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)


def _save(fig, name):
    path = FIG_DIR / name
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"[plot] Saved: {path}")


def plot_product_distribution(df, product_col="product_label"):
    if product_col not in df.columns:
        print(f"[plot_product_distribution] Missing {product_col} — skipped")
        return
    fig, ax = plt.subplots(figsize=(7, 5))
    order = df[product_col].value_counts().index
    sns.countplot(x=product_col, data=df, order=order, ax=ax)
    ax.set_title("Product distribution (KP281 / KP481 / KP781)")
    ax.set_xlabel("Product")
    ax.set_ylabel("Count")
    _save(fig, "product_distribution.png")


def plot_income_by_product(df, income_col="income", product_col="product_label"):
    if income_col not in df.columns or product_col not in df.columns:
        print("[plot_income_by_product] Missing columns — skipped")
        return
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.boxplot(x=product_col, y=income_col, data=df, ax=ax)
    ax.set_title("Income distribution by product")
    ax.set_ylabel("Income")
    _save(fig, "income_by_product_boxplot.png")


def plot_miles_vs_usage(df, miles_col="miles", usage_col="usage"):
    if miles_col not in df.columns or usage_col not in df.columns:
        print("[plot_miles_vs_usage] Missing miles/usage — skipped")
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(x=miles_col, y=usage_col, data=df, alpha=0.5, ax=ax)
    try:
        sns.regplot(x=miles_col, y=usage_col, data=df, scatter=False, lowess=True, ax=ax, ci=None)
    except Exception:
        sns.regplot(x=miles_col, y=usage_col, data=df, scatter=False, ax=ax, ci=None)
    ax.set_title("Miles vs Usage")
    ax.set_xlabel("Miles (monthly)")
    ax.set_ylabel("Usage (e.g., days/week)")
    _save(fig, "miles_vs_usage.png")


def plot_usage_histogram(df, usage_col="usage"):
    if usage_col not in df.columns:
        print("[plot_usage_histogram] Missing usage — skipped")
        return
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.histplot(df[usage_col].dropna(), bins=20, kde=False, ax=ax)
    ax.set_title("Usage distribution")
    ax.set_xlabel("Usage")
    _save(fig, "usage_histogram.png")


def plot_product_gender(df, product_col="product_label", gender_col="gender_label"):
    if product_col not in df.columns or gender_col not in df.columns:
        print("[plot_product_gender] Missing product/gender — skipped")
        return
    cross = df.groupby([product_col, gender_col]).size().reset_index(name="count")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=product_col, y="count", hue=gender_col, data=cross, ax=ax)
    ax.set_title("Product by Gender")
    _save(fig, "product_gender_bar.png")


def plot_usage_by_product(df, usage_col="usage", product_col="product_label"):
    if usage_col not in df.columns or product_col not in df.columns:
        print("[plot_usage_by_product] Missing usage/product — skipped")
        return
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.boxplot(x=product_col, y=usage_col, data=df, ax=ax)
    ax.set_title("Usage by Product (distribution)")
    _save(fig, "usage_by_product_boxplot.png")


def plot_education_vs_product(df, edu_col="education_label", product_col="product_label"):
    if edu_col not in df.columns or product_col not in df.columns:
        print("[plot_education_vs_product] Missing education/product — skipped")
        return
    # pivot for stacked bar
    pivot = (df.groupby([edu_col, product_col])
               .size().unstack(fill_value=0))
    pivot = pivot.div(pivot.sum(axis=1), axis=0)  # percentages per education group
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot.plot(kind="bar", stacked=True, ax=ax)
    ax.set_title("Product share per education group (normalized)")
    ax.set_ylabel("Share")
    _save(fig, "education_product_stacked.png")


def plot_correlation_heatmap(df):
    num = df.select_dtypes(include=[np.number])
    if num.shape[1] < 2:
        print("[plot_correlation_heatmap] Not enough numeric columns — skipped")
        return
    corr = num.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0, ax=ax)
    ax.set_title("Correlation heatmap (numeric features)")
    _save(fig, "correlation_heatmap.png")


def generate_all(input_csv="data/processed_aerofit.csv"):
    p = Path(input_csv)
    if not p.exists():
        raise FileNotFoundError(f"Processed CSV not found: {input_csv}. Run src/data_processing.py first.")
    df = pd.read_csv(p, parse_dates=True)

    # If there is a datetime-like column, try to parse it into 'date' for time series
    dtcols = [c for c in df.columns if "date" in c or "time" in c or "datetime" in c]
    if dtcols:
        try:
            df[dtcols[0]] = pd.to_datetime(df[dtcols[0]], errors="coerce")
            if "date" not in df.columns:
                df["date"] = pd.to_datetime(df[dtcols[0]]).dt.date
        except Exception:
            pass

    plot_product_distribution(df)
    plot_income_by_product(df)
    plot_miles_vs_usage(df)
    plot_usage_histogram(df)
    plot_product_gender(df)
    plot_usage_by_product(df)
    plot_education_vs_product(df)
    plot_correlation_heatmap(df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Aerofit plots")
    parser.add_argument("--input", "-i", default="data/processed_aerofit.csv", help="Processed CSV file")
    args = parser.parse_args()
    generate_all(input_csv=args.input)
