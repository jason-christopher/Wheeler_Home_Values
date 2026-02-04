import streamlit as st
import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# Page config
st.set_page_config(
    page_title="Wheeler Home Values",
    page_icon="🏠",
    layout="wide"
)

@st.cache_data
def load_data():
    """Load and preprocess the property data."""
    df = pd.read_csv('output.csv')

    # Remove specific addresses
    remove_addresses = ['900 HANGAR DR', '934 HANGAR DR']
    df = df[~df['address'].isin(remove_addresses)]

    # Convert string representations of dictionaries
    df['market_values'] = df['market_values'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else {})
    df['sales_prices'] = df['sales_prices'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else {})

    # Extract most recent values
    get_most_recent = lambda x: next(iter(x.values())) if x else None
    df['most_recent_sales_year'] = df['sales_prices'].apply(lambda x: next(iter(x.keys())) if x else None)
    df['most_recent_sales_price'] = df['sales_prices'].apply(get_most_recent)
    df['most_recent_market_value'] = df['market_values'].apply(get_most_recent)

    # Create derived features
    df['total_sqft'] = df['square_feet'].fillna(0) + df['unfin_attic_sqft'].fillna(0) + df['garage_apt_sqft'].fillna(0)
    df['has_garage'] = df['garage_sqft'].apply(lambda x: 1 if x > 0 else 0)
    df['has_apt'] = df['garage_apt_sqft'].apply(lambda x: 1 if x > 0 else 0)

    # Calculate price per sqft
    df['price_per_sqft'] = df.apply(
        lambda row: row['most_recent_sales_price'] / row['total_sqft'] if row['total_sqft'] > 0 and pd.notna(row['most_recent_sales_price']) else None,
        axis=1
    )

    return df

@st.cache_resource
def train_models(df):
    """Train the prediction models."""
    # Filter data
    filtered_df = df.dropna(subset=['square_feet', 'most_recent_sales_price', 'most_recent_market_value'])

    # Remove outliers
    column = 'price_per_sqft'
    filtered_df = filtered_df.dropna(subset=[column])
    mean = filtered_df[column].mean()
    std = filtered_df[column].std()
    z_scores = (filtered_df[column] - mean) / std
    filtered_df = filtered_df[np.abs(z_scores) <= 2]

    # Prepare features
    X = filtered_df[['total_sqft', 'year_built', 'bedrooms', 'bathrooms', 'has_garage', 'has_apt']].values
    y_market = filtered_df['most_recent_market_value'].values

    # Preprocessing
    numerical_columns = [0, 1, 2, 3]
    binary_columns = [4, 5]
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_columns),
            ('binary', 'passthrough', binary_columns)
        ])

    # Train market value model (Ridge)
    X_train, X_test, y_train, y_test = train_test_split(X, y_market, test_size=0.2, random_state=1)
    market_model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', Ridge(alpha=1.0))
    ])
    market_model.fit(X_train, y_train)

    # Train sales price model (recent sales only)
    recent_df = filtered_df[filtered_df['most_recent_sales_year'] >= 2024]
    X_sales = recent_df[['total_sqft', 'year_built', 'bedrooms', 'bathrooms', 'has_garage', 'has_apt']].values
    y_sales = recent_df['most_recent_sales_price'].values

    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(X_sales, y_sales, test_size=0.3, random_state=0)
    sales_model = LinearRegression()
    sales_model.fit(X_train_s, y_train_s)

    return market_model, sales_model

def create_sales_dataframe(df):
    """Create expanded sales dataframe for trend analysis."""
    filtered_df = df.dropna(subset=['square_feet', 'most_recent_sales_price'])

    new_rows = []
    for _, row in filtered_df.iterrows():
        address = row['address']
        total_sqft = row['total_sqft']
        sales_data = row['sales_prices']

        for year, price in sales_data.items():
            year = int(year)
            sales_price = int(price)
            sales_price_sqft = price / total_sqft if total_sqft > 0 else 0
            new_rows.append({
                'address': address,
                'total_sqft': total_sqft,
                'year': year,
                'sales_price': sales_price,
                'price_per_sqft': sales_price_sqft
            })

    return pd.DataFrame(new_rows)

# Load data and models
df = load_data()
market_model, sales_model = train_models(df)

