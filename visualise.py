import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
import json
from plotly.subplots import make_subplots

# Load real data from response.json
try:
    with open('response.json', 'r') as file:
        json_data = json.load(file)
    
    # Extract top 5 customers data
    if 'business_metrics' in json_data and 'top_5_customers_by_total_spend' in json_data['business_metrics']:
        top_customers_data = json_data['business_metrics']['top_5_customers_by_total_spend']
        # Create DataFrame for top customers
        real_top_customers_df = pd.DataFrame([
            {
                'customers': customer['name'],
                'total_spend': customer['total_spent']
            } for customer in top_customers_data
        ])
        print("Successfully loaded top customers data from response.json")
    else:
        real_top_customers_df = None
        print("Could not find top_5_customers_by_total_spend in response.json")
        
    # Extract top 5 products data
    if 'business_metrics' in json_data and 'top_5_products_by_revenue' in json_data['business_metrics']:
        top_products_data = json_data['business_metrics']['top_5_products_by_revenue']
        # Create DataFrame for top products
        real_top_products_df = pd.DataFrame([
            {
                'products': product['name'],
                'revenue': product['total_revenue']
            } for product in top_products_data
        ])
        print("Successfully loaded top products data from response.json")
    else:
        real_top_products_df = None
        print("Could not find top_5_products_by_revenue in response.json")
        
    # Extract shipping performance by carrier data
    if 'business_metrics' in json_data and 'shipping_performance_by_carrier' in json_data['business_metrics']:
        shipping_performance_data = json_data['business_metrics']['shipping_performance_by_carrier']
        # Create DataFrame for shipping performance with calculated metrics
        real_shipping_performance_df = pd.DataFrame([
            {
                'carrier': carrier['carrier'],
                'total_shipments': carrier['total_shipments'],
                'on_time_deliveries': carrier['on_time_deliveries'],
                'delayed_shipments': carrier['delayed_shipments'],
                'undelivered_shipments': carrier['undelivered_shipments']
            } for carrier in shipping_performance_data
        ])
        
        # Calculate derived metrics
        real_shipping_performance_df['on_time_delivery_rate'] = real_shipping_performance_df['on_time_deliveries'] / real_shipping_performance_df['total_shipments']
        real_shipping_performance_df['lost_packages_rate'] = real_shipping_performance_df['undelivered_shipments'] / real_shipping_performance_df['total_shipments']
        # We don't have average delivery time in the data, so we'll create a placeholder
        real_shipping_performance_df['average_delivery_time'] = np.random.uniform(1, 5, len(real_shipping_performance_df))
        
        print("Successfully loaded shipping performance data from response.json")
    else:
        real_shipping_performance_df = None
        print("Could not find shipping_performance_by_carrier in response.json")
        
    # Extract refund reason analysis data
    if 'business_metrics' in json_data and 'refund_reason_analysis' in json_data['business_metrics']:
        refund_reason_data = json_data['business_metrics']['refund_reason_analysis']
        # Create DataFrame for refund reasons
        real_refund_reason_df = pd.DataFrame([
            {
                'reason': reason['reason'],
                'total_returns': reason['total_returns'],
                'total_refund_amount': reason['total_refund_amount']
            } for reason in refund_reason_data
        ])
        print("Successfully loaded refund reason analysis data from response.json")
    else:
        real_refund_reason_df = None
        print("Could not find refund_reason_analysis in response.json")
except Exception as e:
    print(f"Error loading response.json: {e}")
    real_top_customers_df = None
    real_top_products_df = None
    real_shipping_performance_df = None
    real_refund_reason_df = None

# Sample data for time series visualizations
data = {
    'date': pd.date_range(start='2023-01-01', periods=100, freq='D'),
    'spend': np.random.rand(100) * 1000,
    'shipping_performance': np.random.rand(100) * 100,
    'refunds': np.random.rand(100) * 50,
}
df = pd.DataFrame(data)

