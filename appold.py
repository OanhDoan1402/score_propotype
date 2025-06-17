import pandas as pd
import dash
from dash import dcc, html, Input, Output
from dash import dash_table
from dash import Input, Output
import dash_daq as daq          
import dash_auth
import plotly.graph_objs as go
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Khởi tạo app
app = dash.Dash(__name__)
server = app.server  # nếu bạn đang deploy trên Render

# Định nghĩa tài khoản và mật khẩu
VALID_USERNAME_PASSWORD = {
    'admin': 'admin',
    'team': 'score123'
}
# print(VALID_USERNAME_PASSWORD)


# Kích hoạt login
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD
)

app.layout = html.Div([
    html.H1("Welcome to the secured dashboard"),
    html.Div("You are logged in!")
])


app.title = "FiinGate Credit Score Viewer"

# Load dữ liệu
profile_df = pd.read_csv('data_final/profile.csv')
score_df = pd.read_csv('data_final/score_data.csv')
score_df.columns = score_df.columns.str.strip()  # ← Xóa khoảng trắng thừa
score_df.columns = score_df.columns.str.replace(" ", "").str.replace("(", "").str.replace(")", "")
distribution_df = pd.read_csv('data_final/distribution.csv')
risk_indicator_df = pd.read_csv("data_final/Risk_Indicators.csv")

from layout import get_layout
app.layout = get_layout()

###################################################### CREATE TEMPLATE COLOR CHART


INDICATOR_COLORS = {
    "Cash Flow Ratios": "#4f81bd",
    "Efficiency (Activity) Ratios": "#b8cf89",
    "Growth Ratios": "#79c1d5",
    "Leverage (Solvency) Ratios": "#536e8f",
    "Liquidity Ratios": "#7b8d54",
    "Profitability Ratios": "#5a8d9b",
    "Size Ratios": "#8aacd3",
    "Growth Stability": "#95cedd",
    "Tax Compliance Risk": "#6a8cb4",
    "Industry Health Status": "#96af63",
    "Industry Trade Activity": "#bacee5",
    "Industry New Business Dynamics": "#5ca4b7",
    "Scale": "#bed393",
    "Financial": "#4f81bd",
    "Industry Non-Financial": "#9bbb59",
    "Corporate Non-Financial": "#4bacc6",
    "Score Model Segment": "#abe5f5",
    "Score Company": "#0752ad",
    "Probability of Default (%)": "#9bbb59"
}





