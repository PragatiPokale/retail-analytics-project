"""
generate_sample_data.py
------------------------
Generates a synthetic e-commerce transactions dataset that mimics the
structure of the UCI "Online Retail II" dataset, so you can build and test
the full pipeline (cleaning -> SQL -> RFM -> churn -> dashboard) before
swapping in the real dataset.

REAL DATASET (recommended for your final portfolio piece):
UCI Online Retail II: https://archive.ics.uci.edu/dataset/502/online+retail+ii
Kaggle mirror: https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci

To use the real data instead, download the CSV/XLSX, save it as
data/raw_online_retail.csv with the same column names used below, and
skip running this script.

Usage:
    python scripts/generate_sample_data.py
"""

import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

N_CUSTOMERS = 800
N_PRODUCTS = 150
N_TRANSACTIONS = 40000
COUNTRIES = ["United Kingdom", "Germany", "France", "Netherlands", "Ireland",
             "Spain", "Belgium", "Switzerland", "Portugal", "Australia"]

# Build customer pool (some customers churn early, some are frequent buyers)
customers = []
for i in range(1, N_CUSTOMERS + 1):
    customers.append({
        "CustomerID": 10000 + i,
        "Country": random.choices(COUNTRIES, weights=[40, 10, 10, 8, 7, 6, 5, 5, 5, 4])[0],
        "join_date": fake.date_between(start_date="-2y", end_date="-3M"),
        "activity_level": random.choices(["high", "medium", "low", "churned"],
                                          weights=[15, 35, 30, 20])[0],
    })

# Build product catalog
products = []
categories = ["Home Decor", "Kitchenware", "Stationery", "Toys", "Lighting",
              "Textiles", "Garden", "Gift Sets"]
for i in range(1, N_PRODUCTS + 1):
    products.append({
        "StockCode": f"SKU{1000 + i}",
        "Description": fake.catch_phrase().title(),
        "Category": random.choice(categories),
        "UnitPrice": round(random.uniform(0.85, 45.0), 2),
    })

products_df = pd.DataFrame(products)
customers_df = pd.DataFrame(customers)

def random_date_for_activity(level, join_date):
    """Skew transaction dates based on customer activity level to simulate churn."""
    today = datetime(2024, 12, 31)
    join_dt = datetime.combine(join_date, datetime.min.time())
    if level == "churned":
        # last purchase happened a while ago
        max_days_ago = 400
        min_days_ago = 120
    elif level == "low":
        max_days_ago = 200
        min_days_ago = 0
    elif level == "medium":
        max_days_ago = 150
        min_days_ago = 0
    else:  # high
        max_days_ago = 60
        min_days_ago = 0
    days_ago = random.randint(min_days_ago, max_days_ago)
    d = today - timedelta(days=days_ago)
    return max(d, join_dt)

rows = []
invoice_counter = 500000
for _ in range(N_TRANSACTIONS):
    cust = random.choice(customers)
    prod = random.choice(products)
    invoice_counter += 1
    qty = random.choice([1, 1, 1, 2, 2, 3, 4, 6, 12])
    # inject some returns (negative quantity) and some messy rows for cleaning practice
    if random.random() < 0.03:
        qty = -qty
    tx_date = random_date_for_activity(cust["activity_level"], cust["join_date"])

    description = prod["Description"]
    # inject messiness: missing description, weird casing, whitespace
    if random.random() < 0.02:
        description = None
    elif random.random() < 0.05:
        description = f"  {description.upper()}  "

    unit_price = prod["UnitPrice"]
    if random.random() < 0.01:
        unit_price = 0.0  # bad data row

    customer_id = cust["CustomerID"]
    if random.random() < 0.03:
        customer_id = None  # missing customer id, common in real dataset

    rows.append({
        "InvoiceNo": invoice_counter,
        "StockCode": prod["StockCode"],
        "Description": description,
        "Quantity": qty,
        "InvoiceDate": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
        "UnitPrice": unit_price,
        "CustomerID": customer_id,
        "Country": cust["Country"],
    })

# add a handful of exact duplicate rows (common real-world issue)
rows += random.sample(rows, 50)

df = pd.DataFrame(rows)
df.to_csv("data/raw_online_retail.csv", index=False)
products_df.to_csv("data/product_catalog.csv", index=False)

print(f"Generated {len(df)} transaction rows -> data/raw_online_retail.csv")
print(f"Generated {len(products_df)} products -> data/product_catalog.csv")
print("Swap this file with the real UCI Online Retail II dataset when ready.")
