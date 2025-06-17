# src/risk_scale_utils.py

#================================ Định nghĩa thông tin Risk Scale chuẩn hoá
RISK_SCALE = [
    {"grade": "FG-1",  "score_range": "903–1000", "label": "Negligible risk", "pd": 0.36,   "color": "#00B050"},
    {"grade": "FG-2",  "score_range": "822–903",  "label": "Very low risk",    "pd": 0.50,   "color": "#00CC00"},
    {"grade": "FG-3",  "score_range": "766–822",  "label": "Very low risk",    "pd": 0.70,   "color": "#00CC00"},
    {"grade": "FG-4",  "score_range": "700–766",  "label": "Very low risk",    "pd": 0.98,   "color": "#00CC00"},
    {"grade": "FG-5",  "score_range": "660–700",  "label": "Low risk",         "pd": 1.36,   "color": "#92D050"},
    {"grade": "FG-6",  "score_range": "628–660",  "label": "Low risk",         "pd": 1.90,   "color": "#92D050"},
    {"grade": "FG-7",  "score_range": "599–628",  "label": "Low risk",         "pd": 2.64,   "color": "#92D050"},
    {"grade": "FG-8",  "score_range": "570–599",  "label": "Moderate risk",    "pd": 3.68,   "color": "#FFE699"},
    {"grade": "FG-9",  "score_range": "540–570",  "label": "Moderate risk",    "pd": 5.13,   "color": "#FFE699"},
    {"grade": "FG-10", "score_range": "510–540",  "label": "Moderate risk",    "pd": 7.15,   "color": "#FFE699"},
    {"grade": "FG-11", "score_range": "482–510",  "label": "High risk",        "pd": 9.96,   "color": "#FFC000"},
    {"grade": "FG-12", "score_range": "457–482",  "label": "High risk",        "pd": 13.87,  "color": "#FFC000"},
    {"grade": "FG-13", "score_range": "428–457",  "label": "High risk",        "pd": 19.32,  "color": "#FFC000"},
    {"grade": "FG-14", "score_range": "389–428",  "label": "Very high risk",   "pd": 26.91,  "color": "#ED7D31"},
    {"grade": "FG-15", "score_range": "356–389",  "label": "Very high risk",   "pd": 37.48,  "color": "#ED7D31"},
    {"grade": "FG-16", "score_range": "326–389",  "label": "Near default",     "pd": 52.20,  "color": "#FF0000"},
    {"grade": "FG-17", "score_range": "257–326",  "label": "Near default",     "pd": 72.71,  "color": "#FF0000"},
    {"grade": "FG-18", "score_range": "0–257",     "label": "Defaulted",        "pd": 100.0,  "color": "#C00000"},
]


def get_risk_info_by_grade(grade):
    """Trả về dict chứa thông tin label, màu, PD dựa vào mã grade"""
    for entry in RISK_SCALE:
        if entry["grade"] == grade:
            return entry
    return {"label": "Unknown", "color": "#ccc", "pd": None, "score_range": "-"}


def get_risk_label_by_pd(pd_value):
    """Tìm grade và label tương ứng với PD đầu vào"""
    try:
        pd_value = float(pd_value)
    except (ValueError, TypeError):
        return None

    for entry in RISK_SCALE:
        if pd_value <= entry["pd"]:
            return entry["label"]
    return "Defaulted"

