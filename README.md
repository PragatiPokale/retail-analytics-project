# Retail Sales Analytics & Customer Churn Prediction

**A Python + SQL + BI dashboard project analyzing e-commerce transactions to identify revenue drivers, segment customers by value, and flag churn risk.**

![Dashboard Preview](dashboard/dashboard_screenshot.png)
*(Add your Power BI / Tableau screenshot here once built — see [Step 5](#5-dashboard))*

---

## Business Problem

An online retailer wants to understand:
1. Where is revenue coming from, and how is it trending?
2. Which customers are most valuable, and which are at risk of leaving?
3. What behaviors predict churn, so the business can intervene early?

This project answers those questions end-to-end: raw data → SQL database → Python analysis → BI dashboard → business recommendations.

## Key Findings
- Segmented 5,878 customers into 6 RFM groups: Champions (1,821), Hibernating/Lost (2,045), Loyal Customers (796), At-Risk High Value (643), Recent/New (336), and Needs Attention (237)
- 50.8% of customers had not purchased in 90+ days, indicating a substantial churn problem
- A logistic regression churn model achieved 73% accuracy and 0.795 ROC-AUC on held-out data
- Return rate was the single strongest predictor of churn — customers who return items frequently are far more likely to stop purchasing altogether

## Tech Stack
- **Python** (pandas, scikit-learn) — data cleaning, RFM segmentation, churn model
- **SQL** (PostgreSQL) — schema design, business-question queries, cohort analysis
- **Power BI / Tableau** — interactive dashboard for stakeholders
- **Jupyter Notebooks** — documented, reproducible analysis

## Repo Structure
```
retail-analytics-project/
├── README.md
├── requirements.txt
├── data/                        # raw + cleaned CSVs (or .gitignore if too large)
├── sql/
│   ├── schema.sql                # table definitions
│   └── analysis_queries.sql      # revenue trends, RFM, cohort, churn queries
├── scripts/
│   ├── generate_sample_data.py   # synthetic data generator (swap for real dataset)
│   ├── clean_data.py             # data cleaning pipeline
│   ├── rfm_segmentation.py       # RFM scoring + KMeans clustering
│   └── churn_analysis.py         # churn flagging + logistic regression model
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_rfm_segmentation.ipynb
│   └── 03_churn_analysis.ipynb
└── dashboard/
    └── dashboard_screenshot.png  # + link to live Tableau Public dashboard
```

## How to Run

```bash
# 1. Clone and install dependencies
git clone https://github.com/<your-username>/retail-analytics-project.git
cd retail-analytics-project
pip install -r requirements.txt

# 2. Get the data (choose one)
# Option A: use the included synthetic dataset generator
python scripts/generate_sample_data.py

# Option B (recommended for your final version): download the real dataset
# UCI Online Retail II: https://archive.ics.uci.edu/dataset/502/online+retail+ii
# Save as data/raw_online_retail.csv with matching column names
# (InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country)

# 3. Clean the data
python scripts/clean_data.py

# 4. Run the analysis
python scripts/rfm_segmentation.py
python scripts/churn_analysis.py

# Or explore interactively:
jupyter notebook notebooks/
```

## Data

⚠️ **This repo ships with a synthetic dataset generator** (`scripts/generate_sample_data.py`) so the full pipeline runs out of the box. For your actual portfolio submission, swap in the real **[UCI Online Retail II dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii)** (also on [Kaggle](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci)) — real transactional data with genuine messiness makes the cleaning and insights section far more credible to reviewers.

## Methodology

### 1. Data Cleaning (`notebooks/01_data_cleaning.ipynb`)
Removed duplicates, handled missing customer IDs, standardized text fields, flagged returns, and validated pricing.

### 2. SQL Analysis (`sql/analysis_queries.sql`)
Monthly revenue trends, revenue by country, top products, RFM base table, cohort retention, churn flag — all in raw SQL to demonstrate query-writing ability independent of the Python layer.

### 3. RFM Segmentation (`notebooks/02_rfm_segmentation.ipynb`)
Scored every customer on Recency, Frequency, and Monetary value, then labeled them into actionable segments (Champions, Loyal Customers, At-Risk High Value, Hibernating, etc.) and validated with KMeans clustering.

### 4. Churn Prediction (`notebooks/03_churn_analysis.ipynb`)
Defined churn as 90+ days of inactivity, then trained a logistic regression model to identify which behaviors (frequency, tenure, order value, return rate) most strongly predict churn — moving from "who churned" to "why."

### 5. Dashboard
Built an interactive Power BI / Tableau dashboard with:
- KPI cards: total revenue, active customers, average order value, churn rate
- Revenue trend over time
- Customer segment breakdown (from RFM output)
- Churn risk table for the sales/retention team

*(Add your live dashboard link here, e.g. Tableau Public URL)*

## Recommendations
*(Fill in based on your actual findings)*
1. Launch a win-back campaign targeting "At-Risk High Value" customers before they cross the 90-day churn threshold
2. Double down on marketing spend in top-revenue regions; investigate the cause of decline in underperforming ones
3. Introduce a loyalty tier for "Champions" to protect the ~X% of revenue they generate

## Next Steps
- Automate the pipeline with Airflow/cron for scheduled refreshes
- Add a market-basket analysis (product association rules) to power cross-sell recommendations
- Deploy the churn model as a lightweight API for real-time scoring

---
*Built as a data analytics portfolio project. Feedback welcome — feel free to open an issue.*