# Function to detect anomalies using z-score
def detect_anomalies(series, threshold=2.5):
    """Detect anomalies in a time series using z-score."""
    z_scores = np.abs(stats.zscore(series))
    return z_scores > threshold

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.Div([
        html.H1("Business Metrics Dashboard", 
                style={'textAlign': 'center', 'color': '#2C3E50', 'fontFamily': 'Arial, sans-serif', 'marginBottom': '20px'})
    ], style={'backgroundColor': '#F7F9F9', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'}),
    
    # Add a hidden div for callback triggering
    html.Div(id='trigger-container', style={'display': 'none'}),
    
    html.Div([
        dcc.Graph(id='top-customers-chart'),
        dcc.Graph(id='top-products-chart'),
        dcc.Graph(id='shipping-carriers-chart', style={'marginBottom': '40px'}),
        dcc.Graph(id='refund-reasons-chart')
    ], style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': '#E8F8F5', 'borderRadius': '10px'})
], style={'margin': '20px', 'fontFamily': 'Arial, sans-serif'})

# Callback to update charts - using a proper component ID that exists in layout
@app.callback(
    [Output('top-customers-chart', 'figure'),
     Output('top-products-chart', 'figure'),
     Output('shipping-carriers-chart', 'figure'),
     Output('refund-reasons-chart', 'figure')],
    [Input('trigger-container', 'children')]  # Use the hidden div as input trigger
)
def update_charts(_):
    # Create top 5 customers chart
    top_customers_fig = create_top_customers_chart()
    
    # Create top 5 products chart
    top_products_fig = create_top_products_chart()
    
    # Create shipping carriers chart
    shipping_carriers_fig = create_shipping_carriers_chart()
    
    # Create refund reasons chart
    refund_reasons_fig = create_refund_reasons_chart()
    
    return top_customers_fig, top_products_fig, shipping_carriers_fig, refund_reasons_fig

# Function to create shipping performance by carrier chart
def create_shipping_carriers_chart():
    """Create a horizontal bar chart showing shipping performance by carrier."""
    # Use real data from response.json
    if real_shipping_performance_df is not None:
        shipping_data = real_shipping_performance_df
    else:
        # Create empty DataFrame if no data available
        shipping_data = pd.DataFrame(columns=['carrier', 'total_shipments', 'on_time_delivery_rate', 'average_delivery_time', 'lost_packages_rate'])
        print("Warning: No shipping performance data available")
    
    # Sort data by total shipments for better visualization
    shipping_data = shipping_data.sort_values('total_shipments', ascending=False)
    
    # Create figure with subplot to have better control over layout
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]],
        subplot_titles=["Shipping Performance by Carrier"]
    )
    
    # Add total shipments bars
    fig.add_trace(
        go.Bar(
            y=shipping_data['carrier'],
            x=shipping_data['total_shipments'],
            name='Total Shipments',
            orientation='h',
            marker=dict(color='#3498DB'),
            text=shipping_data['total_shipments'].apply(lambda x: f"{x:,}"),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Total Shipments: %{text}<extra></extra>'
        ),
        row=1, col=1, secondary_y=False
    )
    
    # Calculate percentage metrics for easier understanding
    on_time_pct = shipping_data['on_time_delivery_rate'] * 100
    lost_pct = shipping_data['lost_packages_rate'] * 100
    
    # Add on-time delivery percentage bars (thin, green)
    fig.add_trace(
        go.Bar(
            y=shipping_data['carrier'],
            x=on_time_pct,
            name='On-Time Delivery %',
            orientation='h',
            marker=dict(color='#27AE60'),
            text=on_time_pct.apply(lambda x: f"{x:.1f}%"),
            textposition='auto',
            width=0.5,  # Make bars thinner
            hovertemplate='<b>%{y}</b><br>On-Time Rate: %{text}<extra></extra>'
        ),
        row=1, col=1, secondary_y=True
    )
    
    # Add lost packages percentage (red markers)
    fig.add_trace(
        go.Scatter(
            y=shipping_data['carrier'],
            x=lost_pct,
            mode='markers+text',
            name='Lost Package %',
            marker=dict(
                color='#E74C3C',
                size=16,
                symbol='diamond',
                line=dict(width=1, color='#7F0000')
            ),
            text=lost_pct.apply(lambda x: f"{x:.1f}%"),
            textposition='middle right',
            hovertemplate='<b>%{y}</b><br>Lost Package Rate: %{text}<extra></extra>'
        ),
        row=1, col=1, secondary_y=True
    )
    
    # Update layout for better readability
    fig.update_layout(
        title={
            'text': 'Shipping Performance by Carrier',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24, color='#1E1E1E', family="Arial, sans-serif")
        },
        barmode='group',
        plot_bgcolor='rgba(245, 245, 245, 0.8)',
        paper_bgcolor='rgba(250, 250, 250, 0.9)',
        height=600,  # Increased height for better visualization
        margin=dict(l=100, r=100, t=100, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,  # Centered legend
            bgcolor='rgba(255, 255, 255, 0.7)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            borderwidth=1
        ),
        hovermode='closest',
        # Add secondary x-axis title using annotations
        annotations=[
            dict(
                x=0.5,
                y=-0.05,
                xref='paper',
                yref='paper',
                text='Percentage (%)',
                showarrow=False,
                font=dict(size=14, family="Arial, sans-serif"),
            ),
            dict(
                xref="paper", yref="paper",
                x=0.5, y=-0.15,
                text="Blue bars: Total Shipments | Green bars: On-Time Delivery % | Red diamonds: Lost Package %",
                showarrow=False,
                font=dict(size=12),
                align="center",
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="rgba(0, 0, 0, 0.2)",
                borderwidth=1,
                borderpad=4
            )
        ]
    )
    
    # Update primary x-axis (total shipments)
    fig.update_xaxes(
        title_text='Total Shipments',
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(0, 0, 0, 0.1)',
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='rgba(0, 0, 0, 0.2)',
        title_font=dict(size=14, family="Arial, sans-serif"),
        row=1, col=1
    )
    
    # Update y-axis
    fig.update_yaxes(
        title_text='Carrier',
        automargin=True,
        title_font=dict(size=14, family="Arial, sans-serif"),
        row=1, col=1
    )
    
    return fig

