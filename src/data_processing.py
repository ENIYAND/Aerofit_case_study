# src/data_processing.py
"""
Process Aerofit treadmill CSV:

* Loads CSV from a local path or a URL
* Basic cleaning, type casting, missing-value handling
* Feature engineering: income_bucket, miles_category, usage_category, age_bucket,
  product_label (KP281/KP481/KP781), gender_label, date/hour features, etc.
* Saves processed CSV to data/processed_aerofit.csv (default)

Usage:
    # Using local CSV
    python src/data_processing.py --input data/aerofit_treadmill.csv --output data/processed_aerofit.csv

    # Or read from URL
    python src/data_processing.py --url "https://...aerofit_treadmill.csv?..." --output data/processed_aerofit.csv
"""
from pathlib import Path
import argparse
import pandas as pd
import numpy as np

DEFAULT_URL = "https://d2beiqkhq929f0.cloudfront.net/public_assets/assets/000/001/125/original/aerofit_treadmill.csv?1639992749"
DEFAULT_INPUT = Path("data/aerofit_treadmill.csv")
DEFAULT_OUTPUT = Path("data/processed_aerofit.csv")


def load_data(path: str = None, url: str = None) -> pd.DataFrame:
    """Load CSV from local path or URL; fallback to DEFAULT_INPUT then DEFAULT_URL."""
    if url:
        print(f"[load_data] Loading from URL: {url}")
        df = pd.read_csv(url)
    elif path:
        print(f"[load_data] Loading from local file: {path}")
        df = pd.read_csv(path)
    else:
        if DEFAULT_INPUT.exists():
            print(f"[load_data] Loading from default local file: {DEFAULT_INPUT}")
            df = pd.read_csv(DEFAULT_INPUT)
        else:
            print("[load_data] No local file found; loading from default URL")
            df = pd.read_csv(DEFAULT_URL)
    print(f"[load_data] Loaded dataframe with shape: {df.shape}")
    return df


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: strip column names, lowercase, drop duplicates, normalize strings."""
    # normalize column names
    df = df.rename(columns=lambda c: c.strip().lower().replace(" ", "_"))
    # drop exact duplicates
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    after = len(df)
    if after < before:
        print(f"[basic_clean] Dropped {before-after} duplicate rows")
    # trim string columns of leading/trailing whitespace
    obj_cols = df.select_dtypes(include="object").columns.tolist()
    for c in obj_cols:
        df[c] = df[c].astype(str).str.strip()
    return df


def impute_and_cast(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cast expected numeric columns and impute missing values with medians or sensible defaults.
    This function is defensive: only operates on columns that exist.
    """
    # Common numeric candidates
    numeric_candidates = [
        "income", "miles", "usage", "fitness", "age", "year", "price", "quantity", "count"
    ]
    for col in numeric_candidates:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            med = df[col].median(skipna=True)
            if np.isnan(med):
                med = 0
            df[col] = df[col].fillna(med)
            print(f"[impute_and_cast] Ensured numeric & imputed '{col}' (median={med})")

    # Cast product / gender / education to string-clean labels if present
    for cat in ["product", "gender", "education"]:
        if cat in df.columns:
            df[cat] = df[cat].astype(str).str.strip()

    return df


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived features:
     - product_label (cleaned)
     - income_bucket (Low/Medium/High)
     - miles_category (low/medium/high)
     - usage_category (casual/regular/heavy)
     - age_bucket
     - gender_label normalized
     - date/hour/day features if datetime column present
    """
    # PRODUCT: normalize common product codes (KP281, KP481, KP781) if present
    if "product" in df.columns:
        df["product_label"] = df["product"].str.upper().str.replace(r"\s+", "", regex=True)
        print("[feature_engineering] Created product_label from 'product'")

    # GENDER: unified labels
    if "gender" in df.columns:
        df["gender_label"] = df["gender"].str.lower().map(
            lambda x: "male" if "m" in x else ("female" if "f" in x else x)
        )
        print("[feature_engineering] Created gender_label")

    # INCOME buckets (quantile-based if income present)
    if "income" in df.columns:
        try:
            df["income_bucket"] = pd.qcut(df["income"].replace({0: np.nan}), q=3, labels=["low", "medium", "high"])
        except Exception:
            # fallback to simple rules
            bins = [-np.inf, 40000, 70000, np.inf]
            df["income_bucket"] = pd.cut(df["income"], bins=bins, labels=["low", "medium", "high"])
        print("[feature_engineering] Created income_bucket")

    # MILES category (use qcut if enough unique values)
    if "miles" in df.columns:
        try:
            if df["miles"].nunique() >= 3:
                df["miles_category"] = pd.qcut(df["miles"], q=3, labels=["low", "medium", "high"])
            else:
                df["miles_category"] = pd.cut(df["miles"], bins=3, labels=["low", "medium", "high"])
        except Exception:
            df["miles_category"] = "unknown"
        print("[feature_engineering] Created miles_category")

    # USAGE category: if usage is numeric (e.g., days per week or hours)
    if "usage" in df.columns:
        # usage might be continuous; we define casual <3, regular 3-5, heavy >5 (adjustable)
        df["usage_category"] = pd.cut(df["usage"],
                                     bins=[-np.inf, 2.99, 5.0, np.inf],
                                     labels=["casual", "regular", "heavy"])
        print("[feature_engineering] Created usage_category")

    # AGE buckets
    if "age" in df.columns:
        df["age_bucket"] = pd.cut(df["age"], bins=[0, 24, 34, 44, 54, 120],
                                  labels=["<25", "25-34", "35-44", "45-54", "55+"])
        print("[feature_engineering] Created age_bucket")

    # EDUCATION normalization
    if "education" in df.columns:
        df["education_label"] = df["education"].astype(str).str.lower().replace({
            "bachelors": "bachelor", "bachelor's": "bachelor",
            "masters": "master", "master's": "master", "phd": "phd"
        })
        print("[feature_engineering] Created education_label")

    # DATETIME features: if a datetime-like column exists, create date/hour/day
    datetime_cols = [c for c in df.columns if "date" in c or "time" in c or "datetime" in c]
    if datetime_cols:
        # pick a representative datetime column
        dtc = datetime_cols[0]
        df[dtc] = pd.to_datetime(df[dtc], errors="coerce")
        df["date"] = df[dtc].dt.date
        df["hour"] = df[dtc].dt.hour
        df["day_of_week"] = df[dtc].dt.day_name()
        print(f"[feature_engineering] Created date/hour/day features from '{dtc}'")

    # If there's a 'registered' and 'casual' pattern (unlikely in this dataset) attempt to add count
    if ("registered" in df.columns or "casual" in df.columns) and "count" not in df.columns:
        reg = df.get("registered")
        cas = df.get("casual")
        if reg is not None and cas is not None:
            df["count"] = reg + cas
            print("[feature_engineering] Created 'count' from registered+casual")

    return df


def process(input_path: str = None, url: str = None, output_path: str = None) -> pd.DataFrame:
    output_path = Path(output_path) if output_path else DEFAULT_OUTPUT
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = load_data(path=input_path, url=url)
    df = basic_clean(df)
    df = impute_and_cast(df)
    df = feature_engineering(df)

    # Save processed CSV
    df.to_csv(output_path, index=False)
    print(f"[process] Wrote processed CSV: {output_path} (shape={df.shape})")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process AeroFit treadmill dataset")
    parser.add_argument("--input", "-i", help="Local CSV path (e.g. data/aerofit_treadmill.csv)")
    parser.add_argument("--url", "-u", help="CSV download URL")
    parser.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT), help="Output processed CSV path")
    args = parser.parse_args()
    process(input_path=args.input, url=args.url, output_path=args.output)