###################################################### CALL OUT PROFLE AND SCORE CARD
@app.callback(
    Output('company-info', 'children'),
    Output('score-summary', 'children'),
    Input('taxcode-input', 'value')
)
def update_output(taxcode):
    if not taxcode or taxcode not in profile_df['TaxCode'].astype(str).values:
        return html.Div("No matching company found.", style={"textAlign": "center"}), html.Div()

    profile = profile_df[profile_df['TaxCode'].astype(str) == taxcode].iloc[0]

    # Lấy Score, PD, Grade từ score_df của năm mới nhất
    scores = score_df[score_df["TaxCode"].astype(str).str.strip() == str(taxcode).strip()]
    if scores.empty:
        latest_score = None
        latest_pd = None
        risk_grade = None
    else:
        latest = scores.sort_values("YearReport").iloc[-1]
        latest_score = int(latest["Score"])
        latest_pd = latest["PD"]
        risk_grade = str(latest["Grade"]).strip()
        previous = scores.iloc[-2] if len(scores) >= 2 else None
        prev_score = int(previous["Score"]) if previous is not None else None
        delta = latest_score - prev_score if previous is not None else None   

    # Tạo mapping Grade → risk_label
    risk_scale = [
        (0.36, "FG-1", "Negligible risk"),
        (0.50, "FG-2", "Very low risk"),
        (0.70, "FG-3", "Very low risk"),
        (0.98, "FG-4", "Very low risk"),
        (1.36, "FG-5", "Low risk"),
        (1.90, "FG-6", "Low risk"),
        (2.64, "FG-7", "Low risk"),
        (3.68, "FG-8", "Moderate risk"),
        (5.13, "FG-9", "Moderate risk"),
        (7.15, "FG-10", "Moderate risk"),
        (9.96, "FG-11", "High risk"),
        (13.87, "FG-12", "High risk"),
        (19.32, "FG-13", "Very high risk"),
        (26.91, "FG-14", "Very high risk"),
        (37.48, "FG-15", "Very high risk"),
        (52.20, "FG-16", "Near default"),
        (72.71, "FG-17", "Near default"),
        (100.0, "FG-18", "Defaulted")
    ]
    grade_to_label = {grade: label for _, grade, label in risk_scale}
    risk_label = grade_to_label.get(risk_grade, "Unknown") if risk_grade else "Unknown"

    # Mapping màu theo grade
    grade_color_map = {
        "FG-1": "#00B050",
        "FG-2": "#00CC00", "FG-3": "#00CC00", "FG-4": "#00CC00",
        "FG-5": "#92D050", "FG-6": "#92D050", "FG-7": "#92D050",
        "FG-8": "#FFE699", "FG-9": "#FFE699", "FG-10": "#FFE699",
        "FG-11": "#FFC000", "FG-12": "#FFC000", "FG-13": "#FFC000",
        "FG-14": "#ED7D31", "FG-15": "#ED7D31",
        "FG-16": "#FF0000", "FG-17": "#FF0000",
        "FG-18": "#C00000"
    }
    grade_color = grade_color_map.get(risk_grade, "#ffc000")

    # Thông tin công ty
    company_info = html.Div([
        html.H3(profile['OrganizationName'], style={"color": "#004a99", "marginBottom": "10px", "textTransform": "uppercase"}),
        html.Div([html.Span("Tax Code: ", style={"fontWeight": "bold"}), html.Span(profile['TaxCode'])]),
        html.Div([html.Span("Operating Status: ", style={"fontWeight": "bold"}), html.Span(profile['en_ActiveStatusName'])]),
        html.Div([html.Span("Ticker: ", style={"fontWeight": "bold"}), html.Span(profile['Ticker'])]),
        html.Div([html.Span("En_Name: ", style={"fontWeight": "bold"}), html.Span(profile['en_OrganizationName'])]),
        html.Div([html.Span("Industry: ", style={"fontWeight": "bold"}), html.Span(profile['en_VSICName (LV3)'])]),
        html.Div([html.Span("Model Segment: ", style={"fontWeight": "bold"}), html.Span(f"{profile['Modelsegmentvsic']} - {profile['Modelsegmentsize']}")])
    ], style={"textAlign": "left", "lineHeight": "1.8", "margin": "auto", "width": "100%", "fontSize": "18px"})
    


    # Score Summary Section
    score_summary = html.Div([
        html.Div([
            html.Div("Total Score: (1-1000 scale)", style={
                "fontSize": "16px", "color": "#999", "textAlign": "center", "marginBottom": "8px"
            }),
            html.Div([
                html.Div(str(latest_score), style={
                    "fontSize": "40px", "fontWeight": "bold", "backgroundColor": grade_color,
                    "border": "0.5px solid white", "padding": "20px 20px", "borderRadius": "5px 0 0 5px",
                    "boxShadow": "2px 2px 5px rgba(0,0,0,0.2)", "width": "50%", "textAlign": "center"
                }),
                html.Div(risk_grade, style={
                    "fontSize": "36px", "fontWeight": "bold", "backgroundColor": grade_color,
                    "border": "0.5px solid white", "padding": "20px 20px", "borderRadius": "0 5px 5px 0",
                    "boxShadow": "2px 2px 5px rgba(0,0,0,0.2)", "width": "50%", "textAlign": "center"
                }),
            ], style={"display": "flex", "marginBottom": "15px"}),

            html.Div(risk_label, style={
                "textAlign": "center", "fontWeight": "bold", "fontSize": "26px", "marginBottom": "10px"
            }),

            html.Div([
                html.Div([
                    html.Div("Previous", style={"fontSize": "13px", "textAlign": "center", "marginBottom": "4px"}),
                    html.Div(str(prev_score) if prev_score is not None else "N/A", style={
                        "fontWeight": "bold", "textAlign": "center", "fontSize": "20px"
                    })
                ], style={"border": "1px solid #ccc", "borderRadius": "10px", "padding": "10px", "width": "90px",
                        "boxShadow": "2px 2px 4px rgba(0,0,0,0.1)"}),

                html.Div([
                    html.Div("Change", style={"fontSize": "13px", "textAlign": "center", "marginBottom": "4px"}),
                    html.Div(f"{delta:+}" if delta is not None else "N/A", style={
                        "fontWeight": "bold", "textAlign": "center",
                        "color": "red" if delta > 0 else "green", "fontSize": "20px"
                    })
                ], style={"border": "1px solid #ccc", "borderRadius": "10px", "padding": "10px", "width": "90px",
                        "boxShadow": "2px 2px 4px rgba(0,0,0,0.1)"}),

                html.Div([
                    html.Div("PD", style={"fontSize": "13px", "textAlign": "center", "marginBottom": "4px"}),
                    html.Div(f"{latest_pd:.2f}%", style={
                        "fontWeight": "bold", "textAlign": "center", "fontSize": "20px"
                    })
                ], style={"border": "1px solid #ccc", "borderRadius": "10px", "padding": "10px", "width": "90px",
                        "boxShadow": "2px 2px 4px rgba(0,0,0,0.1)"})
            ], style={"display": "flex", "gap": "15px", "marginBottom": "20px"}),

            html.Div([
                html.Div([
                    html.Span("● ", style={"color": "#aaa"}),
                    html.Span("Current score based on Financial Statement: "),
                    html.Span(str(latest["YearFS"]), style={"fontWeight": "bold", "fontSize": "19px"})
                ], style={"marginBottom": "5px"}),

                html.Div([
                    html.Span("● ", style={"color": "#aaa"}),
                    html.Span("Company size: "),
                    html.Span(str(profile["Modelsegmentvsic"]), style={"fontWeight": "bold", "fontSize": "19px"})
                ], style={"marginBottom": "5px"}),

                html.Div([
                    html.Span("● ", style={"color": "#aaa"}),
                    html.Span("Industry: "),
                    html.Span(str(profile["Modelsegmentsize"]), style={"fontWeight": "bold", "fontSize": "19px"})
                ], style={"marginBottom": "5px"}),

                html.Div([
                    html.Span("● ", style={"color": "#aaa"}),
                    html.Span("Model Segment: "),
                    html.Span(f"{profile['Modelsegmentsize']} - {profile['Modelsegmentvsic']}", style={
                        "fontWeight": "bold", "fontSize": "19px"})
                ], style={"marginBottom": "5px"}),
                                
            
                html.Div([
                    html.Span("● ", style={"color": "#aaa"}),
                    html.Span("Trade credit limit recommendation: "),
                    html.Span(str(profile["TotalTradeCreditLimit"]), style={"fontWeight": "bold", "fontSize": "19px"})
                ], style={"marginBottom": "5px"})
            ], style={"fontSize": "16px", "color": "#333", "paddingTop": "5px", "lineHeight": "1.6"})
        ])
    ], style={"display": "flex", "justifyContent": "flex-start", "marginTop": "30px"})

    return company_info, score_summary




