from dash import html, dcc
from dash import dash_table
import dash_daq as daq             # ✅ Đúng

# from dash import dash_core_components as dcc


def get_layout():
    return html.Div([
        # Toàn bộ khung chính
        html.Div([
            html.Div(
                html.H1("FIINGATE SCORE DASHBOARD", style={
                    "color": "white",  ##    
                    "fontSize": "32px",
                    "fontWeight": "bold",
                    "margin": "0",
                    "padding": "15px 0",
                    "textAlign": "center"
                }),
                style={
                    "width": "100%",
                    "backgroundColor": "#2c5d87", ## 
                    "boxShadow": "0px 0px 12px rgba(0,0,0,0.15)",
                    "marginBottom": "20px"
                }
            )
            
            ,

            ############################### Nhập taxcode & ttin cơ bản
            html.Div([
                html.Label("Enter TaxCode:", style={"marginRight": "10px", "fontSize": "16px","fontWeight": "bold"}),
                dcc.Input(
                    id='taxcode-input',
                    type='text',
                    debounce=True,
                    placeholder="Enter taxcode",
                    style={
                        "width": "400px",
                        "padding": "8px 12px",
                        "fontSize": "16px",
                        "border": "1px solid #ccc",
                        "borderRadius": "10px",
                        "display": "inline-block"
                    }
                )
            ], style={
                "textAlign": "center",
                "marginBottom": "30px",
                "marginTop": "30px"
            }),

            # Company info sẽ được hiển thị bên trái nhưng theo cùng khung
            html.Div(id='company-info', style={
                "textAlign": "left",
                "fontSize": "16px",
                "marginBottom": "30px",
                "lineHeight": "1.8"
            }),

            ############################### Bảng Risk Scale and Interpretation
            html.Details([
                html.Summary("Risk Scale and Interpretation", style={
                    "cursor": "pointer",
                    "fontWeight": "bold",
                    "fontSize": "20px",
                    "marginBottom": "10px",
                    "color": "#004a99"
                }),

                html.Table([
                    html.Tr([
                        html.Th("Risk Grade", style={"border": "1px solid gray", "padding": "6px", "backgroundColor": "#f0f0f0", "textAlign": "left"})
                    ] + [
                        html.Th(f"FG-{i}", style={
                            "border": "1px solid gray",
                            "padding": "6px",
                            "backgroundColor": color,
                            "color": "black"
                        }) for i, color in zip(range(1, 19), [
                            "#00B050", "#00CC00", "#00CC00", "#00CC00", "#92D050", "#92D050", "#92D050",
                            "#FFE699", "#FFE699", "#FFE699", "#FFC000", "#FFC000", "#FFC000",
                            "#ED7D31", "#ED7D31", "#FF0000", "#FF0000", "#C00000"
                        ])
                    ]),

                    html.Tr([
                        html.Td("Risk Score", style={"border": "1px solid gray", "padding": "6px", "textAlign": "left"})
                    ] + [
                        html.Td(score, style={"border": "1px solid gray", "padding": "6px"}) for score in [
                            "903–1000",
                            "822-903", 
                            "766–822", 
                            "700–766",
                            "660–700", 
                            "628–660", 
                            "599–628",
                            "570–599", 
                            "540–570", 
                            "510–540",
                            "482–510", 
                            "457–482", 
                            "428–457",
                            "389–428", 
                            "356–389",
                            "326–389", 
                            "257–326", 
                            "0–257"
                        ]
                    ]),

                    html.Tr([
                        html.Td("Risk Definition", style={"border": "1px solid gray", "padding": "6px", "textAlign": "left"})
                    ] + [
                        html.Td(defn, style={"border": "1px solid gray", "padding": "6px"}) for defn in [
                            "Negligible risk", "Very low risk", "Very low risk", "Very low risk",
                            "Low risk", "Low risk", "Low risk",
                            "Moderate risk", "Moderate risk", "Moderate risk",
                            "High risk", "High risk", "High risk",
                            "Very high risk", "Very high risk",
                            "Near default", "Near default", "Defaulted"
                        ]
                    ]),

                    html.Tr([
                        html.Td("Probability of Default", style={"border": "1px solid gray", "padding": "6px", "textAlign": "left"})
                    ] + [
                        html.Td(prob, style={"border": "1px solid gray", "padding": "6px"}) for prob in [
                            "0.36%", 
                            "0.50%", 
                            "0.70%", 
                            "0.98%", 
                            "1.36%", 
                            "1.90%", 
                            "2.64%", 
                            "3.68%",
                            "5.13%", 
                            "7.15%", 
                            "9.96%", 
                            "13.87%",
                            "19.32%",
                            "26.91%",
                            "37.48%",
                            "52.20%",
                            "72.71%",
                            "100%"
                        ]
                    ])
                ], style={
                    "width": "100%",
                    "borderCollapse": "collapse",
                    "textAlign": "center",
                    "fontFamily": "Arial, sans-serif",
                    "fontSize": "14px",
                    "marginBottom": "30px"
                })
            ], open=True)

,
            
            ############################### thanh ngăn tách
            html.Div([
                html.Span("Corporate Credit Risk Score", style={
                    "fontWeight": "bold", "fontSize": "16px"
                }),
                html.Span(title="The generic risk model has been developed and back-tested based on historical data from a dataset of over 2 million companies, encompassing both private and public entities across a wide range of industries.",
                    style={"marginLeft": "8px", "cursor": "pointer", "fontSize": "15px"})
            ], style={
                "backgroundColor": "#eee",
                "padding": "8px 15px",
                "borderLeft": "3px solid #888",
                "fontWeight": "bold",
                "marginTop": "30px",
                "marginBottom": "10px",
                "borderRadius": "10px",
                "fontSize": "20px"
            }),

            ############################### Score card + historical change
            html.Div([
                html.Div(id="score-summary", 
                         style={  "width": "450px",   # bằng với box kia
                                "height": "520px",  # cho bằng nhau
                                "padding": "20px",
                                "border": "1px solid #ddd",
                                "borderRadius": "10px",
                                "boxShadow": "0px 0px 12px rgba(0,0,0,0.15)",
                                "backgroundColor": "#fff"
                                }
                         ),
                
                
                ### HISTORICAL CHANGE  
                html.Div([
                    html.Div("Historical Change", style={
                        "fontWeight": "bold", "fontSize": "24px", "marginBottom": "10px","textAlign": "center",
                    }),

                    html.Div([
                        html.Span("From ", style={"marginRight": "10px", "fontSize": "18px","textAlign": "center","lineHeight": "38px"}),
                        dcc.Dropdown(id="from-year-dropdown", placeholder="Select...", style={"width": "100px", "display": "inline-block", "marginRight": "10px","textAlign": "center",}),
                        html.Span("to", style={"marginRight": "10px", "fontSize": "18px","textAlign": "center","lineHeight": "38px"}),
                        dcc.Dropdown(id="to-year-dropdown", placeholder="Select...", style={"width": "100px", "display": "inline-block", "marginRight": "10px","textAlign": "center",}),
                    ]
                    , style={
                             "display": "flex",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "marginBottom": "15px",
                            "marginTop": "10px"
                             }),

                    dcc.Graph(id="score-trend",config={"displayModeBar": True},style={"height": "420px"})  # Ép chiều cao và ẩn tràn)
                ], style={
                    "width": "1230px",   # bằng với box kia
                    "height": "520px",  # cho bằng nhau
                    "padding": "20px",
                    "border": "1px solid #ddd",
                    "borderRadius": "10px",
                    "boxShadow": "0px 0px 12px rgba(0,0,0,0.15)",
                    "backgroundColor": "#fff"
                })
            ], style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "flex-start",
                "gap": "20px",
                "marginTop": "30px",
                "height": "500px"
      
            }),
            
            
            ############################### Risk Component Analysis
            html.Div([
                html.Div("Risk Component Analysis", style={
                    "fontSize": "24px", "fontWeight": "bold", "marginBottom": "15px", "textAlign": "center"
                }),

                # Compare control
                html.Div([
                    dcc.Checklist(
                    # daq.ToggleSwitch(
                        id="compare-toggle",
                        options=[{"label": " Compare data", "value": "on"}],
                        value=[],
                        # value=False,
                        style={"fontSize": "18px", "marginRight": "30px"}
                    ),
                    html.Span("Base Period", style={"marginRight": "5px", "fontSize": "18px"}),
                    dcc.Dropdown(id="from-compare", placeholder="Select...", style={"width": "120px", "marginRight": "15px"}),
                    html.Span("Comparison Period", style={"marginRight": "5px", "fontSize": "18px"}),
                    dcc.Dropdown(id="to-compare", placeholder="Select...", style={"width": "120px"})
                ], style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "marginBottom": "15px",
                    "marginTop": "15px"
                })

                ,

                # Main content
                html.Div([
                    # Left column
                    html.Div([
                        html.Div([
                            html.Div("Score Breakdown", style={"fontWeight": "bold", "fontSize": "20px", "marginBottom": "10px" , "marginTop": "10px","textAlign": "center"}),
                            dcc.Graph(id="score-breakdown", style={"height": "350px"
                                                                   , "width": "100%", "marginTop": "10px"
                                                                   }),
                        ], style={
                            "padding": "20px",
                            "border": "1px solid #ccc",
                            "borderRadius": "10px",
                            "marginBottom": "20px",
                            "height": "450px",
                            "display": "flex",
                            "flexDirection": "column",
                            "justifyContent": "center"
                        }),

                        html.Div([
                            html.Div("Relative Contributions", style={"fontWeight": "bold", "fontSize": "20px", "marginBottom": "5px", "marginTop": "5px","textAlign": "center"}),
                            dcc.Graph(id="relative-contributions",responsive=True,config={"responsive": True},style={"height": "700px", "width": "100%", "marginTop": "5px"                                                                         
                                                                         }),

                        ], style={
                            "padding": "15px",
                            "border": "1px solid #ccc",
                            "borderRadius": "10px",
                            "height": "780px",
                            "display": "flex",
                            "flexDirection": "column",
                            "justifyContent": "center",
                             "overflowX": "auto",
                        })
                    ], style={"width": "49%"}),

                    # Right column
                    html.Div([
                        html.Div([
                            html.Div("Risk Drivers", style={
                                "fontWeight": "bold", "fontSize": "20px", "marginBottom": "10px","textAlign": "center", "borderBottom": "1px solid #ccc", "paddingBottom": "10px"
                            }),
                            # html.Div([
                            html.Div([
                                html.Div("Financial Risk", style={"fontWeight": "bold", "marginBottom": "8px", "fontSize": "18px" }),
                                html.Div(id="financial-risk-table", style={"marginTop": "15px", "fontSize": "17px"}),

                                # ✅ Dùng dynamic title cho Non-Financial Risk
                                html.Div(id="non-financial-risk-title", children="Non-Financial Risk", style={"fontWeight": "bold", "marginBottom": "8px", "fontSize": "18px"  }),
                                html.Div(id="non-financial-risk-table", style={"fontSize": "17px"})
                            ])

                        ], style={
                            "padding": "20px",
                            "border": "1px solid #ccc",
                            "borderRadius": "10px",
                            "height": "1280px",  # 350 + 30 margin + 350
                            "display": "flex",
                            "flexDirection": "column",
                            "justifyContent": "flex-start"
                        })
                    ], style={"width": "62%"})
                ], style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "gap": "30px"
                })
            ], style={
                "padding": "30px",
                "marginTop": "80px",
                "backgroundColor": "#fff",
                "border": "1px solid #ccc",
                "borderRadius": "10px",
                "boxShadow": "0px 0px 12px rgba(0,0,0,0.15)",
            })
,


            ############################### Commentary
            html.Div([
                html.Span("Commentary", style={
                    "fontSize": "24px", "fontWeight": "bold", "marginBottom": "15px", "textAlign": "center", "display": "block"
                }),
                html.Div(id="commentary-box", style={
                    "whiteSpace": "pre-line",  # Giữ xuống dòng trong Markdown/text
                    "fontSize": "20px"
                })
            ], style={
                "padding": "30px",
                "backgroundColor": "#fff",
                "border": "1px solid #ccc",
                "borderRadius": "10px",
                "boxShadow": "0px 0px 12px rgba(0,0,0,0.15)",
                "marginTop": "30px",
                "height": "300px",
                "overflowY": "auto"
            }),
            
            ############################### Probability of Default Term Structure
            ############################### Probability of Default Term Structure
            html.Div([
                html.Span("Probability of Default Term Structure", style={
                    "fontSize": "24px",
                    "fontWeight": "bold",
                    "marginBottom": "20px",
                    "textAlign": "center",
                    "display": "block"
                }),

                html.Div([
                    # Monthly Term Structure
                    html.Div([
                        html.Div("Monthly Term Structure", style={
                            "fontWeight": "bold", "marginBottom": "10px", "textAlign": "center", "fontSize": "18px",
                        }),
                        dash_table.DataTable(
                            id="monthly-pd-table",
                            columns=[{"name": f"{i+1} MONTH", "id": f"m{i+1}"} for i in range(12)],
                            data=[{f"m{i+1}": None for i in range(12)}],
                            style_cell={"textAlign": "center", "minWidth": "60px", "padding": "4px"},
                            style_header={"backgroundColor": "#d4edda", "fontWeight": "bold"},
                            style_data={"backgroundColor": "#f8fdf8"}
                        )
                    ], style={"width": "48%", "paddingRight": "1%"}),

                    # Vertical divider
                    html.Div(style={
                        "width": "2%", "borderLeft": "2px solid #ccc", "height": "100%"
                    }),

                    # Yearly Term Structure (3 bảng)
                    html.Div([
                        html.Div("Yearly Term Structure", style={
                            "fontWeight": "bold", "marginBottom": "10px", "textAlign": "center", "fontSize": "18px",
                        }),
                        html.Div([
                            dash_table.DataTable(
                                id="yearly-pd-table-1",
                                columns=[{"name": f"{i+1} YEAR", "id": f"y{i+1}"} for i in range(12)],
                                data=[{f"y{i+1}": None for i in range(12)}],
                                style_cell={"textAlign": "center", "minWidth": "60px", "padding": "4px"},
                                style_header={"backgroundColor": "#cce5ff", "fontWeight": "bold"},
                                style_data={"backgroundColor": "#f7fbff"},
                                style_table={"marginBottom": "1px"}
                            ),
                            dash_table.DataTable(
                                id="yearly-pd-table-2",
                                columns=[{"name": f"{i+13} YEAR", "id": f"y{i+13}"} for i in range(12)],
                                data=[{f"y{i+13}": None for i in range(12)}],
                                style_cell={"textAlign": "center", "minWidth": "60px", "padding": "4px"},
                                style_header={"backgroundColor": "#cce5ff", "fontWeight": "bold"},
                                style_data={"backgroundColor": "#f7fbff"},
                                style_table={"marginBottom": "1px"}
                            ),
                            dash_table.DataTable(
                                id="yearly-pd-table-3",
                                columns=[{"name": f"{i+25} YEAR", "id": f"y{i+25}"} for i in range(11)],
                                data=[{f"y{i+25}": None for i in range(11)}],
                                style_cell={"textAlign": "center", "minWidth": "60px", "padding": "4px"},
                                style_header={"backgroundColor": "#cce5ff", "fontWeight": "bold"},
                                style_data={"backgroundColor": "#f7fbff"},
                                style_table={"marginBottom": "0.5px"}
                            )
                        ])
                    ], style={"width": "48%", "paddingLeft": "1%"})
                ], style={"display": "flex", "width": "100%", "gap": "10px"})
            ], style={
                "padding": "30px",
                "backgroundColor": "#fff",
                "border": "1px solid #ccc",
                "borderRadius": "10px",
                "boxShadow": "0px 0px 12px rgba(0,0,0,0.15)",
                "marginTop": "30px",
                "height": "auto"
            })

            ,
            ############################### Distribution of Score  
            html.Div([
                html.Span("Distribution of Score", style={
                    "fontSize": "24px",
                    "fontWeight": "bold",
                    "marginBottom": "15px","marginTop": "25px",
                    "textAlign": "center",
                    "display": "block"
                }),

                # Lựa chọn chế độ phân phối
                dcc.RadioItems(
                    id="distribution-mode",
                    options=[
                        {"label": "By Model Segment", "value": "segment"},
                        {"label": "By Industry", "value": "industry"},
                        {"label": "By Company Size", "value": "size"},
                    ],
                    value="segment",  # mặc định
                    labelStyle={
                        "display": "inline-block",
                        "padding": "8px 16px",
                        "marginRight": "10px",
                        "border": "1px solid #ccc",
                        "borderRadius": "6px",
                        "cursor": "pointer",
                        "backgroundColor": "#f8f9fa",
                        "fontWeight": "500"
                    },
                    inputStyle={"marginRight": "6px"},
                    style={"marginBottom": "25px"}
                ),


                # ✅ Quan trọng: thêm biểu đồ vào đây
                dcc.Graph(
                    id="distribution-chart",
                    config={"displayModeBar": False},
                    style={"height": "400px","marginBottom": "20px",}
                ),
                
                html.Div(id="distribution-info", style={
                        "textAlign": "left", "fontSize": "18px", "marginTop": "20px",
                        "padding": "10px", "backgroundColor": "white",
                        "border": "1px solid #ccc", "borderRadius": "10px"
                    })
                               

                ], style={  
                "backgroundColor": "#fff",
                "border": "1px solid #ccc",
                "borderRadius": "10px",
                "boxShadow": "0px 0px 12px rgba(0,0,0,0.15)",
                "marginTop": "20px",
                "overflowY": "auto",
                "height": "750px",
                "textAlign": "center"
            })
                        
            ,
                    
        ], style={
            "maxWidth": "1800px",
            "marginLeft": "auto",
            "marginRight": "auto",
            "padding": "0",
            # "margin": "0"
        })
    ] )
