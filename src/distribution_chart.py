from dash import html, Input, Output
import plotly.graph_objects as go
import pandas as pd
from src.data_loader import score_df, profile_df, distribution_df

def register_callbacks(app):
    @app.callback(
        Output("distribution-chart", "figure"),
        Output("distribution-info", "children"),
        Input("taxcode-input", "value"),
        Input("distribution-mode", "value")  # 👈 thêm input mới
    )
    def update_distribution_chart(taxcode, mode):
        if not taxcode:
            return go.Figure(), html.Div()

        return plot_distribution_chart(taxcode)

        
def plot_distribution_chart(taxcode):
    taxcode = str(taxcode).strip()

    # 1. Lấy segment từ profile
    profile_row = profile_df[profile_df["TaxCode"].astype(str).str.strip() == taxcode]
    if profile_row.empty:
        return go.Figure(), html.Div("")

    profile_row = profile_row.iloc[0]
    model_segment = str(profile_row["ModelSegment"]).strip()
    # print("→ Using ModelSegment:", model_segment)


    # 2. Lọc phân phối từ distribution_df
    dist_filtered = distribution_df[distribution_df["Segment"].astype(str).str.strip() == model_segment]
    # print("→ Matching rows in distribution_df:", len(dist_filtered))
    if dist_filtered.empty:
        return go.Figure(), html.Div("No distribution data found.")

    # 3. Lấy FG hiện tại từ điểm gần nhất trong score_df
    scores = score_df[score_df["TaxCode"].astype(str).str.strip() == taxcode]
    if scores.empty:
        current_grade = None
    else:
        if "MonthReport" in scores.columns:
            latest_score = scores.sort_values(["YearReport", "MonthReport"]).iloc[-1]
        else:
            latest_score = scores.sort_values("YearReport").iloc[-1]

        current_grade = str(latest_score.get("Grade", "")).strip()

    # 4. Tổng hợp count theo từng FG
    fg_order = [f"FG-{i}" for i in range(1, 18)]
    fg_counts = {fg: 0 for fg in fg_order}
    grouped = dist_filtered.groupby("FG")["count"].sum().to_dict()
    fg_counts.update(grouped)

    x_labels = fg_order
    y_values = [fg_counts[fg] for fg in fg_order]
    bar_colors = ["#0752ad" if fg != current_grade else "#FFC000" for fg in fg_order]

    # 5. Vẽ biểu đồ
    fig = go.Figure(data=[
        go.Bar(x=x_labels, y=y_values, marker_color=bar_colors)
    ])

    fig.update_layout(
        xaxis_title="Score Grade (FG)",
        yaxis_title="Total Count",
        template="simple_white",
        height=350,
        margin=dict(t=10, b=40, l=40, r=10)
    )

    # 6. Hiển thị mô tả thông tin
    info = html.Div([
        html.P(["Industry: ", html.B(str(profile_row.get("en_VSICName (LV3)", "")).strip())]),
        html.P(["Model Segment: ", html.B(model_segment.replace("_", " - "))]),
        html.P(["Current Grade: ", html.B(current_grade or "N/A")])
    ])

    return fig, info