###################################################### CALL OUT HISTORICAL CHANGE

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

    filtered_df = score_df[score_df['TaxCode'].astype(str) == taxcode].sort_values("YearReport")
    available_years = sorted(filtered_df["YearReport"].unique())
    
    # Ép kiểu an toàn
    from_year = int(from_year) if from_year is not None else available_years[0]
    to_year = int(to_year) if to_year is not None else available_years[-1]

    # Filter score theo năm
    filtered_df = filtered_df[(filtered_df["YearReport"] >= from_year) & (filtered_df["YearReport"] <= to_year)]
    filtered_df["YearReport"] = filtered_df["YearReport"].astype(int)
    
    # Lấy Median_sum từ Risk_Indicators.csv
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
    
     # === Vẽ biểu đồ ===
    fig = go.Figure()
    
    # Shadow line (nét to, mờ, nằm dưới)
    fig.add_trace(go.Scatter(
        x=filtered_df["YearReport"],
        y=filtered_df["Score"],
        mode="lines",
        line=dict(color='rgba(0, 0, 0, 0.15)', width=6),  # Bóng đổ
        hoverinfo='skip',
        showlegend=False
    ))
    
    # Line Score chính
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
    
    # Line Score Segment (Median_sum)
    fig.add_trace(go.Scatter(
        x=segment_per_year["YearReport"],
        y=segment_per_year["Median_sum"],
        mode="lines+markers",
        name="Score Model Segment",
        line=dict(color=INDICATOR_COLORS["Score Company"], width=3, dash="dash"),
        marker=dict(size=6, symbol="triangle-up"),
        hoverinfo="x+y",
        opacity=0.8,
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
        margin=dict(t=40, b=110, l=40, r=40),  # tăng đáy để chứa legend
        xaxis=dict(
            title="Year",
            # type="category", # ✅ bắt buộc xem năm là rời rạc
            showgrid=False,
            gridcolor="#e0e0e0"
        ),
        yaxis=dict(
            title="Score",
            range=[0, 1000],dtick=100,       
            showgrid=True,
            gridcolor="#e0e0e0"
        ),
        yaxis2=dict(
            title="PD (%)",
            overlaying="y",
            side="right",
            range=[0, 20],dtick=2,       # ✅ không đảo ngược nữa
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.35,              # ✨ đẩy sâu hơn xuống dưới
            yanchor="bottom",
            font=dict(size=13),
            itemwidth=50,
            bgcolor='rgba(0,0,0,0)'  # để trong suốt nếu cần
        ),
        plot_bgcolor="white"        # sửa lỗi gõ nhầm "whit"
    )


    return fig, [{"label": str(y), "value": y} for y in available_years], from_year, [{"label": str(y), "value": y} for y in available_years], to_year


###################################################### CALL OUT RISK COMPONENT


# ==== CALLBACK CHUẨN HÓA ĐẦY ĐỦ CHO SCORE BREAKDOWN + RISK DRIVER ====
# Callback phụ để fill YearReport vào Dropdown
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
    risk_latest = risk_data[risk_data["YearReport"] == latest["YearReport"]]

    pie_labels = [
        f"Financial ({latest['FinancialRisk']}%)",
        f"Industry Non-Financial ({latest['IndustryFinancialRisk']}%)",
        f"Corporate Non-Financial ({latest['CorporateFinancialRisk']}%)"
    ]
    pie_values = [
        latest["FinancialRisk"],
        latest["IndustryFinancialRisk"],
        latest["CorporateFinancialRisk"]
    ]
    
    labels = ["Financial", "Industry Non-Financial", "Corporate Non-Financial"]
    pie_colors = [INDICATOR_COLORS.get(label, "#ddd") for label in labels]

    if compare_toggle and "on" in compare_toggle and from_compare and to_compare:
        from plotly.subplots import make_subplots
        base_data = data[data["YearReport"] == from_compare].iloc[-1]
        compare_data = data[data["YearReport"] == to_compare].iloc[-1]
        pie_fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
        
        # Base year (left pie)
        pie_fig.add_trace(go.Pie(
            values=[base_data["FinancialRisk"], base_data["IndustryFinancialRisk"], base_data["CorporateFinancialRisk"]],
            labels=labels,
            marker=dict(colors=pie_colors),
            hole=0.5,
            textinfo='percent',
            sort=False,
            domain=dict(x=[0, 0.48], y=[0, 1])
        ), row=1, col=1)

        # Compare year (right pie)
        pie_fig.add_trace(go.Pie(
            values=[compare_data["FinancialRisk"], compare_data["IndustryFinancialRisk"], compare_data["CorporateFinancialRisk"]],
            labels=labels,
            marker=dict(colors=pie_colors),
            hole=0.5,
            textinfo='percent',
            sort=False,
            domain=dict(x=[0.52, 1], y=[0, 1])
        ), row=1, col=2)


        # ✅ Bù lại title thủ công + dùng vị trí chính xác
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
                font=dict(size=9),
                itemwidth=90    
            )
        )
    else:
        pie_fig = go.Figure(
            data=[go.Pie(
            labels=pie_labels, values=pie_values,
            marker=dict(colors=["#70ad47", "#5b9bd5", "#ffc000"]),
            hole=0.4
        )
            ],
            layout=go.Layout(height=340, uniformtext_minsize=14, uniformtext_mode='hide',
                            margin=dict(t=10, b=10, l=5, r=5), plot_bgcolor="white",
                            legend=dict(orientation="h", x=0.5, y=-0.3, xanchor="center", yanchor="bottom", font=dict(size=10), itemwidth=90)
                             )
        )


    ################### 2. Bar chart (Relative Contributions)
    indicators = [
        
        # financial drivers
        "Cash Flow Ratios", 
        "Efficiency (Activity) Ratios", 
        "Growth Ratios",
        "Leverage (Solvency) Ratios", 
        "Liquidity Ratios", 
        "Profitability Ratios", 
        "Size Ratios",
        
        # Non financial drivers
        "Scale", 
        "Growth Stability",
        "Tax Compliance Risk", 
        "Industry Trade Activity", 
        "Industry Health Status", 
        "Industry New Business Dynamics"
    ]
    rel_data = risk_latest[risk_latest["Indicator"].isin(indicators)]

    # Tạo danh sách màu tự động từ Plotly Express (hoặc bạn có thể thay bằng Pastel, D3, Set2,...)
    color_list = px.colors.qualitative.Plotly
    color_map = {ind: color_list[i % len(color_list)] for i, ind in enumerate(rel_data["Indicator"].unique())}

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
                x=0.5, y=1.02,                 # Vị trí dưới title
                showarrow=False,
                font=dict(
                    size=10,
                    color="red"
                ),
                align="center"
            )

    for _, row in rel_data.iterrows():
        
        # Bar đổ bóng bên dưới (layer shadow)
        bar_fig.add_trace(go.Bar(
            x=[row["Indicator"]],
            y=[row["Relative"]],
            marker_color='rgba(0, 0, 0, 0.08)',  # màu đổ bóng xám mờ
            width=0.4,
            offset=0,
            showlegend=False,
            hoverinfo="skip"
        ))
    
        bar_fig.add_trace(go.Bar(
            x=[row["Indicator"]],
            y=[row["Relative"]],
            name=row["Indicator"],
            # marker_color=color_map[row["Indicator"]],
            marker_color = INDICATOR_COLORS.get(row["Indicator"], "#888"),
            text=[f"{row['Relative']:.4f}"],     # ✨ Hiển thị giá trị
            textposition="outside",              # ✨ Nằm bên trên cột
            textfont=dict(size=7),
            hoverinfo="x+y",
            showlegend=True,
            # width=0.4,
        ))

        # Cấu hình layout biểu đồ
        bar_fig.update_layout(
            height=400,
            margin=dict(t=5, b=5),
            xaxis=dict(
                showticklabels=False,     # ❌ ẩn label dài dưới trục X
                showgrid=False
            ),
            yaxis=dict(
                # title="Relative Contribution",
                tickfont=dict(size=12),
                showgrid=True,
                gridcolor="#e0e0e0",
                zeroline=True,
                zerolinecolor="#999"
            ),
            legend=dict(
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.6,
                yanchor="bottom",
                font=dict(size=10),
                itemwidth=70,     # ✅ Giảm xuống giúp dễ wrap
                bgcolor="rgba(0,0,0,0)"
            ),legend_tracegroupgap=5
            ,
            bargap=0.25,
            plot_bgcolor="#ffffff"
        )

    # Mũi tên Deterioration (trên)
    bar_fig.add_annotation(
        xref="paper", yref="paper",
        x=1.08, y=1,  # đẩy xa hơn
        text="Deterioration",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="red",
        ax=0,
        ay=55,
        font=dict(size=10, color="red")
    )

    # Mũi tên Improvement (dưới)
    bar_fig.add_annotation(
        xref="paper", yref="paper",
        x=1.08, y=0,
        text="Improvement",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="green",
        ax=0,
        ay=-70,
        font=dict(size=10, color="green")
    )


    # 3. Table builder
    def build_risk_table(df, title):
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

            # Tính Diff cho từng cột
            for col in ["Score", "Contributions", "Median", "Relative"]:
                merged[f"{col}_diff"] = merged[f"{col}_compare"] - merged[f"{col}_base"]

            # Gộp giá trị hiển thị: X (±Y)
            for col in ["Score", "Contributions", "Median", "Relative"]:
                merged[col] = merged[f"{col}_compare"].round(2).astype(str) + " (" + merged[f"{col}_diff"].apply(
                    lambda x: f"+{x:.2f}" if x > 0 else f"{x:.2f}"
                ) + ")"

            # Chuẩn bị bảng hiển thị
            base_final = base_df[["Indicator", "Score", "Contributions", "Median", "Relative"]].copy()
            compare_final = merged[["Indicator", "Score", "Contributions", "Median", "Relative"]].copy()

            # Định dạng phần trăm trước khi concat
            base_final["Contributions"] = base_final["Contributions"].apply(lambda x: f"{x:.2f}%")
            base_final["Relative"] = base_final["Relative"].apply(lambda x: f"{x * 100:.4f}%")


            compare_final["Contributions"] = compare_final["Contributions"].astype(str).str.replace(")", "%)")
            compare_final["Relative"] = compare_final["Relative"].astype(str).str.replace(")", "%)")

            # Đánh dấu dòng Base và Compare
            base_final["TypeRow"] = "Base"
            compare_final["TypeRow"] = "Compare"

            # Gộp 2 bảng
            final = pd.concat([base_final, compare_final], ignore_index=True)
            final = final.sort_values(by=["Indicator", "TypeRow"]).drop(columns=["TypeRow"]).reset_index(drop=True)
            final.loc[final.index % 2 == 1, "Indicator"] = ""

            # Tạo style so sánh
            styles = []
            for i, row in final.iterrows():
                if row["Indicator"] == "":
                    for col in ["Score", "Contributions", "Median", "Relative"]:
                        value = str(row[col])
                        if "(" in value and ")" in value:
                            diff_str = value.split("(")[-1].replace(")", "").replace("+", "").replace("%", "")
                            try:
                                diff = float(diff_str)
                                styles.append({
                                    "if": {"row_index": i, "column_id": col},
                                    "color": "red" if diff < 0 else "green" if diff > 0 else "black",
                                    "fontStyle": "italic",
                                    "fontSize": "11px"
                                })
                            except ValueError:
                                pass
        else:
            # Trường hợp không có Period (không phải so sánh)
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
        "Cash Flow Ratios", 
        "Efficiency (Activity) Ratios", 
        "Growth Ratios",
        "Leverage (Solvency) Ratios", 
        "Liquidity Ratios", 
        "Profitability Ratios", 
        "Size Ratios",
    ]

    non_financial_names = [
        "Scale", 
        "Growth Stability",
        "Tax Compliance Risk", 
        "Industry Trade Activity", 
        "Industry Health Status", 
        "Industry New Business Dynamics"
    ]

    if compare_toggle and "on" in compare_toggle and from_compare and to_compare:
        base_risk = risk_data[risk_data["YearReport"] == from_compare].copy()
        compare_risk = risk_data[risk_data["YearReport"] == to_compare].copy()

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

    return pie_fig, bar_fig, build_risk_table(financial_df, "Financial Risk"), build_risk_table(non_financial_df, "Non-Financial Risk")

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


