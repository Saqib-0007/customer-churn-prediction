from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:NewPassword123@localhost/customer_churn_db"
)