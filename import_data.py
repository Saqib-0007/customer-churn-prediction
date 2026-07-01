import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:NewPassword123@localhost/customer_churn_db"
)

# Import original dataset
df = pd.read_csv("data/customer_churn.csv")

df.to_sql(
    "customers",
    engine,
    if_exists="replace",
    index=False
)

# Import processed dataset
processed_df = pd.read_csv("data/customer_churn_processed.csv")

processed_df.to_sql(
    "processed_customers",
    engine,
    if_exists="replace",
    index=False
)

print("Both tables imported successfully!")