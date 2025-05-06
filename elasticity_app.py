import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Price Elasticity & Volume Analysis Tool")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your Excel file (MSA or Diversity data)", type=["xlsx"])

if uploaded_file:
    sheet_names = pd.ExcelFile(uploaded_file).sheet_names
    selected_sheet = st.selectbox("Select a sheet", sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

    st.subheader("Raw Data Preview")
    st.write(df.head())

    st.markdown("---")

    # --- User Input for Columns ---
    st.subheader("Column Selection")
    price_col = st.selectbox("Select the Price column", df.columns)
    volume_col = st.selectbox("Select the Volume column", df.columns)
    year_col = st.selectbox("Select the Year column", df.columns)
    market_col = st.selectbox("Select optional Market Index column (or None)", ["None"] + list(df.columns))

    # --- Log Transformation ---
    df = df.dropna(subset=[price_col, volume_col, year_col])
    df['log_price'] = np.log(df[price_col])
    df['log_volume'] = np.log(df[volume_col])

    if market_col != "None":
        df = df.dropna(subset=[market_col])
        df['log_market'] = np.log(df[market_col])

    # --- Dummy Variables for Year ---
    year_dummies = pd.get_dummies(df[year_col], prefix='year', drop_first=True)

    # --- Regression Model ---
    st.subheader("Elasticity Estimation")

    X_cols = ['log_price']
    if market_col != "None":
        X_cols.append('log_market')

    X = df[X_cols].join(year_dummies)
    X = sm.add_constant(X)
    y = df['log_volume']

    model = sm.OLS(y, X).fit()
    st.write(model.summary())

    # --- Plotting ---
    st.subheader("Volume vs Price (Log-Log Plot)")
    fig, ax = plt.subplots()
    ax.scatter(df['log_price'], df['log_volume'], alpha=0.5)
    ax.set_xlabel("Log(Price)")
    ax.set_ylabel("Log(Volume)")
    st.pyplot(fig)

    # --- Scenario Analysis ---
    st.subheader("Scenario Analysis")
    elasticity = model.params.get('log_price', None)
    if elasticity:
        base_volume = df[volume_col].mean()
        base_price = df[price_col].mean()

        price_change = st.slider("Simulate % Price Change", -50, 50, 0)
        price_multiplier = 1 + price_change / 100
        new_price = base_price * price_multiplier
        predicted_volume = base_volume * ((new_price / base_price) ** elasticity)

        st.metric("Base Volume", f"{base_volume:,.0f}")
        st.metric("New Volume", f"{predicted_volume:,.0f}")
        st.metric("Estimated Elasticity", f"{elasticity:.2f}")
    else:
        st.warning("Elasticity estimation failed or is not statistically significant.")
