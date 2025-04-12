import re
import time
import pandas as pd
import uuid

def clean_common(df):
    """General cleanup for all columns: removes spaces and special characters"""
    for column in df.columns:
        df[column] = df[column].astype(str).str.strip()  # Remove spaces
        df[column] = df[column].apply(lambda x: re.sub(r'[^a-zA-Z0-9:/ -]', '', x))  # Remove special characters
    return df

def is_valid_uuid(value):
    """Check if a value is a valid UUID"""
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False

def clean_shipments(df):
    """Clean and validate shipments data"""

    start_time = time.time()
    print("Cleaning shipments data...")

    # Standardize carrier names
    carrier_mapping = {
        "fedex": "FedEx",
        "ups": "UPS",
        "dhl": "DHL",
        "usps": "USPS"
    }

    df = clean_common(df)  # Apply basic cleaning first

    # Standardize carrier names & remove leading hyphens
    if "carrier" in df.columns:
        df["carrier"] = df["carrier"].str.lower().map(carrier_mapping).fillna(df["carrier"])
        df["carrier"] = df["carrier"].apply(lambda x: re.sub(r'^-+', '', x))  # Remove leading hyphens

    # Preserve datetime format but clean extra characters & last 3 digits if too long
    for column in ["shipment_date", "delivery_date"]:
        if column in df.columns:
            df[column] = df[column].apply(lambda x: re.sub(r'[^0-9:/ -]', '', x))  # Keep valid date characters
            df[column] = df[column].apply(lambda x: x[:-3] if len(x) > 10 else x)  # Remove last 3 digits if too long

    # Validate UUIDs
    df = df[df["id"].apply(is_valid_uuid) & df["order_id"].apply(is_valid_uuid)]

    # Remove duplicate IDs safely
    df = df.drop_duplicates(subset="id")

    processing_time = time.time() - start_time
    print(f"Shipments data cleaned in {processing_time:.2f} seconds")

    return df

def clean_refunds(df, orders_df, products_df):
    """Clean and validate refunds data"""

    start_time = time.time()
    print("Cleaning refunds data...")

    df = clean_common(df)  # Apply basic cleaning first

    # Validate UUIDs
    df = df[df["id"].apply(is_valid_uuid) & df["order_id"].apply(is_valid_uuid) & df["product_id"].apply(is_valid_uuid)]

    # Ensure order_id exists in orders.csv
    df = df[df["order_id"].isin(orders_df["id"])]

    # Ensure product_id exists in products.csv
    df = df[df["product_id"].isin(products_df["id"])]

    # Ensure reason is non-empty
    df = df[df["reason"].str.strip() != ""]

    # **Only check if refund_amount is positive—don't modify values**
    df["refund_amount"] = df["refund_amount"].astype(str).apply(lambda x: re.sub(r'[^0-9.]$', '', x))  # Remove unwanted trailing characters
    df = df[df["refund_amount"].str.replace(",", "").astype(float) > 0]  # Keep valid positive refund amounts

    processing_time = time.time() - start_time
    print(f"Refunds data cleaned in {processing_time:.2f} seconds")

    return df

if __name__ == "__main__":
    # Load CSVs
    shipments_df = pd.read_csv("shipments.csv")
    refunds_df = pd.read_csv("refunds.csv")
    orders_df = pd.read_csv("orders.csv")  # For order validation
    products_df = pd.read_csv("products.csv")  # For product validation

    # Run cleaning functions
    cleaned_shipments_df = clean_shipments(shipments_df)
    cleaned_refunds_df = clean_refunds(refunds_df, orders_df, products_df)

    # **Divide refund_amount by 100 before saving**
    cleaned_refunds_df["refund_amount"] = cleaned_refunds_df["refund_amount"].astype(float) / 100

    # Save cleaned data
    cleaned_shipments_df.to_csv("cleaned_shipments.csv", index=False)
    cleaned_refunds_df.to_csv("cleaned_refunds.csv", index=False)

    print("\nCleaned data saved as cleaned_shipments.csv and cleaned_refunds.csv!")
