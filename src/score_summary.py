# src/score_summary.py
from dash import html, Input, Output
from src.data_loader import profile_df, score_df
from src.risk_scale_utils import get_risk_info_by_grade
import pandas as pd


def register_callbacks(app):

    @app.callback(
        Output('company-info', 'children'),
        Output('score-summary', 'children'),
        Input('taxcode-input', 'value')
    )
    def update_output(taxcode):
        if not taxcode or taxcode not in profile_df['TaxCode'].astype(str).values:
            return html.Div("No matching company found.", style={"textAlign": "center"}), html.Div()

        profile = profile_df[profile_df['TaxCode'].astype(str) == taxcode].iloc[0]
        scores = score_df[score_df['TaxCode'].astype(str).str.strip() == str(taxcode).strip()]

        if scores.empty:
            return html.Div("No score data found."), html.Div()

        latest = scores.sort_values("YearReport").iloc[-1]
        latest_year = int(latest["YearReport"])
        prev_year = latest_year - 1
        
        previous_df = scores[scores["YearReport"] == prev_year]
        previous = previous_df.iloc[-1] if not previous_df.empty else None
        delta = latest["Score"] - previous["Score"] if previous is not None else None

        # Dùng risk_scale_utils
        risk_grade = str(latest["Grade"]).strip()
        pd_val = latest["PD"]
        risk_info = get_risk_info_by_grade(risk_grade)

        grade_color = risk_info["color"]
        risk_label = risk_info["label"]

        company_info = html.Div([
            html.H3(profile['OrganizationName'], style={"color": "#004a99", "marginBottom": "10px", "textTransform": "uppercase"}),
            html.Div([html.Span("Tax Code: ", style={"fontWeight": "bold"}), html.Span(profile['TaxCode'])]),
            html.Div([html.Span("Operating Status: ", style={"fontWeight": "bold"}), html.Span(profile['en_ActiveStatusName'])]),
            html.Div([html.Span("Ticker: ", style={"fontWeight": "bold"}), html.Span(profile['Ticker'])]),
            html.Div([html.Span("En_Name: ", style={"fontWeight": "bold"}), html.Span(profile['en_OrganizationName'])]),
            html.Div([html.Span("Industry: ", style={"fontWeight": "bold"}), html.Span(profile['en_VSICName (LV3)'])]),
            html.Div([html.Span("Model Segment: ", style={"fontWeight": "bold"}), html.Span(profile['ModelSegment'])]),
        ], style={"textAlign": "left", "lineHeight": "1.8", "margin": "auto", "width": "100%", "fontSize": "18px"})

        score_summary = html.Div([
            html.Div([
                html.Div("Total Score: (1-1000 scale)", style={
                    "fontSize": "16px", "color": "#999", "textAlign": "center", "marginBottom": "8px"
                }),
                html.Div([
                    html.Div(str(int(latest["Score"])), style={
                        "fontSize": "40px", "fontWeight": "bold", "backgroundColor": grade_color,
                    "border": "0.5px solid white", "padding": "20px 20px", "borderRadius": "5px 0 0 5px",
                    "boxShadow": "0px 0px 10px rgba(0,0,0,0.25)", "width": "50%", "textAlign": "center"
                    }),
                    html.Div(risk_grade, style={
                        "fontSize": "36px", "fontWeight": "bold", "backgroundColor": grade_color,
                    "border": "0.5px solid white", "padding": "20px 20px", "borderRadius": "0 5px 5px 0",
                    "boxShadow": "0px 0px 10px rgba(0,0,0,0.25)", "width": "50%", "textAlign": "center"
                    }),
                ], style={"display": "flex", "marginBottom": "15px","marginLeft": "35px"}),

                html.Div(risk_label, style={
                    "textAlign": "center", "fontWeight": "bold", "fontSize": "26px", "marginBottom": "10px","marginLeft": "35px"
                }),

                html.Div([
                    html.Div([
                        html.Div("Previous", style={"fontSize": "13px", "textAlign": "center", "marginBottom": "4px"}),
                        html.Div(str(int(previous["Score"])) if previous is not None else "Not available", style={
                            "fontWeight": "bold", "textAlign": "center", "fontSize": "20px"
                        })
                    ], style={"border": "1px solid #ccc", "borderRadius": "10px", "padding": "10px", "width": "90px",
                        "boxShadow": "0px 0px 10px rgba(0,0,0,0.2)"}),

                    html.Div([
                        html.Div("Change", style={"fontSize": "13px", "textAlign": "center", "marginBottom": "4px"}),
                        html.Div(f"{delta:+}" if delta is not None else "Not available", style={
                            "fontWeight": "bold", "textAlign": "center",
                            "color": "red" if delta > 0 else "green", "fontSize": "20px"
                        })
                    ], style={"border": "1px solid #ccc", "borderRadius": "10px", "padding": "10px", "width": "90px",
                        "boxShadow": "0px 0px 10px rgba(0,0,0,0.2)"}),

                    html.Div([
                        html.Div("PD", style={"fontSize": "13px", "textAlign": "center", "marginBottom": "4px"}),
                        html.Div(f"{pd_val}", style={
                            "fontWeight": "bold", "textAlign": "center", "fontSize": "20px"
                        })
                    ], style={"border": "1px solid #ccc", "borderRadius": "10px", "padding": "10px", "width": "90px",
                        "boxShadow": "0px 0px 10px rgba(0,0,0,0.2)"})
                ], style={"display": "flex", "gap": "15px", "marginBottom": "20px","width": "100%","marginLeft": "45px"}),

                html.Div([
                    html.Div([
                        html.Span("● "),
                        "Current score based on Financial Statement: ",
                        html.B(str(int(latest["YearFS"])) if pd.notna(latest["YearFS"]) else "Not available")
                    ]),
                    html.Div([
                        html.Span("● "),
                        "Model Segment: ",
                        html.B(str(profile["ModelSegment"]) if pd.notna(profile["ModelSegment"]) else "Not available")
                    ]),
                    html.Div([
                        html.Span("● "),
                        "Trade credit limit recommendation: ",
                        html.B(f"{int(profile['TotalTradeCreditLimit']):,} VND".replace(",", ".") if pd.notna(profile["TotalTradeCreditLimit"]) else "Not available")
                    ])
                ], style={"fontSize": "17px", "color": "#333", "lineHeight": "2", "width": "100%","marginLeft": "15px"})

            ])
        ], style={"display": "flex", "justifyContent": "flex-start", "marginTop": "30px"})

        return company_info, score_summary



