
from dash import dcc, html, Input, Output
import pandas as pd
from src.data_loader import score_df, risk_indicator_df
from src.risk_scale_utils import COMMENT_RULES_1, COMMENT_RULES_2,RISK_SCALE


def lookup_generate_comment(df_rule, rule_type, delta):
    match = df_rule[
        (df_rule["Type"] == rule_type) &
        (df_rule["Delta_Min"] <= delta) &
        (df_rule["Delta_Max"] >= delta)
    ]
    return match["Comment"].values[0] if not match.empty else ""

def lookup_risk_factor_comment(indicator, relative_val):
    if indicator not in COMMENT_RULES_2:
        return ""
    direction = "Positive" if relative_val > 0 else "Negative"
    return COMMENT_RULES_2[indicator].get(direction, "")

# === Lấy label + color từ RISK_SCALE dựa vào PD ===
def get_pd_risk_info(pd_val):
    try:
        pd_float = float(str(pd_val).replace('%', '').strip())
    except:
        return "", ""

    for item in RISK_SCALE:
        if pd_float <= item["pd"]:
            return item["label"], item["color"]
    return "", ""

def style_g1_text(text):
    highlight_map = {
        "significantly lower": "#C00000",   # red
        "slightly lower": "#C00000",        # red
        "slightly higher": "#008000",       # green
        "significantly higher": "#008000",  # green
        "comparable": "#f4a100",            # orange/yellow
        "weak":"#C00000",
        "strong": "#008000",
        "similar": "#f4a100", 
    }

    parts = []
    lowered = text.lower()
    i = 0

    while i < len(text):
        matched = False
        for phrase, color in highlight_map.items():
            if lowered[i:].startswith(phrase):
                parts.append(html.Span(phrase, style={"color": color, "fontWeight": "bold"}))
                i += len(phrase)
                matched = True
                break
        if not matched:
            parts.append(text[i])
            i += 1

    return html.Span(parts)



def generate_commentary(taxcode: str):
    profile = score_df[score_df["TaxCode"].astype(str) == str(taxcode)].sort_values("YearReport")
    if profile.empty:
        return html.Div("No data available.")

    latest = profile.iloc[-1]
    year = int(latest["YearReport"])
    prev_year = year - 1
    previous = profile[profile["YearReport"] == prev_year]
    previous = previous.iloc[-1] if not previous.empty else None

    median_row = risk_indicator_df[
    (risk_indicator_df["TaxCode"].astype(str) == taxcode) &
    (risk_indicator_df["YearReport"] == latest["YearReport"])
    ]

    score = latest["Score"]
    score_segment = float(median_row["Median_sum"].iloc[0]) if not median_row.empty else None
    delta_score = score - previous["Score"] if previous is not None else 0

    pd_val = latest["PD"]
    # Ép kiểu an toàn
    try:
        pd_val_float = float(str(pd_val).replace('%', '').strip())
    except ValueError:
        pd_val_float = 0.0
    pd_label, pd_color = get_pd_risk_info(pd_val)

    pd_span = html.Span(f" ({pd_label})", style={"color": pd_color, "fontWeight": "bold"})

    year = latest["YearReport"]
    # G1 + G2
    g1 = lookup_generate_comment(COMMENT_RULES_1, "Generate_1", score - score_segment)
    g2 = lookup_generate_comment(COMMENT_RULES_1, "Generate_2", delta_score)

    base_text = [
        html.P([
            f"The company’s current score is ", html.B(f"{score:,}"),
            f", corresponding to a PD of ", html.B(f"{pd_val_float:.2f}%"), html.Span(f" ({pd_label})", style={"color": pd_color, "fontWeight": "bold"}),
            f". Compared to the model segment benchmark of ", html.B(f"{int(score_segment)}"), ", ",
            style_g1_text(g1)
        ]),
        html.P([
        "Compared to the previous year, the current score has ",
        html.Span(
            "increased" if delta_score > 0 else "decreased",
            style={
                "color": "green" if delta_score > 0 else "red",
                "fontWeight": "bold"
            }
        ),
        f" by ", html.B(f"{abs(delta_score):.0f}"), " points, ",
        g2,
        f" The following risk drivers have the most significant impact on the company’s overall score."
        ])
    ]


    # RISK FACTOR COMMENTARY
    risk_data = risk_indicator_df[risk_indicator_df["TaxCode"].astype(str) == str(taxcode)]
    latest_risk = risk_data[risk_data["YearReport"] == year]
    if "MonthReport" in latest_risk.columns:
        latest_risk = latest_risk[latest_risk["MonthReport"] == latest_risk["MonthReport"].max()]

    top_factors = latest_risk.nlargest(3, "Contributions", keep="all")

    bullets = []
    for i, row in enumerate(top_factors.itertuples(), start=1):
        ind = row.Indicator
        sc = row.Score
        md = row.Median
        rel = row.Relative
        diff = sc - md
        direction = "increase" if diff > 0 else "decrease" if diff < 0 else "no change"
        interpretation = lookup_risk_factor_comment(ind, rel)

        bullets.append(html.Li([
            html.B(f"{ind}"), f" is the {'top' if i==1 else 'second' if i==2 else 'third'} most contributing factor, currently at ",
            html.B(f"{int(sc)}"), " vs model segment median ", html.B(f"{int(md)}"), ", and tends to ",
            html.Span("reduce", style={"color": "red","fontWeight": "bold"}) if rel < 0 else html.Span("enhance", style={"color": "green","fontWeight": "bold" }),
            " the overall score. ",
            interpretation
        ]))

    return html.Div([
        html.Div(base_text + [html.Ul(bullets)], style={
            "fontSize": "17px",
            # "lineHeight": "2.0em",
            "padding": "0px 15px",
            "textAlign": "justify"
        })
    ])



def register_callbacks(app):
    @app.callback(
        Output("commentary-box", "children"),
        Input("taxcode-input", "value")
    )
    def update_commentary(taxcode):
        if not taxcode:
            return ""
        return generate_commentary(str(taxcode))