###################################################### CALL OUT COMMENTARY
def get_risk_grade_definition(pd_value):
    try:
        pd_value = float(pd_value)
    except (ValueError, TypeError):
        return None  # hoặc return "Unknown"

    risk_scale = [
        (0.36, "FG-1", "Negligible risk"),
        (0.50, "FG-2", "Very low risk"),
        (0.70, "FG-3", "Very low risk"),
        (0.98, "FG-4", "Very low risk"),
        (1.36, "FG-5", "Low risk"),
        (1.90, "FG-6", "Low risk"),
        (2.64, "FG-7", "Low risk"),
        (3.68, "FG-8", "Moderate risk"),
        (5.13, "FG-9", "Moderate risk"),
        (7.15, "FG-10", "Moderate risk"),
        (9.96, "FG-11", "High risk"),
        (13.87, "FG-12", "High risk"),
        (19.32, "FG-13", "Very high risk"),
        (26.91, "FG-14", "Very high risk"),
        (37.48, "FG-15", "Very high risk"),
        (52.20, "FG-16", "Near default"),
        (72.71, "FG-17", "Near default"),
        (100.0, "FG-18", "Defaulted")
    ]
    for threshold, grade, definition in risk_scale:
        if pd_value <= threshold:
            return definition
    return "Defaulted"