#================================ ĐỊNH NGHĨA MÀU CHO CÁC COMPONENT
INDICATOR_COLORS = {
    # ## old version
    # "Cash Flow Ratios": "#4f81bd",
    # "Efficiency (Activity) Ratios": "#b8cf89",
    # "Growth Ratios": "#79c1d5",
    # "Leverage (Solvency) Ratios": "#536e8f",
    # "Liquidity Ratios": "#7b8d54",
    # "Profitability Ratios": "#5a8d9b",
    # "Size Ratios": "#8aacd3",
    # "Growth Stability": "#95cedd",
    # "Tax Compliance Risk": "#6a8cb4",
    # "Industry Health Status": "#96af63",
    # "Industry Trade Activity": "#bacee5",
    # "Industry New Business Dynamics": "#5ca4b7",
    # "Scale": "#bed393",

    # Financial
    "Growth Ratios":"#4f81bd",
    "Profitability Ratios":"#b8cf89",
    "Efficiency Ratios":"#79c1d5",
    "Liquidity Ratios":"#536e8f",
    "Leverage Ratios":"#7b8d54",
    "Cash Flow Ratios":"#5a8d9b",
    "Size Ratios":"#8aacd3",

    # Organ
    "Business Activity History": "#95cedd",
    "Company Size":"#6a8cb4",
    "Statutory Compliance Risk": "#96af63",
    "News Sentiment Risk": "#bacee5",
    "Import Volume Trend": "#5ca4b7",
    "Export Volume Trend": "#bed393",

    # Industry
    "Import Volume Trend in Industry":"#4f81bd",
    "Export Volume Trend in Industry":"#b8cf89",
    "Distress Businesses":"#79c1d5",
    "Active Business in Industry":"#536e8f",
    "New Business Registrations":"#5a8d9b",


    ## Pie chart
    "FinancialRisk": "#4f81bd",
    "IndustryRisk": "#9bbb59",
    "OrganizationRisk": "#4bacc6",


    ## trend of score
    "Score Model Segment": "#4bacc6",
    "Score Company": "#0752ad",
    "Probability of Default (%)": "#9bbb59"
}

#================================ MASTER COMMENT
import pandas as pd

# === Generate_1,2 ===

COMMENT_RULES_1 = pd.DataFrame([
    # ==== Generate_1 (So sánh với median score segment)
    {"Type": "Generate_1", "Delta_Min": -1000, "Delta_Max": -101, "Label": "Much Lower", "Comment": "The company's score is significantly lower than the segment median, indicating a weak credit position relative to its peers."},
    {"Type": "Generate_1", "Delta_Min": -100, "Delta_Max": -31, "Label": "Lower", "Comment": "The company's score is slightly lower than the segment median, indicating a somewhat weak credit position relative to its peers."},
    {"Type": "Generate_1", "Delta_Min": -30, "Delta_Max": 30, "Label": "Similar", "Comment": "The company's score is comparable to the segment median, indicating a similar credit position relative to its peers."},
    {"Type": "Generate_1", "Delta_Min": 30, "Delta_Max": 100, "Label": "Higher", "Comment": "The company's score is slightly higher than the segment median, indicating a somewhat strong credit position relative to its peers."},
    {"Type": "Generate_1", "Delta_Min": 100, "Delta_Max": 1000, "Label": "Much Higher", "Comment": "The company's score is significantly higher than the segment median, indicating a strong credit position relative to its peers."},

    # ==== Generate_2 (So sánh thay đổi điểm theo thời gian)
    {"Type": "Generate_2", "Delta_Min": -1000, "Delta_Max": -76, "Label": "Significant decrease", "Comment": "indicating a strong deterioration in credit condition."},
    {"Type": "Generate_2", "Delta_Min": -75, "Delta_Max": -26, "Label": "Slight decrease", "Comment": "indicating a slight weakening in credit profile."},
    {"Type": "Generate_2", "Delta_Min": -25, "Delta_Max": 26, "Label": "Stable", "Comment": "indicating a stable credit position.."},
    {"Type": "Generate_2", "Delta_Min": 25, "Delta_Max": 76, "Label": "Slight increase", "Comment": "indicating a gradual improvement in credit standing."},
    {"Type": "Generate_2", "Delta_Min": 75, "Delta_Max": 1000, "Label": "Significant increase", "Comment": "indicating a strong positive credit trend."}
])


# === Risk Factor Comment ===

