import pandas as pd
import uuid
import re
import json
import time
import os


class DataValidator:
    """Class for validating different data types"""
    
    @staticmethod
    def is_valid_uuid(val):
        """Validate if a string is a valid UUID"""
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_email(email):
        """Validate if a string is a valid email"""
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    @staticmethod
    def is_valid_phone(phone):
        """Validate if a string is a valid 10-digit phone number"""
        return re.match(r"^\d{10}$", phone) is not None


class DataCleaner:
    """Class for cleaning and validating data from various sources"""
    
    def __init__(self, data_dir='downloads'):
        """Initialize DataCleaner with data directory path"""
        self.data_dir = data_dir
        self.validator = DataValidator()
        
        # Load all datasets
        self.customers = self._load_csv('customers.csv')
        self.products = self._load_csv('products.csv')
        self.orders = self._load_csv('orders.csv')
        self.shipments = self._load_csv('shipments.csv')
        self.refunds = self._load_csv('refunds.csv')
        
        # Clean datasets
        self.valid_customers = None
        self.valid_products = None
        self.valid_orders = None 
        self.valid_shipments = None
        self.valid_refunds = None

    def _load_csv(self, filename):
        """Load a CSV file from the data directory"""
        filepath = os.path.join(self.data_dir, filename)
        return pd.read_csv(filepath)
    
    def clean_customers(self):
        """Clean and validate customers data"""
        start_time = time.time()
        print("Cleaning customers data...")
        
        valid_customers = self.customers[
            self.customers['id'].apply(self.validator.is_valid_uuid) & 
            (self.customers['name'].str.strip() != '') & 
            (self.customers['email'].apply(self.validator.is_valid_email) | 
             self.customers['phone'].apply(self.validator.is_valid_phone))
        ]
        valid_customers.drop_duplicates(subset='id', inplace=True)
        
        self.valid_customers = valid_customers
        processing_time = time.time() - start_time
        print(f"Customers data cleaned in {processing_time:.2f} seconds")
        return valid_customers
    
    def clean_products(self):
        """Clean and validate products data"""
        start_time = time.time()
        print("Cleaning products data...")
        
        # Convert price and stock to numeric, coercing errors to NaN
        self.products['price'] = pd.to_numeric(self.products['price'], errors='coerce')
        self.products['stock'] = pd.to_numeric(self.products['stock'], errors='coerce')
        
        valid_products = self.products[
            self.products['id'].apply(self.validator.is_valid_uuid) & 
            (self.products['name'].str.strip() != '') & 
            (self.products['category'].isin(["Electronics", "Furniture", "Clothing", "Beauty", "Sports"])) & 
            (self.products['price'] > 0) & 
            (self.products['stock'] >= 0)
        ]
        
        # Remove special characters from the 'name' field
        valid_products['name'] = valid_products['name'].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
        valid_products['name'] = valid_products['name'].str.strip()
        
        valid_products.drop_duplicates(subset='id', inplace=True)
        
        self.valid_products = valid_products
        processing_time = time.time() - start_time
        print(f"Products data cleaned in {processing_time:.2f} seconds")
        return valid_products
    
    def clean_orders(self):
        """Clean and validate orders data"""
        start_time = time.time()
        print("Cleaning orders data...")
        
        # Convert quantity to numeric, coercing errors to NaN
        self.orders['quantity'] = pd.to_numeric(self.orders['quantity'], errors='coerce')
        
        # Clean and transform dates to YYYY-MM-DD format
        self.orders['date'] = pd.to_datetime(
            self.orders['date'].str.extract(r'(\d{4}-\d{2}-\d{2})')[0], 
            errors='coerce'
        )
        
        # Validate and clean orders
        valid_orders = self.orders[
            self.orders['id'].apply(self.validator.is_valid_uuid) & 
            self.orders['customer_id'].apply(self.validator.is_valid_uuid) & 
            self.orders['product_id'].apply(self.validator.is_valid_uuid) & 
            (self.orders['quantity'] >= 0) &
            self.orders['date'].notna()  # Ensure date is valid
        ]
        valid_orders.drop_duplicates(subset='id', inplace=True)
        
        self.valid_orders = valid_orders
        processing_time = time.time() - start_time
        print(f"Orders data cleaned in {processing_time:.2f} seconds")
        return valid_orders
    
    def clean_shipments(self):
        """Clean and validate shipments data"""
        start_time = time.time()
        print("Cleaning shipments data...")
        
        valid_shipments = self.shipments[
            self.shipments['id'].apply(self.validator.is_valid_uuid) & 
            self.shipments['order_id'].apply(self.validator.is_valid_uuid) & 
            self.shipments['carrier'].isin(["FedEx", "UPS", "DHL", "USPS"]) & 
            self.shipments['status'].isin(["Shipped", "Delivered", "Delayed", "Unknown"])
        ]
        valid_shipments.drop_duplicates(subset='id', inplace=True)
        
        self.valid_shipments = valid_shipments
        processing_time = time.time() - start_time
        print(f"Shipments data cleaned in {processing_time:.2f} seconds")
        return valid_shipments
    
    def clean_refunds(self):
        """Clean and validate refunds data"""
        start_time = time.time()
        print("Cleaning refunds data...")
        
        # Convert refund_amount to numeric, coercing errors to NaN
        self.refunds['refund_amount'] = pd.to_numeric(self.refunds['refund_amount'], errors='coerce')
        
        valid_refunds = self.refunds[
            self.refunds['id'].apply(self.validator.is_valid_uuid) & 
            self.refunds['order_id'].apply(self.validator.is_valid_uuid) & 
            self.refunds['product_id'].apply(self.validator.is_valid_uuid) & 
            (self.refunds['refund_amount'] > 0)
        ]
        valid_refunds.drop_duplicates(subset='id', inplace=True)
        
        self.valid_refunds = valid_refunds
        processing_time = time.time() - start_time
        print(f"Refunds data cleaned in {processing_time:.2f} seconds")
        return valid_refunds
    
    def clean_all_data(self):
        """Clean all datasets"""
        self.clean_customers()
        self.clean_products()
        self.clean_orders()
        self.clean_shipments()
        self.clean_refunds()