def generate_commentary(taxcode: str) -> str:
    df_score = score_df[score_df["TaxCode"].astype(str) == taxcode].sort_values("YearReport")
    df_risk = risk_indicator_df[risk_indicator_df["TaxCode"].astype(str) == taxcode]

    if df_score.empty or df_risk.empty:
        return "No commentary available for this taxcode."

    latest = df_score.iloc[-1]
    previous = df_score.iloc[-2] if len(df_score) > 1 else None
    diff = latest["Score"] - previous["Score"] if previous is not None else 0
    median_row = risk_indicator_df[
    (risk_indicator_df["TaxCode"].astype(str) == taxcode) &
    (risk_indicator_df["YearReport"] == latest["YearReport"])
    ]

    model_median = float(median_row["Median_sum"].iloc[0]) if not median_row.empty else None

    
    diff_word = "increased" if diff > 0 else "decreased"
    diff_color = "green" if diff > 0 else "red"
    risk_def = get_risk_grade_definition(latest["PD"])
    
    # Format chính
    score_val = int(latest["Score"])
    pd_val = round(latest["PD"], 2)
    avg_industry = int(latest["avg_scoreindus"])
    avg_size = int(latest["avg_Scoresize"])
        
    if model_median:
        is_score_higher = latest["Score"] > model_median
        score_vs_model = "higher" if is_score_higher else "lower"
        credit_position = "stronger" if is_score_higher else "weaker"
        
        score_vs_color = "green" if is_score_higher else "red"
        credit_color = "green" if is_score_higher else "red"
        
        line1 = (
            f"The company’s current score is <strong>{int(latest['Score'])}</strong>, corresponding to a PD of <strong>{round(latest['PD'], 2)}%</strong> "
            f"<span style='color:orange'><strong>({risk_def})</strong></span>. "
            f"This score is significantly <span style='color:{score_vs_color}; font-weight:bold'>{score_vs_model}</span> than the <strong>model segment benchmark</strong> of "
            f"<strong>{int(model_median)}</strong>, indicating a relatively <span style='color:{credit_color}; font-weight:bold'>{credit_position}</span> credit position within its peer group."
        )
    else:
        line1 = "Model segment benchmark is not available for this company."


    line2 = (
        f"Compared to the previous year, the current score has "
        f"<span style='color:{diff_color}; font-weight:bold'>{diff_word}</span> by <strong>{abs(int(diff))}</strong> points, "
        f"which may indicate a change in risk factors."
    )

    # Top 3 contributors
    latest_risk = df_risk[df_risk["YearReport"] == latest["YearReport"]]
    top3 = latest_risk.sort_values("Contributions", ascending=False).head(3)

    ranking_labels = ["top contributing factor", "second most contributing factor", "third most contributing factor"]

    bullets = []
    for idx, (_, row) in enumerate(top3.iterrows()):
        indicator = row["Indicator"]
        score = float(row["Score"])
        median = float(row["Median"])
        trend = "higher" if score > median else "lower"
        impact = "reduce" if trend == "higher" else "increase"
        impact_color = "red" if impact == "reduce" else "green"

        bullets.append(
            f"<strong>{indicator}</strong> is the {ranking_labels[idx]}, "
            f"currently at <strong>{score:.0f}</strong> vs model segment median <strong>{median:.0f}</strong>, "
            f"and tends to <span style='color:{impact_color}; font-weight:bold'>{impact}</span> the overall score."
        )


    # Combine all
    full_comment = (
        f"<p>{line1}</p>"
        f"<p>{line2}</p>"
        + "<ul style='margin-top:10px;'>" + "".join([f"<li>{b}</li>" for b in bullets]) + "</ul>"
    )

    return full_comment


