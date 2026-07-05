"""
rfm_segmentation.py
--------------------
Computes RFM (Recency, Frequency, Monetary) scores per customer and
segments them using KMeans clustering. Outputs a CSV ready for the
Power BI / Tableau dashboard.

Run:
    python scripts/rfm_segmentation.py
"""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def compute_rfm(tx: pd.DataFrame) -> pd.DataFrame:
    tx = tx[~tx["is_return"]].copy()
    tx["invoice_date"] = pd.to_datetime(tx["invoice_date"])
    max_date = tx["invoice_date"].max()

    rfm = tx.groupby("customer_id").agg(
        recency_days=("invoice_date", lambda x: (max_date - x.max()).days),
        frequency=("invoice_no", "nunique"),
        monetary=("line_total", "sum"),
    ).reset_index()

    return rfm


def score_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    # Quartile-based scoring: 4 = best, 1 = worst
    rfm["r_score"] = pd.qcut(rfm["recency_days"], 4, labels=[4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["rfm_score"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)
    return rfm


def label_segment(row):
    if row["r_score"] >= 3 and row["f_score"] >= 3 and row["m_score"] >= 3:
        return "Champions"
    elif row["r_score"] >= 3 and row["f_score"] >= 2:
        return "Loyal Customers"
    elif row["r_score"] >= 3:
        return "Recent / New Customers"
    elif row["f_score"] >= 3 and row["m_score"] >= 3:
        return "At-Risk High Value"
    elif row["r_score"] <= 2 and row["f_score"] <= 2:
        return "Hibernating / Lost"
    else:
        return "Needs Attention"


def cluster_rfm(rfm: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    features = rfm[["recency_days", "frequency", "monetary"]]
    scaled = StandardScaler().fit_transform(features)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm["cluster"] = kmeans.fit_predict(scaled)
    return rfm


def main():
    tx = pd.read_csv("data/clean_transactions.csv")
    rfm = compute_rfm(tx)
    rfm = score_rfm(rfm)
    rfm["segment"] = rfm.apply(label_segment, axis=1)
    rfm = cluster_rfm(rfm)

    rfm.to_csv("data/rfm_segments.csv", index=False)

    print("RFM segmentation complete. Segment breakdown:")
    print(rfm["segment"].value_counts())
    print(f"\nSaved: data/rfm_segments.csv ({len(rfm)} customers)")


if __name__ == "__main__":
    main()
