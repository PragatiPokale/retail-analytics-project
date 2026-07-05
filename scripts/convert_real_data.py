import pandas as pd

# Read both sheets from the real UCI file and combine them
sheet1 = pd.read_excel("data/online_retail_II.xlsx", sheet_name="Year 2009-2010")
sheet2 = pd.read_excel("data/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = pd.concat([sheet1, sheet2], ignore_index=True)

# Rename columns to match what our scripts expect
df = df.rename(columns={
    "Invoice": "InvoiceNo",
    "Price": "UnitPrice",
    "Customer ID": "CustomerID",
})

df.to_csv("data/raw_online_retail.csv", index=False)
print(f"Saved {len(df)} rows to data/raw_online_retail.csv")

# Also rebuild a simple product catalog from this data
products = df[["StockCode", "Description"]].drop_duplicates(subset="StockCode")
products["Category"] = "General"
products["UnitPrice"] = df.groupby("StockCode")["UnitPrice"].mean().values[:len(products)]
products.to_csv("data/product_catalog.csv", index=False)
print(f"Saved {len(products)} products to data/product_catalog.csv")