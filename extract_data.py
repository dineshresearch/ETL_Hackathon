import json

# Load the data from response.json
with open('response.json', 'r') as file:
    data = json.load(file)

# Check if shipping_performance_by_carrier exists and print its structure
if 'business_metrics' in data and 'shipping_performance_by_carrier' in data['business_metrics']:
    shipping_data = data['business_metrics']['shipping_performance_by_carrier']
    print("\nShipping Performance Data Structure:")
    print(f"Number of carriers: {len(shipping_data)}")
    
    if len(shipping_data) > 0:
        print("\nFirst carrier structure:")
        first_carrier = shipping_data[0]
        print(json.dumps(first_carrier, indent=2))
    else:
        print("No carriers found in the data")
else:
    print("Could not find shipping_performance_by_carrier in the JSON data")

# Extract the top 5 customers data
if 'business_metrics' in data and 'top_5_customers_by_total_spend' in data['business_metrics']:
    top_customers = data['business_metrics']['top_5_customers_by_total_spend']
    print("Top 5 Customers by Total Spend:")
    # Print the structure
    print("Structure of the first customer entry:")
    first_customer = top_customers[0]
    for key, value in first_customer.items():
        print(f"  - {key}: {value}")
    
    # Print all customers
    print("\nAll customers data:")
    for i, customer in enumerate(top_customers):
        print(f"Customer {i+1}:")
        print(f"  Data: {customer}")
else:
    print("Could not find top_5_customers_by_total_spend in the JSON data") 