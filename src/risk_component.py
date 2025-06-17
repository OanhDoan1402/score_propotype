# src/risk_component.py
from dash import Input, Output, html
import plotly.graph_objects as go
from dash import dash_table
import pandas as pd
from src.data_loader import score_df, risk_indicator_df
from src.risk_scale_utils import INDICATOR_COLORS

def register_callbacks(app):

    def get_latest_month_record(df, year):
        subset = df[df["YearReport"] == year]
        if "MonthReport" in subset.columns:
            max_month = subset["MonthReport"].max()
            return subset[subset["MonthReport"] == max_month]
        return subset

    @app.callback(
        Output("from-compare", "options"),
        Output("from-compare", "value"),
        Output("to-compare", "options"),
        Output("to-compare", "value"),
        Input("taxcode-input", "value")
    )
    def update_compare_dropdown(taxcode):
        if not taxcode or taxcode not in score_df['TaxCode'].astype(str).values:
            return [], None, [], None
        years = sorted(score_df[score_df['TaxCode'].astype(str) == taxcode]['YearReport'].unique())
        options = [{"label": str(y), "value": y} for y in years]
        return options, None, options, None

    @app.callback(
        Output("score-breakdown", "figure"),
        Output("relative-contributions", "figure"),
        Output("financial-risk-table", "children"),
        Output("non-financial-risk-table", "children"),
        Input("taxcode-input", "value"),
        Input("compare-toggle", "value"),
        Input("from-compare", "value"),
        Input("to-compare", "value")
    )
    def update_risk_component(taxcode, compare_toggle, from_compare, to_compare):
        if not taxcode:
            return go.Figure(), go.Figure(), [], []

        data = score_df[score_df["TaxCode"].astype(str) == taxcode]
        risk_data = risk_indicator_df[risk_indicator_df["TaxCode"].astype(str) == taxcode]

        if data.empty or risk_data.empty:
            return go.Figure(), go.Figure(), [], []

        latest = data.sort_values("YearReport").iloc[-1]
        latest_year = int(latest["YearReport"])
        risk_latest_year = risk_data[risk_data["YearReport"] == latest_year]

        # ✅ Lọc theo tháng nếu có
        if "MonthReport" in risk_latest_year.columns:
            max_month = risk_latest_year["MonthReport"].max()
            risk_latest = risk_latest_year[risk_latest_year["MonthReport"] == max_month]
        else:
            risk_latest = risk_latest_year

        # ==== Pie Chart
        pie_labels = [
            f"FinancialRisk ({latest['FinancialRisk']}%)",
            f"IndustryRisk ({latest['IndustryRisk']}%)",
            f"OrganizationRisk ({latest['OrganizationRisk']}%)"
        ]
        pie_values = [
            latest["FinancialRisk"],
            latest["IndustryRisk"],
            latest["OrganizationRisk"]
        ]
        labels = ["FinancialRisk", "IndustryRisk", "OrganizationRisk"]
        pie_colors = [INDICATOR_COLORS.get(label, "#ddd") for label in labels]




        if compare_toggle and "on" in compare_toggle and from_compare and to_compare:
            from plotly.subplots import make_subplots
            base_data = data[data["YearReport"] == from_compare].iloc[-1]
            compare_data = data[data["YearReport"] == to_compare].iloc[-1]
            pie_fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
            
            pie_fig.add_trace(go.Pie(
                values=[base_data["FinancialRisk"], base_data["IndustryRisk"], base_data["OrganizationRisk"]],
                labels=labels,
                # marker=dict(colors=pie_colors),
                marker=dict(colors=[INDICATOR_COLORS.get(l, "#ddd") for l in labels]),
                hole=0.5,
                textinfo='percent',
                sort=False,
                domain=dict(x=[0, 0.48], y=[0, 1])
            ), row=1, col=1)

            pie_fig.add_trace(go.Pie(
                values=[compare_data["FinancialRisk"], compare_data["IndustryRisk"], compare_data["OrganizationRisk"]],
                labels=labels,
                # marker=dict(colors=pie_colors),
                marker=dict(colors=[INDICATOR_COLORS.get(l, "#ddd") for l in labels]),
                hole=0.5,
                textinfo='percent',
                sort=False,
                domain=dict(x=[0.52, 1], y=[0, 1])
            ), row=1, col=2)

            pie_fig.update_layout(
                annotations=[
                    dict(text=f"Base Year {from_compare}", x=0.22, y=1.02, font_size=12, showarrow=True, xanchor='center'),
                    dict(text=f"Comparison Year {to_compare}", x=0.78, y=1.02, font_size=12, showarrow=True, xanchor='center')
                ],
                showlegend=True,
                margin=dict(t=50, b=20, l=15, r=15),
                height=390  ,
                plot_bgcolor="white",uniformtext_minsize=10, uniformtext_mode='hide',
                legend=dict(
                    orientation="h",
                    x=0.5,
                    y=-0.5,
                    xanchor="center",
                    yanchor="bottom",
                    font=dict(size=10),
                    itemwidth=90    
                )
            )
        else:
            pie_fig = go.Figure(
                data=[go.Pie(
                labels=labels, values=pie_values,
                # marker=dict(colors=["#70ad47", "#5b9bd5", "#ffc000"]),
                marker=dict(colors=[INDICATOR_COLORS.get(l, "#ddd") for l in labels]),
                hole=0.4
            )
                ],
                layout=go.Layout(height=340, uniformtext_minsize=14, uniformtext_mode='hide',
                                margin=dict(t=10, b=10, l=5, r=5), plot_bgcolor="white",
                                legend=dict(orientation="h", x=0.5, y=-0.3, xanchor="center", yanchor="bottom", font=dict(size=10), itemwidth=90)
                                )
            )


        # ==== Bar chart (relative contribution)
        indicators = [
            #Financial
            "Growth Ratios", 
            "Profitability Ratios", 
            "Efficiency Ratios",
            "Liquidity Ratios", 
            "Leverage Ratios", 
            "Cash Flow Ratios",
            "Size Ratios", 

            # Organ
            "Business Activity History", 
            "Company Size", 
            "Statutory Compliance Risk",
            "News Sentiment Risk",
            "Import Volume Trend",
            "Export Volume Trend",

            # Industry
            "Import Volume Trend in Industry", 
            "Export Volume Trend in Industry", 
            "Distress Businesses",
            "Active Business in Industry",
            "New Business Registrations",
        ]
        rel_data = risk_latest[risk_latest["Indicator"].isin(indicators)]

        # Tạo từng trace riêng biệt cho từng Indicator
        bar_fig = go.Figure()


        # Lấy Median_sum từ risk_indicator_df theo taxcode
        median_row = risk_indicator_df[risk_indicator_df["TaxCode"].astype(str).str.strip() == str(taxcode).strip()]
        if not median_row.empty:
            median_value = median_row.iloc[0]["Median_sum"]
            try:
                median_value = float(str(median_value).replace('%', '').replace(',', '').strip())
            except (ValueError, TypeError):
                median_value = None

            if median_value is not None:
                bar_fig.add_annotation(
                    text=f"<b>Median Score = {int(round(median_value))}</b>",
                    xref="paper", yref="paper",
                    x=0.5, y=1.1,                 # ✅ tăng từ 1.02 lên 1.15 để đẩy cao hơn
                    showarrow=False,
                    font=dict(
                        size=10,
                        color="red"
                    ),
                    align="center"
                )

        for _, row in rel_data.iterrows():
            
            bar_fig.add_trace(go.Bar(
                x=[row["Indicator"]],
                y=[row["Relative"]],
                name=row["Indicator"],
                marker_color=INDICATOR_COLORS.get(row["Indicator"], "#888"),
                text=[f"{row['Relative']:.2f}%"],  # ✅ hiển thị 2 chữ số thập phân
                textposition="outside",
                textfont=dict(size=10),
                hoverinfo="x+y",
                showlegend=True,
            ))

            bar_fig.update_layout(
                height=400,
                xaxis=dict(
                    showticklabels=False,
                    tickangle=-30,
                    tickfont=dict(size=10),
                    showgrid=False
                ),
                yaxis=dict(
                    # title="Relative (%)",
                    tickfont=dict(size=12),
                    zeroline=True,
                    zerolinecolor="#999",
                    showgrid=True,
                    gridcolor="#e0e0e0"
                ),
                bargap=0.25,
                plot_bgcolor="white",
                margin=dict(t=60, b=40, l=60, r=40),  # 👈 Tăng bottom margin
                legend=dict(
                    orientation="h",
                    x=0.5,
                    xanchor="center",
                    y=-0.6,           # 👈 Đặt xa hơn khỏi biểu đồ
                    yanchor="bottom",
                    font=dict(size=10),
                    itemwidth=100,
                    bgcolor="rgba(0,0,0,0)"
                ),
                uniformtext_minsize=8,
                uniformtext_mode='show'
            )


        # ==== Tables

        def build_table(df):
            if "Period" in df.columns:
                # Tách Base và Compare
                base_df = df[df["Period"].str.contains("Base")].copy()
                compare_df = df[df["Period"].str.contains("Compare")].copy()

                # Merge để tính chênh lệch
                merged = compare_df.merge(
                    base_df,
                    on="Indicator",
                    suffixes=("_compare", "_base")
                )

                # Tính chênh lệch và format
                for col in ["Score", "Contributions", "Median", "Relative"]:
                    merged[f"{col}_diff"] = merged[f"{col}_compare"] - merged[f"{col}_base"]
                    merged[col] = merged[f"{col}_compare"].round(2).astype(str) + " (" + merged[f"{col}_diff"].apply(
                        lambda x: f"+{x:.2f}" if x > 0 else f"{x:.2f}"
                    ) + ")"

                # Chuẩn bị 2 bảng để ghép
                base_final = base_df[["Indicator", "Score", "Contributions", "Median", "Relative"]].copy()
                compare_final = merged[["Indicator", "Score", "Contributions", "Median", "Relative"]].copy()

                # Format phần trăm
                base_final["Score"] = base_final["Score"].apply(lambda x: f"{round(x):,}" if pd.notna(x) else "N/A")
                base_final["Contributions"] = base_final["Contributions"].apply(lambda x: f"{x:.2f}%")
                base_final["Median"] = base_final["Median"].apply(lambda x: f"{round(x):,}" if pd.notna(x) else "N/A")
                base_final["Relative"] = base_final["Relative"].apply(lambda x: f"{x:.4f}%")

                # compare_final["Score"] = compare_final["Score"].apply(lambda x: f"{round(x):,}" if pd.notna(x) else "N/A")
                compare_final["Contributions"] = compare_final["Contributions"].astype(str).str.replace(")", "%)")
                # compare_final["Median"] = compare_final["Median"].apply(lambda x: f"{round(x):,}" if pd.notna(x) else "N/A")
                compare_final["Relative"] = compare_final["Relative"].astype(str).str.replace(")", "%)")

                # Gắn nhãn dòng
                base_final["TypeRow"] = "Base"
                compare_final["TypeRow"] = "Compare"

                # Gộp 2 bảng
                final = pd.concat([base_final, compare_final], ignore_index=True)
                final = final.sort_values(by=["Indicator", "TypeRow"]).drop(columns=["TypeRow"]).reset_index(drop=True)
                final.loc[final.index % 2 == 1, "Indicator"] = ""

                # Tạo style: tô màu xanh/đỏ cho phần chênh lệch
                styles = []
                for i, row in final.iterrows():
                    if row["Indicator"] == "":
                        for col in ["Score", "Contributions", "Median", "Relative"]:
                            value = str(row[col])
                            if "(" in value and ")" in value:
                                try:
                                    diff = float(value.split("(")[-1].replace(")", "").replace("%", "").replace("+", ""))
                                    styles.append({
                                        "if": {"row_index": i, "column_id": col},
                                        "color": "green" if diff > 0 else "red" if diff < 0 else "black",
                                        "fontStyle": "italic",
                                        "fontSize": "12px"
                                    })
                                except ValueError:
                                    pass
            else:
                # Trường hợp không compare
                final = df[["Indicator", "Score", "Contributions", "Median", "Relative"]].copy()
                final["Score"] = final["Score"].apply(lambda x: f"{round(x):,}" if pd.notna(x) else "N/A")
                final["Contributions"] = final["Contributions"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
                final["Median"] = final["Median"].apply(lambda x: f"{round(x):,}" if pd.notna(x) else "N/A")
                final["Relative"] = final["Relative"].apply(lambda x: f"{x:.4f}%" if pd.notna(x) else "N/A")
                styles = []

            return html.Div([
                dash_table.DataTable(
                    columns=[
                        {"name": "Indicator", "id": "Indicator"},
                        {"name": "Score", "id": "Score"},
                        {"name": "Contributions", "id": "Contributions"},
                        {"name": "Median", "id": "Median"},
                        {"name": "Relative", "id": "Relative"}
                    ],
                    data=final.to_dict("records"),
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "padding": "6px",
                        "textAlign": "center",
                        "border": "1px solid #ccc",
                        "fontSize": "14px",
                        "fontFamily": "Arial, sans-serif"
                    },
                    style_header={
                        "backgroundColor": "#f5f5f5",
                        "fontWeight": "bold",
                        "textAlign": "center"
                    },
                    style_data_conditional=styles + [
                        {"if": {"column_id": "Indicator"}, "textAlign": "left"}
                    ]
                )
            ])

        # ===========================

        financial_names = [
            #Financial
            "Growth Ratios", 
            "Profitability Ratios", 
            "Efficiency Ratios",
            "Liquidity Ratios", 
            "Leverage Ratios", 
            "Cash Flow Ratios",
            "Size Ratios", 
        ]

        non_financial_names = [
            # Organ
            "Business Activity History", 
            "Company Size", 
            "Statutory Compliance Risk",
            "News Sentiment Risk",
            "Import Volume Trend",
            "Export Volume Trend",

            # Industry
            "Import Volume Trend in Industry", 
            "Export Volume Trend in Industry", 
            "Distress Businesses",
            "Active Business in Industry",
            "New Business Registrations",
        ]

        if compare_toggle and "on" in compare_toggle and from_compare and to_compare:
            # ✅ Lấy bản ghi mới nhất theo MonthReport cho mỗi kỳ
            base_risk = get_latest_month_record(risk_data, from_compare).copy()
            compare_risk = get_latest_month_record(risk_data, to_compare).copy()

            base_risk["Period"] = f"Base {from_compare}"
            compare_risk["Period"] = f"Compare {to_compare}"

            financial_base = base_risk[base_risk["Indicator"].isin(financial_names)]
            financial_compare = compare_risk[compare_risk["Indicator"].isin(financial_names)]
            financial_df = pd.concat([financial_base, financial_compare])

            non_financial_base = base_risk[base_risk["Indicator"].isin(non_financial_names)]
            non_financial_compare = compare_risk[compare_risk["Indicator"].isin(non_financial_names)]
            non_financial_df = pd.concat([non_financial_base, non_financial_compare])
        else:
            financial_df = risk_latest[risk_latest["Indicator"].isin(financial_names)].copy()
            non_financial_df = risk_latest[risk_latest["Indicator"].isin(non_financial_names)].copy()

        financial_df = financial_df.sort_values(["Indicator", "Period"]) if "Period" in financial_df.columns else financial_df.sort_values(["Indicator"])
        non_financial_df = non_financial_df.sort_values(["Indicator", "Period"]) if "Period" in non_financial_df.columns else non_financial_df.sort_values(["Indicator"])

        return pie_fig, bar_fig, build_table(financial_df), build_table(non_financial_df)


    @app.callback(
        Output("non-financial-risk-title", "style"),
        Input("compare-toggle", "value")
    )
    def update_non_financial_margin(compare_toggle):
        if compare_toggle and "on" in compare_toggle:
            # Khi có compare → marginTop nhỏ
            return {"fontWeight": "bold", "marginTop": "15px", "marginRight": "15px", "marginBottom": "8px", "fontSize": "18px"}
        else:
            # Khi không compare → giữ khoảng cách như hiện tại
            return {"fontWeight": "bold", "marginTop": "190px", "marginRight": "15px", "marginBottom": "8px", "fontSize": "20px"}

