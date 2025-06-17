# src/data_loader.py
import pandas as pd
import os

# Tự động chuyển .xlsx sang .csv nếu chưa có
def convert_xlsx_to_csv():
    files = [
        ("data/profile.xlsx", "data/profile.csv"),
        ("data/score_data.xlsx", "data/score_data.csv"),
        ("data/distribution.xlsx", "data/distribution.csv"),
        ("data/Risk_Indicators.xlsx", "data/Risk_Indicators.csv"),
        ("data/term.xlsx", "data/term.csv")
    ]

    for xlsx_path, csv_path in files:
        if os.path.exists(xlsx_path) and not os.path.exists(csv_path):
            df = pd.read_excel(xlsx_path)
            df.to_csv(csv_path, index=False)

# Chạy chuyển đổi khi import
convert_xlsx_to_csv()

# Load profile data
def load_profile_data():
    return pd.read_csv("data/profile.csv")

# Load score data
def load_score_data():
    df = pd.read_csv("data/score_data.csv")
    df.columns = df.columns.str.strip().str.replace(" ", "").str.replace("(", "").str.replace(")", "")
    return df

# Load distribution data
def load_distribution_data():
    return pd.read_csv("data/distribution.csv")

# Load risk indicator data
def load_risk_indicator_data():
    return pd.read_csv("data/Risk_Indicators.csv")

# Load PD term structure data
def load_term_data():
    df = pd.read_csv("data/term.csv")
    df.columns = df.columns.str.strip()
    return df

# Global variables to use in other modules
profile_df = load_profile_data()
score_df = load_score_data()
distribution_df = load_distribution_data()
risk_indicator_df = load_risk_indicator_data()
term_df = load_term_data()