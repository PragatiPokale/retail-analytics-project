"""
clean_data.py
-------------
Cleans the raw transactions CSV and produces three tidy CSVs ready to load
into the SQL database (schema.sql): clean_customers.csv, clean_products.csv,
clean_transactions.csv.

Run:
    python scripts/clean_data.py
"""

import pandas as pd

RAW_PATH = "data/raw_online_retail.csv"
PRODUCT_CATALOG_PATH = "data/product_catalog.csv"


def load_data():
    df = pd.read_csv(RAW_PATH, parse_dates=["InvoiceDate"])
    products = pd.read_csv(PRODUCT_CATALOG_PATH)
    return df, products


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # 1. Drop exact duplicate rows
    df = df.drop_duplicates()

    # 2. Drop rows with missing CustomerID (can't attribute to a customer for RFM/churn)
    df = df.dropna(subset=["CustomerID"])
    df["CustomerID"] = df["CustomerID"].astype(int)

    # 3. Clean text fields: strip whitespace, standardize casing
    df["Description"] = df["Description"].astype(str).str.strip().str.title()
    df.loc[df["Description"].isin(["Nan", "None"]), "Description"] = "Unknown Item"

    # 4. Flag returns (negative quantity) instead of dropping them — they're
    #    real business signal (return rate), just handled separately in revenue calcs
    df["is_return"] = df["Quantity"] < 0

    # 5. Remove rows with invalid price (0 or negative, excluding legitimate returns)
    df = df[~((df["UnitPrice"] <= 0) & (~df["is_return"]))]

    # 6. Compute line total
    df["line_total"] = (df["Quantity"] * df["UnitPrice"]).round(2)

    # 7. Rename to snake_case for SQL consistency
    df = df.rename(columns={
        "InvoiceNo": "invoice_no",
        "StockCode": "stock_code",
        "Quantity": "quantity",
        "InvoiceDate": "invoice_date",
        "UnitPrice": "unit_price",
        "CustomerID": "customer_id",
        "Country": "country",
    })

    after = len(df)
    print(f"Cleaned transactions: {before} -> {after} rows ({before - after} removed)")
    return df[["invoice_no", "stock_code", "customer_id", "quantity",
               "unit_price", "invoice_date", "line_total", "is_return", "country"]]


def build_customers(df: pd.DataFrame) -> pd.DataFrame:
    customers = (
        df[["customer_id", "country"]]
        .drop_duplicates(subset="customer_id")
        .sort_values("customer_id")
        .reset_index(drop=True)
    )
    return customers


def build_products(products: pd.DataFrame) -> pd.DataFrame:
    products = products.rename(columns={
        "StockCode": "stock_code",
        "Description": "description",
        "Category": "category",
        "UnitPrice": "unit_price",
    })
    return products


def main():
    df, products = load_data()
    clean_tx = clean_transactions(df)
    customers = build_customers(clean_tx)
    clean_products = build_products(products)

    clean_tx.drop(columns=["country"]).to_csv("data/clean_transactions.csv", index=False)
    customers.to_csv("data/clean_customers.csv", index=False)
    clean_products.to_csv("data/clean_products.csv", index=False)

    print("Saved: data/clean_transactions.csv, data/clean_customers.csv, data/clean_products.csv")


if __name__ == "__main__":
    main()
