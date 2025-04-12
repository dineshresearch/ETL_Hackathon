import pandas as pd
import json

# Load the CSVs
df_shipments = pd.read_csv(r'C:\Users\govin\Desktop\Hackathon\downloaded_csvs\shipments.csv')
df_refund = pd.read_csv(r'C:\Users\govin\Desktop\Hackathon\downloaded_csvs\refunds.csv')  # Correct CSV name for refund

# --------------------------
# 1. Clean Shipments Data
# --------------------------

# Lowercase and strip status
df_shipments['status'] = df_shipments['status'].astype(str).str.lower().str.strip()

# Map status to standard labels
def clean_status(val):
    if 'shipped' in val and 'delivered' not in val:
        return 'shipped'
    elif 'in_transit' in val:
        return 'in_transit'
    elif 'delivered' in val:
        return 'delivered'
    elif 'cancel' in val:
        return 'cancelled'
    else:
        return 'invalid'

df_shipments['status_cleaned'] = df_shipments['status'].apply(clean_status)

# Filter only valid cleaned statuses
valid_statuses = ['shipped', 'in_transit', 'delivered', 'cancelled']
df_shipments = df_shipments[df_shipments['status_cleaned'].isin(valid_statuses)]

# Parse delivery_date
df_shipments["delivery_date"] = pd.to_datetime(df_shipments["delivery_date"], errors="coerce")

# Flags
df_shipments["on_time"] = (df_shipments["status_cleaned"] == "delivered") & (df_shipments["delivery_date"].notna())
df_shipments["delayed"] = (df_shipments["status_cleaned"] == "delivered") & (df_shipments["delivery_date"].isna())
df_shipments["undelivered"] = df_shipments["status_cleaned"] != "delivered"

# Group by carrier
shipping_performance = df_shipments.groupby("carrier").agg(
    total_shipments=("id", "count"),
    on_time_deliveries=("on_time", "sum"),
    delayed_shipments=("delayed", "sum"),
    undelivered_shipments=("undelivered", "sum")
).reset_index()

# Get only the top 5 shipping performance results
top_5_shipping_performance = shipping_performance.nlargest(5, 'total_shipments')

# ------------------------------
# 2. Clean Refund Data
# ------------------------------

# Ensure refund_amount is numeric (convert if necessary)
df_refund['refund_amount'] = pd.to_numeric(df_refund['refund_amount'], errors='coerce')

# Group by reason and aggregate refund data
refund_reason_analysis = df_refund.groupby("reason").agg(
    total_returns=("refund_amount", "count"),  # Count refunds per reason
    total_refund_amount=("refund_amount", "sum")  # Sum the refund amounts
).reset_index()

# Get only the top 5 refund reason analysis results
top_5_refund_reason_analysis = refund_reason_analysis.nlargest(5, 'total_refund_amount')

# ----------------------------
# 3. Final Output Structure
# ----------------------------

# Final combined output with only top 5 results
output = {
    "shipping_performance_by_carrier": top_5_shipping_performance.to_dict(orient="records"),
    "refund_reason_analysis": top_5_refund_reason_analysis.to_dict(orient="records")
}

# Pretty print the result
print(json.dumps(output, indent=2))