class MetricsCalculator:
    """Class for calculating business and data quality metrics"""
    
    def __init__(self, cleaner):
        """Initialize with a DataCleaner instance"""
        self.cleaner = cleaner
    
    def calculate_data_quality_metrics(self):
        """Calculate data quality metrics"""
        start_time = time.time()
        print("Calculating data quality metrics...")
        
        metrics = {
            "invalid_customers_records": len(self.cleaner.customers) - len(self.cleaner.valid_customers),
            "invalid_products_records": len(self.cleaner.products) - len(self.cleaner.valid_products),
            "invalid_orders_records": len(self.cleaner.orders) - len(self.cleaner.valid_orders),
            "invalid_shipments_records": len(self.cleaner.shipments) - len(self.cleaner.valid_shipments),
            "invalid_returns_records": len(self.cleaner.refunds) - len(self.cleaner.valid_refunds)
        }
        
        processing_time = time.time() - start_time
        print(f"Data quality metrics calculated in {processing_time:.2f} seconds")
        return metrics
    
    def calculate_top_customers(self):
        """Calculate top 5 customers by total spend"""
        start_time = time.time()
        print("Calculating top customers...")
        
        orders_with_customers = self.cleaner.valid_orders.merge(
            self.cleaner.valid_customers, 
            left_on='customer_id', 
            right_on='id'
        )
        
        top_customers = orders_with_customers.groupby(['customer_id', 'name']).agg(
            total_spent=('quantity', 'sum')
        ).nlargest(5, 'total_spent').reset_index()
        
        processing_time = time.time() - start_time
        print(f"Top customers calculated in {processing_time:.2f} seconds")
        return top_customers
    
    def calculate_top_products(self):
        """Calculate top 5 products by revenue"""
        start_time = time.time()
        print("Calculating top products...")
        
        orders_with_products = self.cleaner.valid_orders.merge(
            self.cleaner.valid_products, 
            left_on='product_id', 
            right_on='id'
        )
        
        orders_with_products['revenue'] = orders_with_products['quantity'] * orders_with_products['price']
        
        top_products = orders_with_products.groupby(['product_id', 'name']).agg(
            total_revenue=('revenue', 'sum')
        ).nlargest(5, 'total_revenue').reset_index()
        
        processing_time = time.time() - start_time
        print(f"Top products calculated in {processing_time:.2f} seconds")
        return top_products
    
    def calculate_shipping_performance(self):
        """Calculate shipping performance by carrier"""
        start_time = time.time()
        print("Calculating shipping performance...")
        
        shipping_performance = self.cleaner.valid_shipments.groupby('carrier').agg(
            total_shipments=('id', 'count'),
            on_time_deliveries=('status', lambda x: (x == 'Delivered').sum()),
            delayed_shipments=('status', lambda x: (x == 'Delayed').sum()),
            undelivered_shipments=('status', lambda x: (x == 'Unknown').sum())
        ).reset_index()
        
        processing_time = time.time() - start_time
        print(f"Shipping performance calculated in {processing_time:.2f} seconds")
        return shipping_performance
    
    def calculate_refund_analysis(self):
        """Calculate refund reason analysis"""
        start_time = time.time()
        print("Calculating refund analysis...")
        
        refund_reason_analysis = self.cleaner.valid_refunds.groupby('reason').agg(
            total_returns=('id', 'count'),
            total_refund_amount=('refund_amount', 'sum')
        ).reset_index()
        
        processing_time = time.time() - start_time
        print(f"Refund analysis calculated in {processing_time:.2f} seconds")
        return refund_reason_analysis
    
    def calculate_all_metrics(self):
        """Calculate all metrics and return as a dictionary"""
        data_quality_metrics = self.calculate_data_quality_metrics()
        top_customers = self.calculate_top_customers()
        top_products = self.calculate_top_products()
        shipping_performance = self.calculate_shipping_performance()
        refund_analysis = self.calculate_refund_analysis()
        
        valid_names = self.cleaner.valid_customers[['id', 'name']].rename(
            columns={'id': 'uuid'}
        ).to_dict(orient='records')
        
        return {
            "valid_names": valid_names,
            "data_quality_metrics": data_quality_metrics,
            "business_metrics": {
                "top_5_customers_by_total_spend": top_customers.to_dict(orient='records'),
                "top_5_products_by_revenue": top_products.to_dict(orient='records'),
                "shipping_performance_by_carrier": shipping_performance.to_dict(orient='records'),
                "refund_reason_analysis": refund_analysis.to_dict(orient='records')
            }
        }