COMMENT_RULES_2 = {

    # Financial risk
    "Growth Ratios": {
        "Positive": "The indicators in the Growth Ratios group show a more positive signal compared to the industry, indicating strong business expansion.",
        "Negative": "The indicators in the Growth Ratios group show a more negative signal compared to the industry, indicating weak business growth."
    },
    "Profitability Ratios": {
        "Positive": "The indicators in the Profitability Ratios group show a more positive signal, indicating efficient profit generation.",
        "Negative": "The indicators in the Profitability Ratios group show a more negative signal, indicating poor profit performance."
    },
    "Efficiency Ratios": {
        "Positive": "The indicators in the Efficiency Ratios group show a more positive signal, indicating good use of resources.",
        "Negative": "The indicators in the Efficiency Ratios group show a more negative signal, indicating inefficient resource usage."
    },
    "Liquidity Ratios": {
        "Positive": "The indicators in the Liquidity Ratios group show a more positive signal, indicating strong short-term solvency.",
        "Negative": "The indicators in the Liquidity Ratios group show a more negative signal, indicating liquidity pressure."
    },
    "Leverage Ratios": {
        "Positive": "The indicators in the Leverage Ratios group show a more positive signal, indicating prudent financial leverage.",
        "Negative": "The indicators in the Leverage Ratios group show a more negative signal, indicating excessive financial risk."
    },
    "Cash Flow Ratios": {
        "Positive": "The indicators in the Cash Flow Ratios group show a more positive signal, indicating healthy cash generation.",
        "Negative": "The indicators in the Cash Flow Ratios group show a more negative signal, indicating weak internal cash flow."
    },
    "Size Ratios": {
        "Positive": "The indicators in the Size Ratios group show a more positive signal, indicating a strong scale of operations.",
        "Negative": "The indicators in the Size Ratios group show a more negative signal, indicating limited operational scale."
    },

    #Non Financial Risk
    "Business Activity History": {
        "Positive": "The indicators in the Business Activity History group show a more positive signal, indicating stable business continuity.",
        "Negative": "The indicators in the Business Activity History group show a more negative signal, indicating operational instability."
    },    
    "Company Size": {
        "Positive": "The indicators in the Company Size group show a more positive signal, indicating significant market presence.",
        "Negative": "The indicators in the Company Size group show a more negative signal, indicating a smaller market footprint."
    },  
    "Statutory Compliance Risk": {
        "Positive": "The indicators in the Statutory Compliance Risk group show a more positive signal, indicating good legal compliance.",
        "Negative": "The indicators in the Statutory Compliance Risk group show a more negative signal, indicating compliance risks."
    },  
    "News Sentiment Risk": {
        "Positive": "The indicators in the News Sentiment Risk group show a more positive signal, indicating good public image.",
        "Negative": "The indicators in the News Sentiment Risk group show a more negative signal, indicating reputational risk."
    },  
    "Import Volume Trend": {
        "Positive": "The indicators in the Import Volume Trend group show a more positive signal, indicating strong supply activity.",
        "Negative": "The indicators in the Import Volume Trend group show a more negative signal, indicating weak supply capacity."
    },  
    "Export Volume Trend": {
        "Positive": "The indicators in the Export Volume Trend group show a more positive signal, indicating healthy export activity.",
        "Negative": "The indicators in the Export Volume Trend group show a more negative signal, indicating weak export demand."
    },  
    "Import Volume Trend in Industry": {
        "Positive": "The indicators in the Industry Import Volume Trend group show a more positive signal, indicating sector-wide demand.",
        "Negative": "The indicators in the Industry Import Volume Trend group show a more negative signal, indicating contracting demand."
    },  
    "Export Volume Trend in Industry": {
        "Positive": "The indicators in the Industry Export Volume Trend group show a more positive signal, indicating strong trade expansion.",
        "Negative": "The indicators in the Industry Export Volume Trend group show a more negative signal, indicating falling trade output."
    },  
    "Distress Businesses": {
        "Positive": "The indicators in the Distress Businesses group show a more positive signal, indicating sector stability.",
        "Negative": "The indicators in the Distress Businesses group show a more negative signal, indicating elevated market risk."
    },  
    "Active Business in Industry": {
        "Positive": "The indicators in the Active Business group show a more positive signal, indicating sector vibrancy.",
        "Negative": "The indicators in the Active Business group show a more negative signal, indicating economic slowdown."
    },  
    "New Business Registrations": {
        "Positive": "The indicators in the New Business Registrations group show a more positive signal, indicating strong market dynamism.",
        "Negative": "The indicators in the New Business Registrations group show a more negative signal, indicating low market entry."
    }
}


