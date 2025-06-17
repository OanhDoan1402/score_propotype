# src/score_trend.py
from dash import Input, Output
import plotly.graph_objects as go
from src.data_loader import score_df, risk_indicator_df
from src.risk_scale_utils import INDICATOR_COLORS

def register_callbacks(app):
    @app.callback(
        Output('score-trend', 'figure'),
        Output('from-year-dropdown', 'options'),
        Output('from-year-dropdown', 'value'),
        Output('to-year-dropdown', 'options'),
        Output('to-year-dropdown', 'value'),
        Input('taxcode-input', 'value'),
        Input('from-year-dropdown', 'value'),
        Input('to-year-dropdown', 'value')
    )
    def update_score_trend(taxcode, from_year, to_year):
        if not taxcode or taxcode not in score_df['TaxCode'].astype(str).values:
            return go.Figure(), [], None, [], None

        # filtered_df = score_df[score_df['TaxCode'].astype(str) == taxcode].sort_values("YearReport")

        df = score_df[score_df['TaxCode'].astype(str) == taxcode].copy()
        df["YearReport"] = df["YearReport"].astype(int)
        df["MonthReport"] = df.get("MonthReport", 0).fillna(0).astype(int)
        df["PD"] = df["PD"].astype(str).str.replace('%', '', regex=False).astype(float)


        # ⚙️ Lấy năm mới nhất theo logic bạn muốn
        latest_year = df["YearReport"].max()
        has_month_col = "MonthReport" in df.columns

        # ✅ Nếu có MonthReport → chỉ giữ bản ghi có MonthReport max trong năm đó
        if has_month_col:
            latest_month = df[df["YearReport"] == latest_year]["MonthReport"].max()
            df = df[~((df["YearReport"] == latest_year) & (df["MonthReport"] != latest_month))]

        # Sau đó tiếp tục lọc theo khoảng from-to
        filtered_df = df[(df["YearReport"] >= from_year) & (df["YearReport"] <= to_year)]

        available_years = sorted(df["YearReport"].unique())
        if not available_years:
            return go.Figure(), [], None, [], None

        from_year = int(from_year) if from_year is not None else available_years[0]
        to_year = int(to_year) if to_year is not None else available_years[-1]


        filtered_df = filtered_df[(filtered_df["YearReport"] >= from_year) & (filtered_df["YearReport"] <= to_year)]
        filtered_df["YearReport"] = filtered_df["YearReport"].astype(int)

        segment_df = risk_indicator_df[risk_indicator_df["TaxCode"].astype(str) == taxcode]
        segment_per_year = (
            segment_df.groupby("YearReport")["Median_sum"]
            .first()
            .reset_index()
            .sort_values("YearReport")
        )
        segment_per_year = segment_per_year[
            (segment_per_year["YearReport"] >= from_year) &
            (segment_per_year["YearReport"] <= to_year)
        ]

        fig = go.Figure()

        # Shadow line
        fig.add_trace(go.Scatter(
            x=filtered_df["YearReport"],
            y=filtered_df["Score"],
            mode="lines",
            line=dict(color='rgba(0, 0, 0, 0.1)', width=6),
            hoverinfo='skip',
            showlegend=False
        ))

        # Line score
        fig.add_trace(go.Scatter(
            x=filtered_df["YearReport"],
            y=filtered_df["Score"],
            mode="lines+markers",
            name="Score Company",
            line=dict(color=INDICATOR_COLORS["Score Company"], width=4),
            hoverinfo="x+y"
        ))

        # Bar PD
        fig.add_trace(go.Bar(
            x=filtered_df["YearReport"],
            y=filtered_df["PD"],
            name="Probability of Default (%)",
            yaxis="y2",
            marker_color=INDICATOR_COLORS["Probability of Default (%)"],
            opacity=1,
            hoverinfo="x+y",
            width=0.4,
            marker=dict(  color="#5B9BD5",
                        line=dict(width=3, color="rgba(0,0,0,0.1)") ),
        ))

        # Median line
        fig.add_trace(go.Scatter(
            x=segment_per_year["YearReport"],
            y=segment_per_year["Median_sum"],
            mode="lines+markers",
            name="Score Model Segment",
            line=dict(color=INDICATOR_COLORS["Score Model Segment"], width=3, dash="dash"),
            marker=dict(size=6, symbol="triangle-up"),
            hoverinfo="x+y",
            opacity=0.8
        ))

        # Vùng màu risk
        risk_zones = [
            (903, 1000, "#00b050"), 
            (700, 903, "#00CC00"), 
            (599, 700, "#92D050"),
            (510, 599, "#FFE699"), 
            (428, 510, "#FFC000"), 
            (326, 428, "#ED7D31"),
            (257, 326, "#FF0000"), 
            (0, 257, "#C00000")
        ]
        for year in filtered_df["YearReport"].unique():
            # Tạo dải màu risk scale bên trái như ảnh 1
            for lower, upper, color in risk_zones:
                fig.add_shape(
                    type="rect",
                    xref="paper",     # dùng theo phần trăm chiều rộng biểu đồ
                    yref="y",
                    x0=0.0,           # bên trái biểu đồ
                    x1=0.02,          # chiếm khoảng 3% chiều ngang
                    y0=lower,
                    y1=upper,
                    fillcolor=color,
                    opacity=0.5,
                    line_width=0,
                    layer="below")
            

        fig.update_layout(
            height=420,
            margin=dict(t=40, b=110, l=40, r=40),
            xaxis=dict(title="Year", 
                       showgrid=False,
                    #    domain=[0.05, 1],
                       ),
            yaxis=dict(title="Score", range=[0, 1000], dtick=100, showgrid=True, gridcolor="#e0e0e0"),
            yaxis2=dict(
                title="PD (%)",
                overlaying="y",
                side="right",
                range=[0, 20],
                dtick=2,
                showgrid=False,
                rangemode="tozero"
            ),
            legend=dict(
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.3,
                yanchor="bottom",
                font=dict(size=13),
                itemwidth=50,
                bgcolor='rgba(0,0,0,0)'
            ),
            plot_bgcolor="white"
        )

        return (
            fig,
            [{"label": str(y), "value": y} for y in available_years],
            from_year,
            [{"label": str(y), "value": y} for y in available_years],
            to_year
        )