@app.callback(
    Output("commentary-box", "children"),
    Input("taxcode-input", "value")
)
def update_commentary(taxcode):
    if not taxcode:
        return ""
    commentary = generate_commentary(str(taxcode))
    return dcc.Markdown(commentary, dangerously_allow_html=True)


###################################################### CALL OUT Probability of Default Term Structure
# Load term_df chuẩn
term_df = pd.read_csv('data_final/term.csv')
term_df.columns = term_df.columns.str.strip()
term_cols = [col for col in term_df.columns if col.startswith("PD_")]

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

    # Lấy PD_latest + Grade
    company_data = score_df[score_df['TaxCode'].astype(str) == str(taxcode).strip()]
    if company_data.empty:
        return [{}], [{}], [{}], [{}]

    latest = company_data.sort_values("YearReport").iloc[-1]
    pd_latest = latest["PD"] / 100    # ✅ chuyển từ % → xác suất
    grade = str(latest["Grade"]).strip()

    # Tra hệ số theo Grade
    term_row = term_df[term_df["Grade"].astype(str).str.strip() == grade]
    if term_row.empty:
        return [{}], [{}], [{}], [{}]

    term_row = term_row.iloc[0]
    table_PD_1Y = term_row.get("PD_1Y", None)

    # Nếu không có PD_1Y thì bỏ qua
    if pd.isna(table_PD_1Y) or table_PD_1Y == 0:
        return [{}], [{}], [{}], [{}]

    # Tính Monthly Term Structure
    monthly_data = {}
    for i in range(1, 13):
        table_PD_t = term_row.get(f"PD_{i}M", None)
        if pd.notna(table_PD_t):
            factor = table_PD_t / table_PD_1Y
            pd_term = pd_latest * factor
            monthly_data[f"m{i}"] = f"{pd_term:.4%}"    # ✅ format kiểu 1.23%
        else:
            monthly_data[f"m{i}"] = None

    # Tính Yearly Term Structure
    yearly_data = []
    for i in range(1, 36):
        table_PD_t = term_row.get(f"PD_{i}Y", None)
        if pd.notna(table_PD_t):
            factor = table_PD_t / table_PD_1Y
            pd_term = pd_latest * factor
            yearly_data.append(f"{pd_term:.4%}")    # ✅ format kiểu 1.23%
        else:
            yearly_data.append(None)

    # Chia bảng Yearly thành 3 block
    yearly_table_1 = {f"y{i+1}": yearly_data[i] for i in range(12)}
    yearly_table_2 = {f"y{i+13}": yearly_data[i+12] for i in range(12)}
    yearly_table_3 = {f"y{i+25}": yearly_data[i+24] for i in range(11)}

    return [monthly_data], [yearly_table_1], [yearly_table_2], [yearly_table_3]

