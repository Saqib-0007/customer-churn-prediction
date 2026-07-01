import streamlit as st
import joblib
import pandas as pd

from database.db import engine

# comment out false for mysql but then it will run locally
USE_MYSQL = True
USE_MYSQL = False



# -----------------------------------
# Page Configuration
# -----------------------------------

st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="wide"
)

# -----------------------------------
# Load CSS
# -----------------------------------

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -----------------------------------
# Load Model
# -----------------------------------

@st.cache_resource
def load_model():
    return joblib.load("model/xgboost_churn_model.pkl")

# -----------------------------------
# Load Data
# -----------------------------------

# @st.cache_data
# def load_data():
#     original_df = pd.read_sql("SELECT * FROM customers", engine)
#     processed_df = pd.read_sql("SELECT * FROM processed_customers", engine)
#     return original_df, processed_df

@st.cache_data
def load_data():

    if USE_MYSQL:

        original_df = pd.read_sql(
            "SELECT * FROM customers",
            engine
        )

        processed_df = pd.read_sql(
            "SELECT * FROM processed_customers",
            engine
        )

    else:

        original_df = pd.read_csv(
            "data/customer_churn.csv"
        )

        processed_df = pd.read_csv(
            "data/customer_churn_processed.csv"
        )

    return original_df, processed_df

model = load_model()
df, processed_df = load_data()

# -----------------------------------
# Header
# -----------------------------------

st.title("📊 Customer Churn Prediction Dashboard")

st.markdown(
    """
### AI Powered Customer Retention Analysis
Predict customer churn using a trained XGBoost Machine Learning model.
"""
)

# -----------------------------------
# Dashboard Metrics
# -----------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Customers", len(df))

with col2:
    st.metric("Model", "XGBoost")

with col3:
    st.metric("Accuracy", "82.07%")

st.divider()

# -----------------------------------
# Customer Lookup
# -----------------------------------

st.subheader("🔍 Customer Lookup")

customer_id = st.selectbox(
    "Search Customer ID",
    options=sorted(df["customerID"].tolist()),
    index=None,
    placeholder="Start typing a Customer ID..."
)

# -----------------------------------
# Customer Details
# -----------------------------------

if customer_id:

    customer = df[df["customerID"] == customer_id]

    if customer.empty:

        st.error("Customer not found.")

    else:

        # customer = customer.reset_index(drop=True)

        # processed_customer = processed_df[
        #     processed_df["customerID"] == customer_id
        # ].drop(columns=["customerID"])
        
        if USE_MYSQL:

            customer = customer.reset_index(drop=True)

            processed_customer = processed_df[
                processed_df["customerID"] == customer_id
            ].drop(columns=["customerID"])

        else:

            original_index = customer.index[0]

            customer = customer.reset_index(drop=True)

            processed_customer = processed_df.iloc[[original_index]].drop(columns=["customerID"])

        senior = (
            "Yes"
            if customer.loc[0, "SeniorCitizen"] == 1
            else "No"
        )

        tenure = customer.loc[0, "tenure"]

        st.subheader("👤 Customer Profile")

        col1, col2 = st.columns(2)

        with col1:

            st.write(f"**Customer ID:** {customer.loc[0,'customerID']}")
            st.write(f"**Gender:** {customer.loc[0,'gender']}")
            st.write(f"**Senior Citizen:** {senior}")
            st.write(f"**Partner:** {customer.loc[0,'Partner']}")
            st.write(f"**Dependents:** {customer.loc[0,'Dependents']}")

            if tenure == 1:
                st.write("**Tenure:** 1 month")
            else:
                st.write(f"**Tenure:** {tenure} months")

        with col2:

            st.write(f"**Contract:** {customer.loc[0,'Contract']}")
            st.write(f"**Internet Service:** {customer.loc[0,'InternetService']}")
            st.write(f"**Monthly Charges:** ₹{customer.loc[0,'MonthlyCharges']:.2f}")
            st.write(f"**Payment Method:** {customer.loc[0,'PaymentMethod']}")
            st.write(f"**Phone Service:** {customer.loc[0,'PhoneService']}")

        st.divider()

        # -----------------------------------
        # Prediction
        # -----------------------------------

        if st.button("Predict Churn", use_container_width=True):

            probability = float(model.predict_proba(processed_customer)[0][1])

            st.subheader("📈 Prediction Result")

            st.metric(
                "Churn Probability",
                f"{probability*100:.2f}%"
            )

            st.progress(probability)

            # ----------------------------
            # Risk Levels
            # ----------------------------

            if probability < 0.30:

                st.success("🟢 Low Risk of Churn")

                st.info("""
### Recommended Business Action

- Continue regular customer engagement.
- Maintain current service quality.
- Promote premium services where appropriate.
""")

            elif probability < 0.70:

                st.warning("🟡 Medium Risk of Churn")

                st.info("""
### Recommended Business Action

- Offer personalized discounts.
- Check recent customer satisfaction.
- Encourage migration to long-term contracts.
""")

            else:

                st.error("🔴 High Risk of Churn")

                st.info("""
### Recommended Business Action

- Launch an immediate retention campaign.
- Offer contract renewal incentives.
- Contact the customer proactively.
- Assign a customer success representative.
""")

            # ----------------------------
            # Testing Only
            # ----------------------------

            # with st.expander("Model Validation"):

            #     st.write(
            #         f"**Actual Churn:** {customer.loc[0,'Churn']}"
            #     )