def main():
    """Main function to run the ETL pipeline"""
    # Start timing
    total_start_time = time.time()
    print("Starting ETL pipeline...")
    
    # Step 1: Clean data
    data_start_time = time.time()
    cleaner = DataCleaner()
    cleaner.clean_all_data()
    data_time = time.time() - data_start_time
    
    # Step 2: Calculate metrics
    metrics_start_time = time.time()
    calculator = MetricsCalculator(cleaner)
    response = calculator.calculate_all_metrics()
    metrics_time = time.time() - metrics_start_time
    
    # Step 3: Save to JSON
    json_start_time = time.time()
    print("Writing results to JSON...")
    json_string = json.dumps(response, indent=2)
    file_path = 'response.json'
    with open(file_path, 'w') as json_file:
        json_file.write(json_string)
    json_time = time.time() - json_start_time
    
    # Calculate total time
    total_time = time.time() - total_start_time
    
    # Print timing information
    print("\n" + "="*50)
    print("ETL PIPELINE EXECUTION SUMMARY")
    print("="*50)
    print(f"Data cleaning time: {data_time:.2f}s ({data_time/total_time*100:.1f}%)")
    print(f"Metrics calculation time: {metrics_time:.2f}s ({metrics_time/total_time*100:.1f}%)")
    print(f"JSON writing time: {json_time:.2f}s ({json_time/total_time*100:.1f}%)")
    print(f"Total execution time: {total_time:.2f}s")
    print("="*50)


if __name__ == "__main__":
    main()