# Function to create top 5 products chart
def create_top_products_chart():
    """Create a bar chart showing the top 5 products by revenue using real data."""
    # Use real data from response.json
    if real_top_products_df is not None:
        top_products = real_top_products_df
    else:
        # Create empty DataFrame if no data available
        top_products = pd.DataFrame(columns=['products', 'revenue'])
        print("Warning: No product data available")
    
    # Create horizontal bar chart
    fig = px.bar(
        top_products,
        y='products',
        x='revenue',
        orientation='h',
        title='Top 5 Products by Revenue',
        labels={'revenue': 'Revenue ($)', 'products': 'Product'},
        color='revenue',
        color_continuous_scale='Plasma'  # Different color scale from customers chart
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        coloraxis_showscale=False,
        height=500
    )
    
    return fig

# Function to create top 5 customers chart
def create_top_customers_chart():
    """Create a bar chart showing the top 5 customers by total spend using real data."""
    # Use real data from response.json
    if real_top_customers_df is not None:
        top_customers = real_top_customers_df
    else:
        # Create empty DataFrame if no data available
        top_customers = pd.DataFrame(columns=['customers', 'total_spend'])
        print("Warning: No customer data available")
    
    # Create horizontal bar chart
    fig = px.bar(
        top_customers,
        y='customers',
        x='total_spend',
        orientation='h',
        title='Top 5 Customers by Total Spend',
        labels={'total_spend': 'Total Spend ($)', 'customers': 'Customer'},
        color='total_spend',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        coloraxis_showscale=False,
        height=500
    )
    
    return fig

# Function to create refund reasons chart
def create_refund_reasons_chart():
    """Create a horizontal bar chart showing refund reasons analysis."""
    # Use real data from response.json
    if real_refund_reason_df is not None:
        refund_data = real_refund_reason_df
    else:
        # Create sample DataFrame if no data available
        refund_data = pd.DataFrame({
            'reason': ['Defective', 'Wrong Size', 'Damaged', 'Not as Described', 'Late Delivery'],
            'total_returns': [120, 85, 65, 45, 30],
            'total_refund_amount': [4500, 3200, 2800, 1900, 1200]
        })
        print("Warning: No refund reason data available, using sample data")
    
    # Sort data by total returns for better visualization
    refund_data = refund_data.sort_values('total_returns')
    
    # Create horizontal bar chart with custom styling
    fig = go.Figure()
    
    # Add bars with customized appearance
    fig.add_trace(
        go.Bar(
            y=refund_data['reason'],
            x=refund_data['total_refund_amount'],
            orientation='h',
            name='Refund Amount',
            marker=dict(
                color='rgba(142, 68, 173, 0.8)',
                line=dict(color='rgba(111, 45, 168, 1.0)', width=1)
            ),
            text=refund_data['total_refund_amount'].apply(lambda x: f"${x:,.2f}"),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Refund Amount: %{text}<br>Returns: %{customdata}<extra></extra>',
            customdata=refund_data['total_returns']
        )
    )
    
    # Update layout for better readability
    fig.update_layout(
        title={
            'text': 'Refund Reasons Analysis',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24, color='#1E1E1E', family="Arial, sans-serif")
        },
        plot_bgcolor='rgba(245, 245, 245, 0.8)',
        paper_bgcolor='rgba(250, 250, 250, 0.9)',
        height=500,
        margin=dict(l=100, r=40, t=100, b=40),
        xaxis_title='Total Refund Amount ($)',
        yaxis_title='Refund Reason',
        hovermode='closest',
        annotations=[
            dict(
                xref="paper", yref="paper",
                x=0.5, y=-0.15,
                text="Size of bars represents total refund amount, hover to see number of returns",
                showarrow=False,
                font=dict(size=12),
                align="center",
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="rgba(0, 0, 0, 0.2)",
                borderwidth=1,
                borderpad=4
            )
        ]
    )
    
    # Add axis styling
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(0, 0, 0, 0.1)',
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='rgba(0, 0, 0, 0.2)',
        title_font=dict(size=14, family="Arial, sans-serif"),
        # Adjust tick spacing to 3m instead of default (likely 0.5m)
        dtick=3000000  # 3 million interval
    )
    
    fig.update_yaxes(
        automargin=True,
        title_font=dict(size=14, family="Arial, sans-serif"),
        categoryorder='total ascending'  # Display in ascending order of values
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
### Explanation

# - **Dash App**: This code sets up a Dash app with a simple layout containing a date picker and three graphs.
# - **Date Picker**: Allows users to filter data by date range.
# - **Interactive Charts**: Uses Plotly to create line charts for spend, shipping performance, and refunds over time.
# - **Callbacks**: Updates the charts based on the selected date range.

### Running the Dashboard

# 1. Save the code in a Python file, e.g., `dashboard.py`.
# 2. Run the file using Python:
#    ```bash
#    python dashboard.py
#    ```
# 3. Open a web browser and go to `http://127.0.0.1:8050` to view the dashboard.

# This setup provides a basic interactive dashboard. You can expand it with more features, such as anomaly tracking, by adding additional data processing and visualization logic. Let me know if you need further customization or additional features!
