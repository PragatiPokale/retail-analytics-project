"""
churn_analysis.py
------------------
Flags customers as churned (no purchase in 90+ days) and trains a simple
logistic regression model to identify which behavioral features predict
churn. This is the "so what" layer on top of the RFM segmentation —
it turns a descriptive label into something actionable.

Run:
    python scripts/churn_analysis.py
"""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

CHURN_THRESHOLD_DAYS = 90


def build_features(tx: pd.DataFrame) -> pd.DataFrame:
    tx = tx.copy()
    tx["invoice_date"] = pd.to_datetime(tx["invoice_date"])
    max_date = tx["invoice_date"].max()

    purchases = tx[~tx["is_return"]]

    features = purchases.groupby("customer_id").agg(
        recency_days=("invoice_date", lambda x: (max_date - x.max()).days),
        frequency=("invoice_no", "nunique"),
        monetary=("line_total", "sum"),
        avg_order_value=("line_total", "mean"),
        tenure_days=("invoice_date", lambda x: (x.max() - x.min()).days),
    ).reset_index()

    returns_rate = (
        tx.groupby("customer_id")["is_return"].mean().rename("return_rate").reset_index()
    )
    features = features.merge(returns_rate, on="customer_id", how="left")

    features["churned"] = (features["recency_days"] > CHURN_THRESHOLD_DAYS).astype(int)
    return features


def train_model(features: pd.DataFrame):
    X = features[["frequency", "monetary", "avg_order_value", "tenure_days", "return_rate"]]
    y = features["churned"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    print("Classification report:")
    print(classification_report(y_test, preds))
    print(f"ROC-AUC: {roc_auc_score(y_test, probs):.3f}")

    coef_df = pd.DataFrame({
        "feature": X.columns,
        "coefficient": model.coef_[0],
    }).sort_values("coefficient")
    print("\nFeature impact on churn likelihood (positive = increases churn risk):")
    print(coef_df.to_string(index=False))

    return model


def main():
    tx = pd.read_csv("data/clean_transactions.csv")
    features = build_features(tx)
    features.to_csv("data/churn_features.csv", index=False)

    churn_rate = features["churned"].mean()
    print(f"Overall churn rate (>{CHURN_THRESHOLD_DAYS} days inactive): {churn_rate:.1%}\n")

    train_model(features)
    print("\nSaved: data/churn_features.csv")


if __name__ == "__main__":
    main()
