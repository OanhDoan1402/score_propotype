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



# call file layout
from layout.layout import get_layout

from src import (
    # auth,               
    score_summary,
    score_trend,
    risk_component,
    commentary,
    pd_term_structure,
    distribution_chart,
)

# Khởi tạo Dash app
app = dash.Dash(__name__)
server = app.server


# # Cấu hình xác thực (nếu dùng)
# VALID_USERNAME_PASSWORD = auth.credentials
# dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD)

# Giao diện tổng
app.layout = get_layout()
app.title = "FiinGate Credit Score Viewer"

# Gọi các hàm đăng ký callback
score_summary.register_callbacks(app)
score_trend.register_callbacks(app)
risk_component.register_callbacks(app)
commentary.register_callbacks(app)
pd_term_structure.register_callbacks(app)
distribution_chart.register_callbacks(app)

# Run (deploy render)
# if __name__ == "__main__":
#     app.run(debug=False, host="0.0.0.0", port=8080)

## Run (test local)
if __name__ == "__main__":
    app.run(debug=True)
