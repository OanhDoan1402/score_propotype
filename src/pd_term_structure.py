from dash import html, Output, Input
from src.data_loader import term_df
from dash import Input, Output
import pandas as pd
from src.data_loader import score_df, term_df

# === TERM COLUMNS
term_cols = [col for col in term_df.columns if col.startswith("PD_")]
term_df.columns = term_df.columns.str.strip()

def register_callbacks(app):
    @app.callback(
        Output("monthly-pd-table", "data"),
        Output("yearly-pd-table-1", "data"),
        Output("yearly-pd-table-2", "data"),
        Output("yearly-pd-table-3", "data"),
        Input("taxcode-input", "value")
    )
    def update_pd_term_structure(taxcode):
        if not taxcode:
            return [{}], [{}], [{}], [{}]

        # 1. Lấy thông tin công ty mới nhất
        company_data = score_df[score_df['TaxCode'].astype(str) == str(taxcode).strip()]
        if company_data.empty:
            return [{}], [{}], [{}], [{}]

        latest = company_data.sort_values("YearReport").iloc[-1]
        pd_val_str = str(latest["PD"]).replace('%', '').strip()
        try:
            pd_latest = float(pd_val_str) / 100
        except ValueError:
            pd_latest = 0.0

        grade = str(latest["Grade"]).strip()

        # 2. Lấy dòng term ứng với grade
        row = term_df[term_df["Grade"].astype(str).str.strip() == grade]

        if row.empty:
            return [{}], [{}], [{}], [{}]
        row = row.iloc[0]

        pd_1y = row.get("PD_1Y", None)
        if pd.isna(pd_1y) or pd_1y == 0:
            return [{}], [{}], [{}], [{}]

        # 3. Monthly Term: PD_1M → PD_12M
        monthly = {}
        for i in range(1, 13):
            col = f"PD_{i}M"
            val = row.get(col, None)
            if pd.notna(val):
                factor = val / pd_1y
                monthly[f"m{i}"] = f"{pd_latest * factor:.4%}"
            else:
                monthly[f"m{i}"] = "N/A"

        # 4. Yearly Term: PD_1Y → PD_35Y
        yearly_raw = []
        for i in range(1, 36):
            col = f"PD_{i}Y"
            val = row.get(col, None)
            if pd.notna(val):
                factor = val / pd_1y
                yearly_raw.append(f"{pd_latest * factor:.4%}")
            else:
                yearly_raw.append("N/A")

        yearly_1 = {f"y{i+1}": yearly_raw[i] for i in range(12)}       # y1 → y12
        yearly_2 = {f"y{i+13}": yearly_raw[i+12] for i in range(12)}   # y13 → y24
        yearly_3 = {f"y{i+25}": yearly_raw[i+24] for i in range(11)}   # y25 → y35

        return [monthly], [yearly_1], [yearly_2], [yearly_3]