###################################################### CALL OUT Distribution of Score  

# 🔄 Callback
@app.callback(
    Output("distribution-chart", "figure"),
    Output("distribution-info", "children"),
    Input("taxcode-input", "value")
)
def update_chart(taxcode):
    if not taxcode:
        return go.Figure()
    return plot_distribution_chart(taxcode)



# 📊 Hàm vẽ Distribution
def plot_distribution_chart(taxcode):
    profile_row = profile_df[profile_df["TaxCode"].astype(str).str.strip() == str(taxcode).strip()]
    if profile_row.empty:
        return go.Figure()

    profile_row = profile_row.iloc[0]
    segment = str(profile_row["Modelsegmentsize"]).strip() + "_" + str(profile_row["Modelsegmentvsic"]).strip()

    dist_filtered = distribution_df[distribution_df["Segment"].astype(str).str.strip() == segment]
    if dist_filtered.empty:
        return go.Figure()

    scores = score_df[score_df["TaxCode"].astype(str).str.strip() == str(taxcode).strip()]
    if scores.empty:
        current_grade = None
    else:
        latest_score = scores.sort_values("YearReport").iloc[-1]
        current_grade = str(latest_score["Grade"]).strip()

    fg_order = [f"FG-{i}" for i in range(1, 19)]
    fg_counts = {fg: 0 for fg in fg_order}
    grouped = dist_filtered.groupby("FG")["count"].sum().to_dict()
    fg_counts.update(grouped)

    x_labels = fg_order
    y_values = [fg_counts[fg] for fg in fg_order]

    bar_colors = ["#0752ad" if fg != current_grade else "#FFC000" for fg in fg_order]

    fig = go.Figure(data=[
        go.Bar(x=x_labels, y=y_values, marker_color=bar_colors)
    ])

    fig.update_layout(
        # title="Distribution of Score Grades",
        xaxis_title="Score Grade (FG)",
        yaxis_title="Total Count",
        template="simple_white",
        height=350,
        margin=dict(t=10, b=40, l=40, r=10)
    )
    
    model_segment = str(profile_row["Modelsegmentsize"]).strip() + " - " + str(profile_row["Modelsegmentvsic"]).strip()
    company_industry_name = str(profile_row["en_VSICName (LV3)"]).strip()
    
    # ✅ Thông tin bên dưới
    info = html.Div([
        html.P(["Industry: ", html.B(company_industry_name)]),
        html.P(["Model Segment: ", html.B(model_segment)]),
        html.P(["Current Grade: ", html.B(current_grade)])
    ])

    return fig,info


###################################################### RUN APP

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)

# if __name__ == "__main__":
#     app.run(debug=True)