# Title
st.title("🏠 Wheeler Home Values Dashboard")
st.markdown("Analyze property data from the Wheeler/Oklahoma County area")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Property Explorer", "🔮 Price Predictions", "📈 Market Trends"])

# ============ TAB 1: Property Explorer ============
with tab1:
    st.header("Property Explorer")
    st.markdown("Filter and browse properties by their features")

    # Filters in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        min_sqft = st.number_input("Min Square Feet", value=0, step=100)
        max_sqft = st.number_input("Max Square Feet", value=int(df['total_sqft'].max() or 5000), step=100)

    with col2:
        min_beds = st.selectbox("Min Bedrooms", options=[0, 1, 2, 3, 4, 5], index=0)
        max_beds = st.selectbox("Max Bedrooms", options=[1, 2, 3, 4, 5, 6], index=5)

    with col3:
        min_baths = st.selectbox("Min Bathrooms", options=[0.0, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], index=0)
        has_garage_filter = st.selectbox("Has Garage?", options=["Any", "Yes", "No"])

    with col4:
        min_year = st.number_input("Min Year Built", value=2018, step=1)
        max_year = st.number_input("Max Year Built", value=2025, step=1)

    # Apply filters
    filtered = df.copy()
    filtered = filtered[filtered['total_sqft'] >= min_sqft]
    filtered = filtered[filtered['total_sqft'] <= max_sqft]
    filtered = filtered[filtered['bedrooms'] >= min_beds]
    filtered = filtered[filtered['bedrooms'] <= max_beds]
    filtered = filtered[filtered['bathrooms'] >= min_baths]
    filtered = filtered[filtered['year_built'] >= min_year]
    filtered = filtered[filtered['year_built'] <= max_year]

    if has_garage_filter == "Yes":
        filtered = filtered[filtered['has_garage'] == 1]
    elif has_garage_filter == "No":
        filtered = filtered[filtered['has_garage'] == 0]

    # Display results
    st.markdown(f"**Found {len(filtered)} properties**")

    # Select columns to display
    display_cols = ['address', 'total_sqft', 'bedrooms', 'bathrooms', 'year_built',
                    'most_recent_sales_price', 'most_recent_market_value', 'garage_sqft']

    display_df = filtered[display_cols].copy()
    display_df.columns = ['Address', 'Total Sq Ft', 'Beds', 'Baths', 'Year Built',
                          'Last Sale Price', 'Market Value', 'Garage Sq Ft']

    # Format currency columns
    display_df['Last Sale Price'] = display_df['Last Sale Price'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
    display_df['Market Value'] = display_df['Market Value'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ============ TAB 2: Price Predictions ============
with tab2:
    st.header("Price Predictions")
    st.markdown("Enter property details to get estimated market value and sales price")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Property Details")
        pred_sqft = st.slider("Total Square Footage", min_value=500, max_value=4000, value=1800, step=50)
        pred_year = st.slider("Year Built", min_value=2018, max_value=2025, value=2021)
        pred_beds = st.selectbox("Bedrooms", options=[1, 2, 3, 4, 5], index=2)
        pred_baths = st.selectbox("Bathrooms", options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5], index=3)
        pred_garage = st.checkbox("Has Garage", value=True)
        pred_apt = st.checkbox("Has Garage Apartment", value=False)

    with col2:
        st.subheader("Predicted Values")

        # Make predictions
        features = [[pred_sqft, pred_year, pred_beds, pred_baths, int(pred_garage), int(pred_apt)]]

        predicted_market = market_model.predict(features)[0]
        predicted_sales = sales_model.predict(features)[0]

        # Display predictions
        st.metric("Estimated Market Value", f"${predicted_market:,.0f}")
        st.metric("Estimated Sales Price", f"${predicted_sales:,.0f}")

        # Price per sqft
        price_per_sqft = predicted_sales / pred_sqft
        st.metric("Price per Sq Ft", f"${price_per_sqft:,.0f}")

        st.markdown("---")
        st.caption("*Market value predictions use Ridge Regression trained on all available data.*")
        st.caption("*Sales price predictions use Linear Regression trained on 2024+ sales data.*")

# ============ TAB 3: Market Trends ============
with tab3:
    st.header("Market Trends")
    st.markdown("Analyze price trends over time in the Wheeler area")

    # Create sales dataframe
    df_sales = create_sales_dataframe(df)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Properties", len(df))
    with col2:
        st.metric("Total Sales Records", len(df_sales))
    with col3:
        avg_price_2024 = df_sales[df_sales['year'] >= 2024]['price_per_sqft'].mean()
        st.metric("Avg $/SqFt (2024+)", f"${avg_price_2024:,.0f}")
    with col4:
        avg_price_2019 = df_sales[df_sales['year'] == 2019]['price_per_sqft'].mean()
        pct_change = ((avg_price_2024 - avg_price_2019) / avg_price_2019) * 100
        st.metric("Price Change (2019-2024)", f"+{pct_change:.1f}%")

    st.markdown("---")

    # Chart selection
    chart_type = st.selectbox("Select Chart", options=[
        "All Sales - Price/Sq Ft by Year",
        "Initial Sales - Price/Sq Ft by Year",
        "Sales Volume by Year",
        "Average Sales Price by Year"
    ])

    fig, ax = plt.subplots(figsize=(10, 6))

    if chart_type == "All Sales - Price/Sq Ft by Year":
        ax.scatter(df_sales['year'], df_sales['price_per_sqft'], alpha=0.6, color='blue')

        # Trend line
        coefficients = np.polyfit(df_sales['year'], df_sales['price_per_sqft'], 2)
        trend_line = np.poly1d(coefficients)
        x_values = np.linspace(df_sales['year'].min(), df_sales['year'].max(), 100)
        ax.plot(x_values, trend_line(x_values), color='red', linewidth=2, label='Trend')

        ax.set_xlabel('Year')
        ax.set_ylabel('Price per Square Foot ($)')
        ax.set_title('All Sales - Price per Square Foot by Year')
        ax.grid(True, alpha=0.3)

    elif chart_type == "Initial Sales - Price/Sq Ft by Year":
        df_initial = df_sales.sort_values(by='year').groupby('address').head(1)
        ax.scatter(df_initial['year'], df_initial['price_per_sqft'], alpha=0.6, color='green')

        # Trend line
        coefficients = np.polyfit(df_initial['year'], df_initial['price_per_sqft'], 2)
        trend_line = np.poly1d(coefficients)
        x_values = np.linspace(df_initial['year'].min(), df_initial['year'].max(), 100)
        ax.plot(x_values, trend_line(x_values), color='red', linewidth=2, label='Trend')

        ax.set_xlabel('Year')
        ax.set_ylabel('Price per Square Foot ($)')
        ax.set_title('Initial Sales - Price per Square Foot by Year')
        ax.grid(True, alpha=0.3)

    elif chart_type == "Sales Volume by Year":
        sales_by_year = df_sales.groupby('year').size()
        ax.bar(sales_by_year.index, sales_by_year.values, color='steelblue')
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of Sales')
        ax.set_title('Sales Volume by Year')
        ax.grid(True, alpha=0.3, axis='y')

    elif chart_type == "Average Sales Price by Year":
        avg_by_year = df_sales.groupby('year')['sales_price'].mean()
        ax.bar(avg_by_year.index, avg_by_year.values, color='coral')
        ax.set_xlabel('Year')
        ax.set_ylabel('Average Sales Price ($)')
        ax.set_title('Average Sales Price by Year')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    st.pyplot(fig)

    # Year-over-year stats table
    st.markdown("### Year-over-Year Statistics")
    yearly_stats = df_sales.groupby('year').agg({
        'sales_price': ['count', 'mean', 'median'],
        'price_per_sqft': 'mean'
    }).round(0)
    yearly_stats.columns = ['# Sales', 'Avg Price', 'Median Price', 'Avg $/SqFt']
    yearly_stats['Avg Price'] = yearly_stats['Avg Price'].apply(lambda x: f"${x:,.0f}")
    yearly_stats['Median Price'] = yearly_stats['Median Price'].apply(lambda x: f"${x:,.0f}")
    yearly_stats['Avg $/SqFt'] = yearly_stats['Avg $/SqFt'].apply(lambda x: f"${x:,.0f}")
    st.dataframe(yearly_stats, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Data sourced from Oklahoma County Assessor's Office")
