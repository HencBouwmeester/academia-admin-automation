# -*- coding: utf-8 -*-

import dash
import pandas as pd
import io
from dash import html, dcc, dash_table, Input, Output, State, ClientsideFunction
import plotly.io as pio
import dash_bootstrap_components as dbc

from utils import *

DEBUG = False

pio.templates.default = "plotly_white"

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    prevent_initial_callbacks=True,
    requests_pathname_prefix="/dashboard/",
    routes_pathname_prefix="/dashboard/",
)

server = app.server
app.title = "Schedule and Metrics Portal"
app.config.update({"suppress_callback_exceptions": True})

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

app.layout = html.Div(
    [
        dcc.Store(id="browser-data-cache", data=[]),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Img(
                                    id="msudenver-logo",
                                    src=app.get_asset_url("msudenver-logo.png"),
                                    style={
                                        "height": "36px",
                                        "marginRight": "16px",
                                        "display": "inline-block",
                                        "verticalAlign": "middle",
                                    },
                                ),
                                html.H1(
                                    children=["Schedule & Enrollment Metrics Portal"],
                                    id="main-dashboard-header",
                                    style={
                                        "display": "inline-block",
                                        "margin": "0",
                                        "fontSize": "2.4rem",
                                        "fontWeight": "300",
                                        "color": "#0f172a",
                                        "verticalAlign": "middle",
                                    },
                                ),
                            ],
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        dcc.Upload(
                            id="upload-data",
                            children=html.Button(
                                ["Upload File (Text or Excel)"],
                                id="upload-data-button",
                                n_clicks=0,
                                className="btn-primary",
                            ),
                            multiple=False,
                            accept=".txt, .xlsx, .xls",
                        ),
                    ],
                    id="header",
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "padding": "20px 0",
                        "borderBottom": "1px solid #e2e8f0",
                        "marginBottom": "24px",
                    },
                ),
                html.Div(
                    [
                        dcc.Tabs(
                            id="main-dashboard-tabs",
                            value="tab-analytics-plots",
                            children=[
                                dcc.Tab(
                                    label="📊 Metrics & Plots View",
                                    value="tab-analytics-plots",
                                    id="analytics-plots-tab-container",
                                    children=[
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.Div(
                                                                    [
                                                                        html.Div(
                                                                            [
                                                                                html.P(
                                                                                    "Sections"
                                                                                ),
                                                                                html.H6(
                                                                                    "0",
                                                                                    id="total_sections_text",
                                                                                ),
                                                                            ],
                                                                            id="sections",
                                                                            className="mini_container",
                                                                        ),
                                                                        html.Div(
                                                                            [
                                                                                html.P(
                                                                                    "Courses"
                                                                                ),
                                                                                html.H6(
                                                                                    "0",
                                                                                    id="total_courses_text",
                                                                                ),
                                                                            ],
                                                                            id="total_courses",
                                                                            className="mini_container",
                                                                        ),
                                                                        html.Div(
                                                                            [
                                                                                html.P(
                                                                                    "Credits"
                                                                                ),
                                                                                html.H6(
                                                                                    "0",
                                                                                    id="total_credits_text",
                                                                                ),
                                                                            ],
                                                                            id="total_credits",
                                                                            className="mini_container",
                                                                        ),
                                                                        html.Div(
                                                                            [
                                                                                html.P(
                                                                                    "Enrollment"
                                                                                ),
                                                                                html.H6(
                                                                                    "0.00",
                                                                                    id="total_enrollment_text",
                                                                                ),
                                                                            ],
                                                                            id="total_enrollment",
                                                                            className="mini_container",
                                                                        ),
                                                                        html.Div(
                                                                            [
                                                                                html.P(
                                                                                    "CHP"
                                                                                ),
                                                                                html.H6(
                                                                                    "0",
                                                                                    id="total_CHP_text",
                                                                                ),
                                                                            ],
                                                                            id="total_CHP",
                                                                            className="mini_container",
                                                                        ),
                                                                        html.Div(
                                                                            [
                                                                                html.P(
                                                                                    "Average Enrollment by CRN"
                                                                                ),
                                                                                html.H6(
                                                                                    "0.0",
                                                                                    id="avg_enrollment_text",
                                                                                ),
                                                                            ],
                                                                            id="avg_enrollment",
                                                                            className="mini_container",
                                                                        ),
                                                                        html.Div(
                                                                            [
                                                                                html.P(
                                                                                    "Average Fill Rate"
                                                                                ),
                                                                                html.H6(
                                                                                    "0.00%",
                                                                                    id="avg_fill_rate_text",
                                                                                ),
                                                                            ],
                                                                            id="avg_fill_rate",
                                                                            className="mini_container",
                                                                        ),
                                                                        html.Div(
                                                                            [
                                                                                html.P(
                                                                                    "Average Waitlist"
                                                                                ),
                                                                                html.H6(
                                                                                    "0.00",
                                                                                    id="avg_waitlist_text",
                                                                                ),
                                                                            ],
                                                                            id="avg_waitlist",
                                                                            className="mini_container",
                                                                        ),
                                                                    ],
                                                                    style={
                                                                        "display": "flex",
                                                                        "flexWrap": "wrap",
                                                                        "marginTop": "15px",
                                                                    },
                                                                ),
                                                            ],
                                                            className="pretty_container twelve columns",
                                                        ),
                                                    ],
                                                    className="row flex-display",
                                                ),
                                                html.Div(
                                                    [
                                                        # HELPER GENERATOR TO AVOID REPETITIVE CODE
                                                        *[
                                                            html.Div(
                                                                [
                                                                    html.H6(
                                                                        f"{split_label}",
                                                                        className="control_label",
                                                                        style={
                                                                            "textAlign": "center",
                                                                            "marginBottom": "10px",
                                                                        },
                                                                    ),
                                                                    html.Table(
                                                                        [
                                                                            html.Tbody(
                                                                                [
                                                                                    html.Tr(
                                                                                        [
                                                                                            html.Td("Sections:"),
                                                                                            html.Td(
                                                                                                "0",
                                                                                                id=f"{split_id}_sections",
                                                                                                style={
                                                                                                    "textAlign": "right",
                                                                                                },
                                                                                            ),
                                                                                        ]
                                                                                    ),
                                                                                    html.Tr(
                                                                                        [
                                                                                            html.Td("Courses:"),
                                                                                            html.Td(
                                                                                                "0",
                                                                                                id=f"{split_id}_courses",
                                                                                                style={
                                                                                                    "textAlign": "right",
                                                                                                },
                                                                                            ),
                                                                                        ]
                                                                                    ),
                                                                                    html.Tr(
                                                                                        [
                                                                                            html.Td("Waitlist:"),
                                                                                            html.Td(
                                                                                                "0",
                                                                                                id=f"{split_id}_wlst",
                                                                                                style={
                                                                                                    "textAlign": "right",
                                                                                                },
                                                                                            ),
                                                                                        ]
                                                                                    ),
                                                                                    html.Tr(
                                                                                        [
                                                                                            html.Td("Total Enrl:"),
                                                                                            html.Td(
                                                                                                "0",
                                                                                                id=f"{split_id}_total_enrl",
                                                                                                style={
                                                                                                    "textAlign": "right",
                                                                                                },
                                                                                            ),
                                                                                        ]
                                                                                    ),
                                                                                    html.Tr(
                                                                                        [
                                                                                            html.Td("Min:"),
                                                                                            html.Td(
                                                                                                "0",
                                                                                                id=f"{split_id}_min_enrl",
                                                                                                style={
                                                                                                    "textAlign": "right",
                                                                                                },
                                                                                            ),
                                                                                        ]
                                                                                    ),
                                                                                    html.Tr(
                                                                                        [
                                                                                            html.Td("Mean:"),
                                                                                            html.Td(
                                                                                                "0.0",
                                                                                                id=f"{split_id}_avg_enrl",
                                                                                                style={
                                                                                                    "textAlign": "right",
                                                                                                },
                                                                                            ),
                                                                                        ]
                                                                                    ),
                                                                                    html.Tr(
                                                                                        [
                                                                                            html.Td("CHP:"),
                                                                                            html.Td(
                                                                                                "0",
                                                                                                id=f"{split_id}_total_chp",
                                                                                                style={
                                                                                                    "textAlign": "right",
                                                                                                },
                                                                                            ),
                                                                                        ]
                                                                                    ),
                                                                                ]
                                                                            )
                                                                        ],
                                                                        style={
                                                                            "width": "100%",
                                                                            "marginBottom": "10px",
                                                                            "lineHeight": "1.4",
                                                                        },
                                                                    ),
                                                                    dcc.Graph(
                                                                        id=f"{split_id}_mini_graph",
                                                                        config={
                                                                            "displayModeBar": False,
                                                                            "staticPlot": False,
                                                                        },
                                                                        style={
                                                                            "height": "45px",
                                                                            "width": "100%",
                                                                        },
                                                                    ),
                                                                ],
                                                                className="mini_container",
                                                                style={
                                                                    "flex": "1",
                                                                    "margin": "0 5px",
                                                                    "padding": "10px",
                                                                    "minWidth": "140px",
                                                                },
                                                            )
                                                            for split_label, split_id in [
                                                                ("Lab", "lab"),
                                                                ("1000 Level", "lvl1"),
                                                                ("2000 Level", "lvl2"),
                                                                ("3000 Level", "lvl3"),
                                                                ("4000 Level", "lvl4"),
                                                                ("Total View", "tot"),
                                                            ]
                                                        ]
                                                    ],
                                                    className="row flex-display pretty_container",
                                                    id="calc_row",
                                                    style={
                                                        "display": "flex",
                                                        "flexWrap": "wrap",
                                                        "justifyContent": "space-between",
                                                        "padding": "15px",
                                                    },
                                                ),
                                                html.Div(
                                                    [
                                                        html.H6(
                                                            "Notes for breakout metrics:"
                                                        ),
                                                        html.Ul(
                                                            [
                                                                html.Li(
                                                                    "Lab enrollments, marked with an 'L' in the datatable, are not included in Total calculations."
                                                                ),
                                                                html.Li(
                                                                    "Enrollments, marked with an 'N' in the datatable, are not included in any calculations."
                                                                ),
                                                                html.Li(
                                                                    "5000 level courses are only included in the Total calculations."
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                    id="notes_enrollment",
                                                    style={"padding": "10px 20px"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                dcc.Graph(
                                                                    figure=blankFigure(),
                                                                    id="max_v_enrl_by_crn_graph",
                                                                )
                                                            ],
                                                            className="pretty_container six columns",
                                                        ),
                                                        html.Div(
                                                            [
                                                                dcc.Graph(
                                                                    figure=blankFigure(),
                                                                    id="max_v_enrl_by_course_graph",
                                                                )
                                                            ],
                                                            className="pretty_container six columns",
                                                        ),
                                                    ],
                                                    className="row flex-display",
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.H6(
                                                                    "Enrollment by Instructor"
                                                                ),
                                                                dash_table.DataTable(
                                                                    id="enrl_by_instructor_table",
                                                                    columns=[
                                                                        {
                                                                            "name": i,
                                                                            "id": i,
                                                                        }
                                                                        for i in [
                                                                            "Instructor",
                                                                            "Total",
                                                                            "Avg",
                                                                        ]
                                                                    ],
                                                                    data=[],
                                                                    fixed_rows={
                                                                        "headers": True
                                                                    },
                                                                    style_table={
                                                                        "height": "400px",
                                                                        "overflowY": "auto",
                                                                    },
                                                                    sort_action="native",
                                                                    style_header={
                                                                        "backgroundColor": "rgb(230, 230, 230)",
                                                                        "fontWeight": "bold",
                                                                    },
                                                                    style_cell={
                                                                        "fontFamily": "sans-serif",
                                                                        "fontSize": "1.5rem",
                                                                        "textAlign": "left",
                                                                    },
                                                                    style_cell_conditional=[
                                                                        {
                                                                            "if": {
                                                                                "column_id": [
                                                                                    "Total",
                                                                                    "Avg",
                                                                                ]
                                                                            },
                                                                            "textAlign": "right",
                                                                        }
                                                                    ],
                                                                ),
                                                            ],
                                                            className="pretty_container four columns",
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.H6(
                                                                    "Course CHP and Enrollment"
                                                                ),
                                                                dash_table.DataTable(
                                                                    id="chp_by_course_table",
                                                                    columns=[
                                                                        {
                                                                            "name": i,
                                                                            "id": i,
                                                                        }
                                                                        for i in [
                                                                            "Course",
                                                                            "CHP",
                                                                            "Enrolled",
                                                                            "Max",
                                                                        ]
                                                                    ],
                                                                    data=[],
                                                                    fixed_rows={
                                                                        "headers": True
                                                                    },
                                                                    style_table={
                                                                        "height": "400px",
                                                                        "overflowY": "auto",
                                                                    },
                                                                    sort_action="native",
                                                                    style_header={
                                                                        "backgroundColor": "rgb(230, 230, 230)",
                                                                        "fontWeight": "bold",
                                                                    },
                                                                    style_cell={
                                                                        "fontFamily": "sans-serif",
                                                                        "fontSize": "1.5rem",
                                                                        "textAlign": "left",
                                                                    },
                                                                    style_cell_conditional=[
                                                                        {
                                                                            "if": {
                                                                                "column_id": [
                                                                                    "CHP",
                                                                                    "Enrolled",
                                                                                    "Max",
                                                                                ]
                                                                            },
                                                                            "textAlign": "right",
                                                                        }
                                                                    ],
                                                                ),
                                                            ],
                                                            className="pretty_container four columns",
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.H6(
                                                                    "Max Ratios",
                                                                    id="f2f-dynamic-title-header",
                                                                    style={
                                                                        "textAlign": "center",
                                                                        "marginBottom": "0px",
                                                                    },
                                                                ),
                                                                dcc.Graph(
                                                                    figure=blankFigure(),
                                                                    id="graph_f2f",
                                                                    style={
                                                                        "height": "270px",
                                                                        "width": "100%",
                                                                    },
                                                                    config={
                                                                        "displayModeBar": False
                                                                    },
                                                                ),
                                                                html.Label(
                                                                    [
                                                                        "Enrollment Split View:",
                                                                        dcc.RadioItems(
                                                                            id="enrollment-max-actual",
                                                                            options=[
                                                                                {
                                                                                    "label": "Max",
                                                                                    "value": "Max",
                                                                                },
                                                                                {
                                                                                    "label": "Actual",
                                                                                    "value": "Enrolled",
                                                                                },
                                                                                {
                                                                                    "label": "Sections",
                                                                                    "value": "Section",
                                                                                },
                                                                            ],
                                                                            labelStyle={
                                                                                "display": "inline-block",
                                                                                "marginRight": "10px",
                                                                            },
                                                                            className="dcc_control",
                                                                            value="Max",
                                                                        ),
                                                                    ]
                                                                ),
                                                            ],
                                                            className="pretty_container four columns",
                                                        ),
                                                    ],
                                                    className="row flex-display",
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                dcc.Graph(
                                                                    figure=blankFigure(),
                                                                    id="enrl_by_instructor_graph",
                                                                )
                                                            ],
                                                            className="pretty_container six columns",
                                                        ),
                                                        html.Div(
                                                            [
                                                                dcc.Graph(
                                                                    figure=blankFigure(),
                                                                    id="chp_by_course_graph",
                                                                )
                                                            ],
                                                            className="pretty_container six columns",
                                                        ),
                                                    ],
                                                    className="row flex-display",
                                                ),
                                            ],
                                            className="control-card",
                                        ),
                                    ],
                                ),
                                dcc.Tab(
                                    label="📅 Weekday Schedule Grid",
                                    value="tab-schedule-grid",
                                    children=[
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        dcc.Tabs(
                                                            [
                                                                generate_weekday_tab(
                                                                    day
                                                                )
                                                                for day in days
                                                            ],
                                                            id="weekdays-tabs",
                                                            value="tab-mon",
                                                            style={"height": "40px"},
                                                        )
                                                    ],
                                                    style={
                                                        "borderBottom": "1px solid #e2e8f0",
                                                        "marginBottom": "16px",
                                                        "marginTop": "20px",
                                                    },
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                generate_tab_fig(
                                                                    day, "tab-mon", None
                                                                )
                                                                for day in days
                                                            ],
                                                            id="weekdays-tabs-content",
                                                            style={
                                                                "width": "100%",
                                                                "background": "white",
                                                            },
                                                        ),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.Button(
                                                                    "Update Grid",
                                                                    id="update-grid-button",
                                                                    n_clicks=0,
                                                                    className="btn-primary",
                                                                    style={
                                                                        "marginRight": "8px"
                                                                    },
                                                                ),
                                                                html.Button(
                                                                    "+ Add Row Record",
                                                                    id="add-row-button",
                                                                    n_clicks=0,
                                                                    className="btn-secondary",
                                                                    style={
                                                                        "marginRight": "8px",
                                                                        "color": "#ffffff",
                                                                        "background-color": "#16a34a",
                                                                        "borderColor": "#bbf7d0",
                                                                    },
                                                                ),
                                                                html.Button(
                                                                    "Delete Row(s)",
                                                                    id="delete-rows-button",
                                                                    n_clicks=0,
                                                                    className="btn-danger",
                                                                    style={
                                                                        "marginRight": "8px"
                                                                    },
                                                                ),
                                                            ],
                                                            style={
                                                                "display": "flex",
                                                                "flexWrap": "wrap",
                                                                "alignItems": "center",
                                                            },
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.Button(
                                                                    "Reset Highlights",
                                                                    id="reset-colors-button",
                                                                    n_clicks=0,
                                                                    className="btn-secondary",
                                                                    style={
                                                                        "marginRight": "8px"
                                                                    },
                                                                ),
                                                                dcc.Dropdown(
                                                                    id="color-select",
                                                                    options=[
                                                                        {
                                                                            "label": "Blue Accent",
                                                                            "value": "#b3cde3",
                                                                        },
                                                                        {
                                                                            "label": "Red Accent",
                                                                            "value": "#fbb4ae",
                                                                        },
                                                                        {
                                                                            "label": "Green Accent",
                                                                            "value": "#ccebc5",
                                                                        },
                                                                        {
                                                                            "label": "Purple Accent",
                                                                            "value": "#decbe4",
                                                                        },
                                                                        {
                                                                            "label": "Orange Accent",
                                                                            "value": "#fed9a6",
                                                                        },
                                                                        {
                                                                            "label": "Yellow Accent",
                                                                            "value": "#ffffcc",
                                                                        },
                                                                        {
                                                                            "label": "Tan Accent",
                                                                            "value": "#e5d8bd",
                                                                        },
                                                                        {
                                                                            "label": "Pink Accent",
                                                                            "value": "#fddaec",
                                                                        },
                                                                        {
                                                                            "label": "Muted Gray",
                                                                            "value": "#f2f2f2",
                                                                        },
                                                                    ],
                                                                    value="#b3cde3",
                                                                    clearable=False,
                                                                    className="custom-dropdown",
                                                                ),
                                                            ],
                                                            style={
                                                                "display": "flex",
                                                                "flexWrap": "wrap",
                                                                "alignItems": "center",
                                                            },
                                                        ),
                                                    ],
                                                    style={
                                                        "display": "flex",
                                                        "justifyContent": "space-between",
                                                        "alignItems": "center",
                                                        "marginBottom": "20px",
                                                        "background": "#f8fafc",
                                                        "padding": "14px",
                                                        "borderRadius": "8px",
                                                        "border": "1px solid #e2e8f0",
                                                    },
                                                ),
                                            ],
                                            className="control-card",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            [
                                html.P(
                                    "Datatable Queries",
                                    style={"fontSize": "2.0rem"},
                                    # className="section-title",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                dcc.Dropdown(
                                                    id="filter-query-dropdown",
                                                    options=[
                                                        {
                                                            "label": "Custom Expression Filter...",
                                                            "value": "custom",
                                                        },
                                                        {
                                                            "label": "Active Math Classes",
                                                            "value": "{S} contains A",
                                                        },
                                                        {
                                                            "label": "Math w/o Labs",
                                                            "value": '{Subject} contains M && {S} contains A && ({Number} < 1081 || {Number} > 1082) && ({Number} != "1101") && ({Number} != "1111") && ({Number} < 1115 || {Number} > 1116) && ({Number} < 1311 || {Number} > 1312)',
                                                        },
                                                        {
                                                            "label": "Math Labs",
                                                            "value": "{Subject} contains M && {S} contains A && ({Number} = 1082 || {Number} = 1101 || {Number} = 1116 || {Number} = 1312)",
                                                        },
                                                        {
                                                            "label": "Math Labs with Parents",
                                                            "value": "{Subject} contains M && {S} contains A && ({Number} = 1081 || {Number} = 1111 || {Number} = 1115 || {Number} = 1311 || {Number} = 1082 || {Number} = 1101 || {Number} = 1116 || {Number} = 1312)",
                                                        },
                                                        {
                                                            "label": "Math Lower Division",
                                                            "value": "{Subject} contains M && {Number} < 3000 && {S} contains A",
                                                        },
                                                        {
                                                            "label": "Math Upper Division",
                                                            "value": "{Subject} contains M && {Number} >= 3000 && {S} contains A",
                                                        },
                                                        {
                                                            "label": "Applied Group",
                                                            "value": "{Subject} contains M && {S} contains A && ({Number} = 3130 || {Number} = 3400 || {Number} = 3420 || {Number} = 3430 || {Number} = 3440 || {Number} = 4480 || {Number} = 4490)",
                                                        },
                                                        {
                                                            "label": "MathEd Group",
                                                            "value": "({S} contains A && {Subject} contains M && ({Number} = 1610 || {Number} = 2620 || {Number} = 3470 || {Number} = 3640 || {Number} = 3650)) || ({S} contains A && {Subject} contains MTL)",
                                                        },
                                                        {
                                                            "label": "Statistics Group",
                                                            "value": "{Subject} contains M && {S} contains A && ({Number} = 3210 || {Number} = 3220 || {Number} = 3230 || {Number} = 3240 || {Number} = 3270 || {Number} = 3510 || {Number} = 4210 || {Number} = 4230 || {Number} = 4250 || {Number} = 4290)",
                                                        },
                                                        {
                                                            "label": "Theoretical Group",
                                                            "value": "{Subject} contains M && {S} contains A && ({Number} = 3100 || {Number} = 3110 || {Number} = 3170 || {Number} = 3140 || {Number} = 4110 || {Number} = 4150 || {Number} = 4410 || {Number} = 4420 || {Number} = 4450)",
                                                        },
                                                        {
                                                            "label": "Canceled CRNs",
                                                            "value": "{S} contains C",
                                                        },
                                                    ],
                                                    placeholder="Select a baseline preset query rule",
                                                    value="",
                                                    className="custom-dropdown",
                                                ),
                                            ],
                                            style={
                                                "flexGrow": "1",
                                                "marginRight": "12px",
                                            },
                                        ),
                                        html.Button(
                                            "Apply Expression Rule",
                                            id="apply_query_button",
                                            className="btn-primary",
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "width": "100%",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        dcc.Input(
                                                            id="filter-query-input",
                                                            placeholder='syntax template: {Subject} contains "MTH" && {Number} >= 3000',
                                                            className="custom-input",
                                                            style={
                                                                "width": "100%",
                                                                "boxSizing": "border-box",
                                                            },
                                                        ),
                                                    ],
                                                    id="filter-query-input-container",
                                                    style={
                                                        "width": "100%",
                                                        "display": "none",
                                                    },
                                                ),
                                                html.Div(
                                                    ['filter_query = "None"'],
                                                    id="filter-query-output",
                                                    style={
                                                        "width": "100%",
                                                        # "fontSize": "1.05rem",
                                                        # "color": "#64748b",
                                                        "fontFamily": "sans-serif",
                                                        # "backgroundColor": "#f8fafc",
                                                        # "padding": "10px 14px",
                                                        # "borderRadius": "6px",
                                                        # "border": "1px dashed #cbd5e1",
                                                        # "marginTop": "12px",
                                                    },
                                                ),
                                            ],
                                            style={"width": "100%"},
                                        )
                                    ]
                                ),
                            ],
                            className="control-card",
                        ),
                        html.Div(
                            [
                                html.P(
                                    "Active Datatable Controls",
                                    style={"fontSize": "2.0rem"},
                                    # className="section-title",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Button(
                                                    "Export Excel (All)",
                                                    id="export-all-button",
                                                    n_clicks=0,
                                                    className="btn-secondary",
                                                    style={"marginRight": "8px"},
                                                ),
                                                html.Button(
                                                    "Export Excel (Filtered)",
                                                    id="export-filtered-button",
                                                    n_clicks=0,
                                                    className="btn-secondary",
                                                    style={"marginRight": "8px"},
                                                ),
                                                html.Button(
                                                    "Export Excel (Stacked)",
                                                    id="export-stacked-button",
                                                    n_clicks=0,
                                                    className="btn-secondary",
                                                    style={"marginRight": "8px"},
                                                ),
                                                dcc.Download(id="datatable-download"),
                                                dbc.Button(
                                                    "Export PDF (Instructor)",
                                                    id="btn-pdf-instructor",
                                                    className="btn-secondary",
                                                    style={"marginRight": "8px"},
                                                ),
                                                dbc.Button(
                                                    "Export PDF (Course)",
                                                    id="btn-pdf-course",
                                                    className="btn-secondary",
                                                    style={"marginRight": "8px"},
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "flexDirection": "row",
                                                "alignItems": "center",
                                                "whiteSpace": "nowrap",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "justifyContent": "space-between",
                                        "alignItems": "center",
                                        "marginBottom": "20px",
                                        "background": "#f8fafc",
                                        "padding": "14px",
                                        "borderRadius": "8px",
                                        "border": "1px solid #e2e8f0",
                                    },
                                ),
                                dcc.Download(id="download-pdf-channel"),
                                html.Div(
                                    id="datatable-interactivity-container",
                                    children=dash_table.DataTable(
                                        id="datatable-interactivity",
                                        columns=[
                                            {"id": "Subject", "name": "Subj"},
                                            {"id": "Number", "name": "Nmbr"},
                                            {"id": "CRN", "name": "CRN"},
                                            {"id": "Section", "name": "Sec"},
                                            {"id": "S", "name": "S"},
                                            {"id": "Campus", "name": "Cam"},
                                            {"id": "T", "name": "T"},
                                            {"id": "Title", "name": "Title"},
                                            {"id": "Credit", "name": "Credit", "type": "numeric"},
                                            {"id": "Max", "name": "Max", "type": "numeric"},
                                            {"id": "Enrolled", "name": "Enrl", "type": "numeric"},
                                            {"id": "WCap", "name": "WCap", "type": "numeric"},
                                            {"id": "WLst", "name": "WLst", "type": "numeric"},
                                            {"id": "Days", "name": "Days"},
                                            {"id": "Time", "name": "Time"},
                                            {"id": "Loc", "name": "Loc"},
                                            {"id": "Rcap", "name": "Rcap", "type": "numeric"},
                                            {"id": "%Ful", "name": "%Ful", "type": "numeric"},
                                            {"id": "Instructor", "name": "Instructor"},
                                            {"id": "Begin/End", "name": "Begin/End"},
                                            {"id": "CHP", "name": "CHP", "type": "numeric"},
                                            {"id": "Ratio", "name": "Ratio", "type": "numeric"},
                                            {"id": "Calc", "name": "Calc"},
                                            {"id": "Course", "name": "Course"},
                                            {"id": "colorRec", "name": "colorRec"},
                                            {"id": "SortKey", "name": "SortKey"},
                                        ],
                                        data=[],
                                        editable=True,
                                        row_selectable="multi",
                                        selected_rows=[],
                                        filter_action="native",
                                        sort_action="native",
                                        sort_mode="multi",
                                        fixed_rows={'headers': True, 'data': 0},
                                        style_header={
                                            "backgroundColor": "rgb(230, 230, 230)",
                                            "fontWeight": "bold",
                                        },
                                        style_cell={
                                            "fontFamily": "sans-serif",
                                            "fontSize": "1.5rem",
                                            "textAlign": "left",
                                            "minWidth": "30px",
                                            "paddingTop": "2px",
                                            "paddingBottom": "2px",
                                            "paddingLeft": "8px",
                                            "paddingRight": "8px",
                                        },
                                        style_data={
                                            "whiteSpace": "nowrap",
                                            "height": "auto",
                                        },
                                        style_table={
                                            "height": "600px",
                                            # "overflowY": "auto",
                                            "overflowX": "auto",
                                            "minWidth": "100%",
                                        },
                                        style_cell_conditional=[
                                            {
                                                "if": {
                                                    "column_id": [
                                                        "Credit",
                                                        "Max",
                                                        "Enrolled",
                                                        "WCap",
                                                        "WLst",
                                                        "Rcap",
                                                        "%Ful",
                                                        "CHP",
                                                        "Ratio",
                                                    ]
                                                },
                                                "textAlign": "right",
                                            }
                                        ],
                                        style_data_conditional=[
                                            {
                                                "if": {
                                                    "column_id": "colorRec",
                                                },
                                                "fontWeight": "bold",
                                                "color": "transparent",
                                            }
                                        ],
                                    ),
                                    style={
                                        "width": "100%",
                                        "display": "block",
                                        "borderRadius": "8px",
                                        "overflow": "hidden",
                                        "border": "1px solid #e2e8f0",
                                    },
                                ),
                            ],
                            className="control-card",
                        ),
                    ],
                    id="output-data-upload",
                    style={"display": "none"},
                ),
            ],
            style={
                "maxWidth": "1440px",
                "width": "95%",
                "margin": "0 auto",
                "paddingBottom": "60px",
            },
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flexDirection": "column"},
)


@app.callback(
    [
        Output("browser-data-cache", "data"),
        Output("datatable-interactivity", "data", allow_duplicate=True),
        Output("output-data-upload", "style"),
        Output("main-dashboard-header", "children"),
    ],
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def execute_initial_server_ingest(contents, filename):
    if contents is None:
        return dash.no_update, dash.no_update, {"display": "block"}

    df = parse_contents_integrated(contents, filename)
    df["colorRec"] = "#b3cde3"
    df = apply_co_requisite_sorting_keys(df)
    df = df.sort_values(by=["SortKey"], ascending=True)

    sorted_columns = [
        "Subject",
        "Number",
        "CRN",
        "Section",
        "S",
        "Campus",
        "T",
        "Title",
        "Credit",
        "Max",
        "Enrolled",
        "WCap",
        "WLst",
        "Days",
        "Time",
        "Loc",
        "Rcap",
        "%Ful",
        "Instructor",
        "Begin/End",
        "CHP",
        "Ratio",
        "Calc",
        "Course",
        "colorRec",
        "SortKey",
    ]
    df = df[sorted_columns].copy()

    records = df.to_dict("records")

    header_children = [
        f"Schedule & Enrollment Metrics Portal ({detect_academic_term(df)})"
    ]
    return dash.no_update, records, {"display": "block"}, header_children


app.clientside_callback(
    """
    function(addClicks, deleteClicks, resetClicks, dropdownValue,
              tableData, virtualIndices, selectedRowIndices) {
        const context = dash_clientside.callback_context.triggered;
        // Safety block: Exit cleanly if no active browser interaction occurred
        if (!context || context.length === 0 || !context[0].prop_id) {
            return window.dash_clientside.no_update;
        }

        // Extract the string text from the first slot object of the context tracker array
        const parts = context[0].prop_id.split('.');
        const triggerId = parts[0]; // Resolves cleanly to 'color-select', 'add-row-button', etc.

        let data = tableData ? [...tableData] : [];

        // Determine target indices based on the specific action
        let targetRealIndexes = [];

        if (triggerId === 'color-select') {
            // Target ALL filtered/visible row indices on screen instead of checkbox selections
            if (virtualIndices && virtualIndices.length > 0) {
                targetRealIndexes = [...virtualIndices];
            } else {
                // Fallback to all data if virtual indices aren't generated yet
                targetRealIndexes = data.map((_, i) => i);
            }
        } else {
            // For Delete Button operations, preserve standard checkbox selections
            if (virtualIndices && selectedRowIndices && selectedRowIndices.length > 0) {
                targetRealIndexes = selectedRowIndices.map(vIdx => virtualIndices[vIdx]);
            } else {
                targetRealIndexes = selectedRowIndices || [];
            }
        }

        // Sort indices descending to prevent array splicing offset shifts during deletions
        targetRealIndexes.sort((a, b) => b - a);

        if (triggerId === 'add-row-button') {
            const tempCRN = "TEMP_" + Math.floor(10000 + Math.random() * 90000);
            data.push({
                'Subject': '', 'Number': '', 'CRN': tempCRN, 'Section': '', 'S': 'A',
                'Campus': '', 'T': '', 'Title': '', 'Credit': '', 'Max': '', 'Enrolled': '',
                'WCap': '', 'WLst': '', 'Days': '', 'Time': '', 'Loc': 'TBA', 'Rcap': '',
                '%Ful': '', 'Begin/End': '', 'Instructor': ',', 'CHP': '', 'Ratio': '',
                'Calc': '', 'Course': '', 'colorRec': '#b3cde3', 'SortKey': 99999
            });
        } else if (triggerId === 'delete-rows-button' && targetRealIndexes.length > 0) {
            targetRealIndexes.forEach(idx => { if (idx < data.length) data.splice(idx, 1); });
        } else if (triggerId === 'reset-colors-button') {
            // Bulk reset every row back to default blue
            data.forEach(row => row['colorRec'] = '#b3cde3');
        } else if (triggerId === 'color-select') {
            if (targetRealIndexes.length === 0) return window.dash_clientside.no_update;

            // Apply the chosen color to all target row records instantly
            targetRealIndexes.forEach(idx => {
                if (data[idx] !== undefined && data[idx] !== null) {
                    data[idx]['colorRec'] = dropdownValue;

                    if (!data[idx]['CRN'] || String(data[idx]['CRN']).trim() === "") {
                        data[idx]['CRN'] = "TEMP_" + Math.floor(10000 + Math.random() * 90000);
                    }
                }
            });
        }

        return data;
    }
    """,
    Output("datatable-interactivity", "data", allow_duplicate=True),
    [
        Input("add-row-button", "n_clicks"),
        Input("delete-rows-button", "n_clicks"),
        Input("reset-colors-button", "n_clicks"),
        Input("color-select", "value"),
    ],
    [
        State("datatable-interactivity", "data"),
        State("datatable-interactivity", "derived_virtual_indices"),
        State("datatable-interactivity", "derived_virtual_selected_rows"),
    ],
    prevent_initial_call=True,
)


# // --- COPY AND PASTE THIS POPUP SNIPPET HERE ---
# const rawTrigger = dash_clientside.callback_context.triggered;
# const triggerSummary = (rawTrigger && rawTrigger.length > 0)
# ? "Trigger ID: " + rawTrigger[0].prop_id
# : "No Trigger Found";

# alert("🚨 Callback Triggered!\\n" + triggerSummary + "\\nSelected Indices: " + selectedRowIndices);
# // ----------------------------------------------


app.clientside_callback(
    """
    function(selectedColor, tableData, virtualIndices, selectedRowIndices, currentStyles) {
        if (!selectedColor || !tableData) return window.dash_clientside.no_update;

        let baseStyles = currentStyles ? [...currentStyles] : [
            { 'if': { 'column_id': 'colorRec' }, 'color': 'rgba(0,0,0,0)' }
        ];

        let targetRealIndexes = [];
        if (virtualIndices && selectedRowIndices && selectedRowIndices.length > 0) {
            targetRealIndexes = selectedRowIndices.map(vIdx => virtualIndices[vIdx]);
        } else {
            targetRealIndexes = selectedRowIndices || [];
        }

        if (targetRealIndexes.length === 0) return window.dash_clientside.no_update;

        targetRealIndexes.forEach(idx => {
            if (tableData[idx] && tableData[idx].CRN) {
                const rowKey = String(tableData[idx].CRN).trim().replace(/"/g, '\\"');

                // Add the custom color background target block natively to the conditional styles map
                baseStyles.push({
                    'if': {
                        'filter_query': '{CRN} = "' + rowKey + '"',
                        'column_id': 'colorRec'
                    },
                    'backgroundColor': selectedColor
                });
            }
        });

        return baseStyles;
    }
    """,
    Output("datatable-interactivity", "style_data_conditional", allow_duplicate=True),
    Input("color-select", "value"),
    [
        State("datatable-interactivity", "data"),
        State("datatable-interactivity", "derived_virtual_indices"),
        State("datatable-interactivity", "derived_virtual_selected_rows"),
        State("datatable-interactivity", "style_data_conditional"),
    ],
    prevent_initial_call=True,
)


app.clientside_callback(
    """
    function(currentTableData) {
        if (!currentTableData || currentTableData.length === 0) {
            return [];
        }

        const dynamicCellStyles = [
            {
                'if': { 'column_id': 'colorRec' },
                'color': 'rgba(0,0,0,0)'
            }
        ];

        currentTableData.forEach((row) => {
            const rowKey = String(row.CRN || '').trim().replace(/"/g, '\\"');
            if (!rowKey) return;

            if (row.colorRec) {
                dynamicCellStyles.push({
                    'if': {
                        'row_index': currentTableData.indexOf(row),
                        'column_id': 'colorRec'
                    },
                    'backgroundColor': row.colorRec
                });
            }

            if (String(row.S || '').trim().toUpperCase() === 'C') {
                dynamicCellStyles.push({
                    'if': {
                        'row_index': currentTableData.indexOf(row),
                    },
                    'backgroundColor': '#ffe4e6',
                    'color': '#9f1239'
                });
                dynamicCellStyles.push({
                    'if': {
                        'row_index': currentTableData.indexOf(row),
                        'column_id': 'colorRec'
                    },
                    'backgroundColor': '#ffe4e6',
                    'color': 'rgba(0,0,0,0)'
                });
            }

            const calcVal = String(row.Calc || '').trim().toUpperCase();
            if (calcVal === 'L') {
                const targetColumn = row.Calc !== undefined ? 'Calc' : 'Calc';
                dynamicCellStyles.push({
                    'if': {
                        'row_index': currentTableData.indexOf(row),
                        'column_id': targetColumn
                    },
                    'backgroundColor': '#EBF8FF',
                    'color': '#2B6CB0',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                });
            }

            if (calcVal === 'N') {
                const targetColumn = row.Calc !== undefined ? 'Calc' : 'Calc';
                dynamicCellStyles.push({
                    'if': {
                        'row_index': currentTableData.indexOf(row),
                        'column_id': targetColumn
                    },
                    'backgroundColor': '#ffe4e6',
                    'color': '#9f1239',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                });
            }

            if (calcVal === 'Y') {
                const targetColumn = row.Calc !== undefined ? 'Calc' : 'Calc';
                dynamicCellStyles.push({
                    'if': {
                        'row_index': currentTableData.indexOf(row),
                        'column_id': targetColumn
                    },
                    'textAlign': 'center',
                });
            }

            const waitlistCount = parseInt(row.WLst || row.WL, 10);
            if (!isNaN(waitlistCount) && waitlistCount > 0) {
                const targetCol = row.WLst !== undefined ? 'WLst' : 'WL';
                dynamicCellStyles.push({
                    'if': {
                        'row_index': currentTableData.indexOf(row),
                        'column_id': targetCol
                    },
                    'backgroundColor': '#FEFCBF',
                    'color': '#744210'
                });
            }

            const statusVal = String(row.S || '').trim().toUpperCase();
            const creditVal = parseFloat(row.Credit || 0);
            const enrolledValue = parseInt(row.Enrolled, 10);
            const subjectVal = String(row.Subject || '').trim().toUpperCase();
            const courseNumber = String(row.Number || '').trim();
            const courseNumberInt = parseInt(courseNumber, 10);
            const maxCapacity = parseInt(row.Max || row.MAX, 10);

            const isBaselineMatch = (
                statusVal === 'A' &&
                maxCapacity > 0 &&
                (creditVal > 0 || calcVal === 'L') &&
                (subjectVal.includes('MTH') || subjectVal.includes('MTL'))
            );


            let styleApplied = false;

            if (isBaselineMatch && !isNaN(courseNumberInt) && !isNaN(enrolledValue)) {
                const conditionOne   = (enrolledValue < 15 && courseNumberInt < 2000);
                const conditionTwo   = (enrolledValue < 15 && (courseNumberInt >= 2000 && courseNumberInt < 3000));
                const conditionThree = (enrolledValue < 10 && (courseNumberInt >= 3000 && courseNumberInt < 4000));
                const conditionFour  = (enrolledValue < 10 && courseNumberInt >= 4000);

                if (conditionOne || conditionTwo || conditionThree || conditionFour) {
                    dynamicCellStyles.push({
                        'if': {
                            'row_index': currentTableData.indexOf(row),
                            'column_id': 'Enrolled'
                        },
                        'backgroundColor': '#FFC7CE',
                        'color': '#9C0006',
                    });
                    styleApplied = true;
                }
            }

            const ratioValue = parseInt(row.Ratio, 10);

            if (!isNaN(ratioValue)) {
                if (ratioValue > 80) {
                    dynamicCellStyles.push({
                        'if': {
                            'row_index': currentTableData.indexOf(row),
                            'column_id': 'Enrolled'
                        },
                        'backgroundColor': '#C6EFCE',
                        'color': '#006100',
                    });
                    styleApplied = true;
                } else if (ratioValue > 94) {
                    dynamicCellStyles.push({
                        'if': {
                            'row_index': currentTableData.indexOf(row),
                            'column_id': 'Enrolled'
                        },
                        'backgroundColor': '#008000',
                        'color': 'white',
                    });
                    styleApplied = true;
                }
            }

            if (!styleApplied && statusVal === "A") {
                dynamicCellStyles.push({
                    'if': {
                        'row_index': currentTableData.indexOf(row),
                        'column_id': 'Enrolled'
                    },
                    'backgroundColor': '#ffffff', 'color': '#000000', 'fontWeight': 'normal'
                });
            }
        });

        return dynamicCellStyles;
    }
    """,
    Output("datatable-interactivity", "style_data_conditional"),
    Input("datatable-interactivity", "derived_virtual_data"),
)


app.clientside_callback(
    """
    function(updateClicks, liveTableData, filteredRows) {
        // Initialize a persistent window namespace variable to cache the grid state if it doesn't exist
        if (window._cachedGridRecords === undefined) {
            window._cachedGridRecords = liveTableData || [];
        }

        const context = dash_clientside.callback_context.triggered;
        let triggerId = '';
        if (context && context.length > 0 && context[0].prop_id) {
            triggerId = context[0].prop_id.split('.')[0];
        }

        // CHOOSE DATA CHANNEL BASED ON EXPLICIT ACTIONS:
        if (triggerId === 'update-grid-button') {
            // A. Manual Button Pushed -> Overwrite the visualization cache with the filtered snapshot
            window._cachedGridRecords = filteredRows ? filteredRows : (liveTableData || []);
        } else if (triggerId === 'datatable-interactivity') {
            // B. Color/Cell Edited -> Map the color changes directly onto our existing records cache
            const liveDataMap = {};
            if (liveTableData) {
                liveTableData.forEach(row => {
                    if (row.CRN) liveDataMap[row.CRN] = row.colorRec;
                });
            }

            // Apply new colors to the currently displayed classes without changing which classes are shown
            window._cachedGridRecords.forEach(row => {
                if (row.CRN && liveDataMap[row.CRN] !== undefined) {
                    row.colorRec = liveDataMap[row.CRN];
                }
            });
        } else {
            // C. Initial Load fallback
            if (window._cachedGridRecords.length === 0 && liveTableData) {
                window._cachedGridRecords = liveTableData;
            }
        }

        let dataRecords = window._cachedGridRecords;
        const dayAbbrvs = ['M', 'T', 'W', 'R', 'F', 'S'];

        const fallbackFigure = {
            data: [],
            layout: {
                height: 90,
                xaxis: { showticklabels: false, ticks: '', showgrid: false, zeroline: false },
                yaxis: { showticklabels: false, ticks: '', showgrid: false, zeroline: false },
                showlegend: false
            }
        };

        if (!dataRecords || dataRecords.length === 0) {
            return dayAbbrvs.map(() => fallbackFigure);
        }

        let records = dataRecords.filter(row => {
            const loc = String(row.Loc || '').trim();
            const campus = String(row.Campus || '').trim();
            const status = String(row.S || '').trim();
            return status === 'A' && campus !== 'I' && !/OFFC|ONLI|TBA|ASYNC/i.test(loc);
        });

        const uniqueRooms = [...new Set(records.map(r => r.Loc).filter(Boolean))].sort();
        const locationIndexMap = {};
        uniqueRooms.forEach((room, index) => locationIndexMap[room] = index);
        const numRooms = uniqueRooms.length;

        return dayAbbrvs.map(dayKey => {
            const offsetTracker = {};
            let currentDayRows = records.filter(r => String(r.Days || '').includes(dayKey));

            const duplicateCounter = {};
            currentDayRows.forEach(row => {
                const compositeKey = String(row.Time || '') + '_' + String(row.Loc || '');
                duplicateCounter[compositeKey] = (duplicateCounter[compositeKey] || 0) + 1;
            });

            let shapes = [];
            let annotations = [];

            currentDayRows.forEach(row => {
                const timeStr = String(row.Time || '').trim();
                if (timeStr.length < 11 || !timeStr.includes('-')) return;

                const timeParts = timeStr.split('-');
                if (timeParts.length !== 2) return;

                const startStr = timeParts[0].trim();
                const endStr = timeParts[1].trim();

                function parseTimeToMinutes(timeString) {
                    const isPM = timeString.toUpperCase().includes('PM');
                    const isAM = timeString.toUpperCase().includes('AM');
                    let cleanTime = timeString.replace(/(AM|PM)/i, '').trim();

                    const hm = cleanTime.split(':');
                    if (hm.length !== 2) return null;

                    let hours = parseInt(hm[0], 10);
                    let minutes = parseInt(hm[1], 10);

                    if (isPM && hours !== 12) hours += 12;
                    if (isAM && hours === 12) hours = 0;

                    return { hours, minutes };
                }

                const startTimeParsed = parseTimeToMinutes(startStr);
                const endTimeParsed = parseTimeToMinutes(endStr);

                if (!startTimeParsed || !endTimeParsed) return;

                let positionXStart = 0, positionXEnd = 0;
                try {
                    positionXStart = 12 * (startTimeParsed.hours - 8) + Math.floor(startTimeParsed.minutes / 5);
                    positionXEnd = 12 * (endTimeParsed.hours - 8) + Math.floor(endTimeParsed.minutes / 5);
                } catch (e) { return; }

                let axisYBase = locationIndexMap[row.Loc] !== undefined ? locationIndexMap[row.Loc] : 0;
                let blockHeight = 1.0;

                const matchKey = timeStr + '_' + String(row.Loc || '');
                const duplicateCount = duplicateCounter[matchKey] || 1;

                if (duplicateCount > 1) {
                    if (offsetTracker[matchKey] === undefined) offsetTracker[matchKey] = 0;
                    axisYBase += offsetTracker[matchKey] / duplicateCount;
                    blockHeight = 1.0 / duplicateCount;
                    offsetTracker[matchKey]++;
                }

                shapes.push({
                    type: 'rect', xref: 'x', yref: 'y',
                    x0: positionXStart, y0: axisYBase, x1: positionXEnd, y1: axisYBase + blockHeight,
                    line: { color: 'white', width: 1 },
                    fillcolor: row.colorRec || '#b3cde3', opacity: 0.95
                });

                annotations.push({
                    xref: 'x', yref: 'y',
                    x: positionXStart + (positionXEnd - positionXStart) / 2,
                    y: axisYBase + blockHeight / 2,
                    text: `${row.Subject || ''} ${row.Number || ''}-${row.Section || ''}`,
                    showarrow: false,
                    font: {
                        size: Math.max(8, Math.min(Math.floor(0.6 * (positionXEnd - positionXStart)), 11)),
                        color: '#334155'
                    },
                    hovertext: `Course: ${row.Subject || ''} ${row.Number || ''}<br>Title: ${row.Title || ''}<br>Time: ${timeStr}<br>Instructor: ${row.Instructor || ''}`
                });
            });

            for (let r = 0; r < numRooms; r++) {
                shapes.push({
                    type: 'rect', xref: 'x', yref: 'y', x0: 0, x1: 168, y0: r, y1: r + 1,
                    fillcolor: r % 2 === 1 ? '#f8fafc' : '#ffffff', layer: 'below', line: { width: 0 }
                });
            }

            if (numRooms === 0) return fallbackFigure;

            return {
                data: [{ x: [0.5 * numRooms], y: [-85], type: 'scatter', mode: 'markers', marker: { opacity: 0 }, hoverinfo: 'none' }],
                layout: {
                    autosize: false,
                    height: Math.max(200, 45 * numRooms),
                    width: 1270,
                    font: { color: '#475569', family: 'sans-serif' },
                    margin: { l: 45, r: 30, b: 20, t: 40, pad: 0 },
                    yaxis: {
                        range: [0, numRooms],
                        tickvals: uniqueRooms.map((_, i) => i + 0.5),
                        ticktext: uniqueRooms,
                        showgrid: false,
                        fixedrange: true,
                        showline: false,
                        zeroline: false,
                        tickfont: { color: '#64748b', size: 11 }
                    },
                    xaxis: {
                        range: [0, 168.2],
                        tickvals: Array.from({length: 15}, (_, i) => i * 12),
                        ticktext: Array.from({length: 15}, (_, i) => String(i + 8).padStart(2, '0') + ':00'),
                        showgrid: true,
                        side: 'top',
                        gridwidth: 1,
                        gridcolor: '#f1f5f9',
                        fixedrange: true,
                        showline: false,
                        zeroline: false,
                        tickfont: { color: '#64748b', size: 11 }
                    },
                    showlegend: false,
                    shapes: shapes,
                    annotations: annotations
                }
            };
        });
    }
    """,
    [Output(f"schedule_{day.lower()[:3]}", "figure") for day in days],
    [Input("update-grid-button", "n_clicks"), Input("datatable-interactivity", "data")],
    [State("datatable-interactivity", "derived_virtual_data")],
)


app.clientside_callback(
    """
    function(liveTableData, filteredRows) {
        // Read directly from the active filtered layout rows if present
        let records = (filteredRows && filteredRows.length > 0) ? filteredRows : (liveTableData || []);

        let totalSections = 0;
        let totalCoursesMap = {};
        let totalCredits = 0;
        let totalEnrolled = 0;
        let totalCHP = 0;

        let sumEnrolledForAvg = 0;
        let validEnrolledRowsCount = 0;
        let totalMaxSeatsForRatio = 0;
        let totalEnrolledForRatio = 0;
        let sumWaitlistForAvg = 0;
        let validWaitlistRowsCount = 0;

        if (!records || records.length === 0) {
            return ["0", "0", "0", "0.00", "0", "0.0", "0.00%", "0.00"];
        }

        records.forEach(row => {
            // 1. Total Sections volume count
            totalSections++;

            // 2. Unique Course ID track tracking map aggregation
            const courseKey = String(row.Course || row.Subject + row.Number || '').trim();
            if (courseKey) {
                totalCoursesMap[courseKey] = true;
            }

            // Extract core cell values natively
            const status = String(row.S || '').trim().toUpperCase();
            const creditVal = parseFloat(row.Credit) || 0;
            const enrolledVal = parseInt(row.Enrolled || row.ENR, 10);
            const maxSeatsVal = parseInt(row.Max || row.MAX, 10);
            const chpVal = parseFloat(row.CHP) || 0;
            const waitlistVal = parseInt(row.WLst || row.WL, 10);

            // Business Rule logic boundaries verification
            if (status === 'A') {
                totalCredits += creditVal;
                totalCHP += chpVal;

                if (!isNaN(enrolledVal)) {
                    totalEnrolled += enrolledVal;
                    sumEnrolledForAvg += enrolledVal;
                    validEnrolledRowsCount++;
                }

                if (!isNaN(maxSeatsVal)) {
                    totalMaxSeatsForRatio += maxSeatsVal;
                    if (!isNaN(enrolledVal)) {
                        totalEnrolledForRatio += enrolledVal;
                    }
                }

                if (!isNaN(waitlistVal)) {
                    sumWaitlistForAvg += waitlistVal;
                    validWaitlistRowsCount++;
                }
            }
        });

        // Compute summary metrics with fallback protection strings
        const totalCourses = Object.keys(totalCoursesMap).length;
        const avgEnrollment = validEnrolledRowsCount > 0 ? (sumEnrolledForAvg / validEnrolledRowsCount).toFixed(1) : "0.0";
        const avgWaitlist = validWaitlistRowsCount > 0 ? (sumWaitlistForAvg / validWaitlistRowsCount).toFixed(2) : "0.00";

        let fillRatePercent = "0.00%";
        if (totalMaxSeatsForRatio > 0) {
            fillRatePercent = ((totalEnrolledForRatio / totalMaxSeatsForRatio) * 100).toFixed(2) + "%";
        }

        // Return updated string metrics directly to layout card text wrappers
        return [
            String(totalSections),
            String(totalCourses),
            String(totalCredits.toFixed(0)),
            String(totalEnrolled),
            String(totalCHP.toFixed(0)),
            String(avgEnrollment),
            String(fillRatePercent),
            String(avgWaitlist)
        ];
    }
    """,
    [
        Output("total_sections_text", "children"),
        Output("total_courses_text", "children"),
        Output("total_credits_text", "children"),
        Output("total_enrollment_text", "children"),
        Output("total_CHP_text", "children"),
        Output("avg_enrollment_text", "children"),
        Output("avg_fill_rate_text", "children"),
        Output("avg_waitlist_text", "children"),
    ],
    [Input("datatable-interactivity", "data")],
    [Input("datatable-interactivity", "derived_virtual_data")],
    prevent_initial_call=False,
)


app.clientside_callback(
    """
    function(viewportData) {
        // Fallback default dictionary payload if table is cleared or empty
        const emptyLayout = {
            data: [],
            layout: {
                xaxis: { showticklabels: false, showgrid: false, zeroline: false },
                yaxis: { showticklabels: false, showgrid: false, zeroline: false },
                margin: { l: 20, r: 20, b: 20, t: 40 }
            }
        };

        if (!viewportData || viewportData.length === 0) {
            return [emptyLayout, emptyLayout, emptyLayout, emptyLayout];
        }

        // 1. DATA PREPARATION & PARSING
        let rows = viewportData.map(row => {
            return {
                Subject: String(row.Subject || '').trim(),
                Number: String(row.Number || '').trim(),
                CRN: String(row.CRN || '').trim(),
                Instructor: String(row.Instructor || '').trim(),
                Course: String(row.Course || row.Subject + row.Number || '').trim(),
                Credit: parseFloat(row.Credit) || 0,
                Enrolled: parseInt(row.Enrolled || row.ENR) || 0,
                Max: parseInt(row.Max || row.MAX) || 0,
                CHP: parseFloat(row.CHP) || 0,
                Ratio: parseFloat(row.Ratio) || 0,
                WLst: parseInt(row.WLst || row.WL) || 0
            };
        });

        // Filter for active sections (Credit > 0) for core volume metrics
        let activeRows = rows.filter(r => r.Credit > 0);

        // Sort descending by Max Capacity for the section/course graphs
        activeRows.sort((a, b) => b.Max - a.Max);

        // 2. PLOT A: PER-CRN OVERLAY BAR CHART
        const crnX = activeRows.map(r => r.CRN);
        const crnMaxY = activeRows.map(r => r.Max);
        const crnEnrY = activeRows.map(r => r.Enrolled);

        const figCrn = {
            data: [
                { x: crnX, y: crnMaxY, type: 'bar', name: 'Max', marker: { color: '#00447c' }, opacity: 0.8 },
                { x: crnX, y: crnEnrY, type: 'bar', name: 'Enrolled', marker: { color: '#d11242' }, overlaying: 'y' }
            ],
            layout: {
                title: { text: 'Enrollment per Section', font: { size: 14 } },
                barmode: 'overlay',
                showlegend: false,
                margin: { l: 50, r: 20, b: 40, t: 40 },
                xaxis: { type: 'category', tickfont: { size: 10 } },
                yaxis: { title: 'Seats / Students' }
            }
        };

        // 3. PLOT B: PER-COURSE AGGREGATED BAR CHART
        let courseMap = {};
        activeRows.forEach(r => {
            if (!courseMap[r.Course]) {
                courseMap[r.Course] = {
                    Max: 0,
                    Enrolled: 0,
                    Subject: r.Subject,
                    Number: r.Number
                };
            }
            courseMap[r.Course].Max += r.Max;
            courseMap[r.Course].Enrolled += r.Enrolled;
        });

        // Extract and explicitly sort the course list keys by Subject, then by Course Number
        const courseX = Object.keys(courseMap).sort((a, b) => {
            const subjA = courseMap[a].Subject;
            const subjB = courseMap[b].Subject;
            if (subjA !== subjB) return subjA.localeCompare(subjB);

            return courseMap[a].Number.localeCompare(courseMap[b].Number, undefined, {numeric: true});
        });

        const courseMaxY = courseX.map(c => courseMap[c].Max);
        const courseEnrY = courseX.map(c => courseMap[c].Enrolled);

        const figCourse = {
            data: [
                { x: courseX, y: courseMaxY, type: 'bar', name: 'Max', marker: { color: '#00447c' }, opacity: 0.8 },
                { x: courseX, y: courseEnrY, type: 'bar', name: 'Enrolled', marker: { color: '#d11242' }, overlaying: 'y' }
            ],
            layout: {
                title: { text: 'Enrollment per Course', font: { size: 14 } },
                barmode: 'overlay',
                showlegend: false,
                margin: { l: 50, r: 20, b: 40, t: 40 },
                xaxis: { type: 'category', tickfont: { size: 10 } },
                yaxis: { title: 'Seats / Students' }
            }
        };

        // 4. PLOT C: INSTRUCTOR COLOR-SCALE HEATMAP CHART
        let instMap = {};
        rows.forEach(r => {
            if (!instMap[r.Instructor]) {
                instMap[r.Instructor] = { Enrolled: 0, TotalRatio: 0, Count: 0 };
            }
            instMap[r.Instructor].Enrolled += r.Enrolled;
            instMap[r.Instructor].TotalRatio += r.Ratio;
            instMap[r.Instructor].Count += 1;
        });

        const instX = Object.keys(instMap).sort();
        const instEnrY = instX.map(i => instMap[i].Enrolled);
        const instColorC = instX.map(i => instMap[i].TotalRatio / instMap[i].Count);

        const figInst = {
            data: [{
                x: instX,
                y: instEnrY,
                type: 'bar',
                marker: {
                    color: instColorC,
                    colorscale: [
                        [0.0, '#d11242'], // Low Fill Rate Warning Red
                        [0.5, '#717073'], // Balanced Gray
                        [1.0, '#00447c']  // Highly Efficient Blue
                    ],
                    showscale: false
                }
            }],
            layout: {
                title: { text: 'Enrollment by Instructor', font: { size: 14 } },
                margin: { l: 50, r: 20, b: 60, t: 40 },
                xaxis: { type: 'category', tickangle: -45, tickfont: { size: 9 } },
                yaxis: { title: 'Students Enrolled' }
            }
        };

        // 5. PLOT D: COURSE CREDIT HOUR PRODUCTION (CHP) VOLUME CHART
        let chpMap = {};
        rows.forEach(r => {
            if (!chpMap[r.Course]) {
                chpMap[r.Course] = { CHP: 0, TotalRatio: 0, Count: 0 };
            }
            chpMap[r.Course].CHP += r.CHP;
            chpMap[r.Course].TotalRatio += r.Ratio;
            chpMap[r.Course].Count += 1;
        });

        const chpX = Object.keys(chpMap).sort((a, b) => chpMap[b].CHP - chpMap[a].CHP);
        const chpY = chpX.map(c => chpMap[c].CHP);
        const chpColorC = chpX.map(c => chpMap[c].TotalRatio / chpMap[c].Count);

        const figChp = {
            data: [{
                x: chpX,
                y: chpY,
                type: 'bar',
                marker: {
                    color: chpColorC,
                    colorscale: [
                        [0.0, '#d11242'],
                        [0.5, '#717073'],
                        [1.0, '#00447c']
                    ],
                    showscale: false
                }
            }],
            layout: {
                title: { text: 'Credit Hour Production by Course', font: { size: 14 } },
                margin: { l: 50, r: 20, b: 60, t: 40 },
                xaxis: { type: 'category', tickangle: -45, tickfont: { size: 9 } },
                yaxis: { title: 'Total Generated CHP' }
            }
        };

        return [figCrn, figCourse, figInst, figChp];
    }
    """,
    [
        Output("max_v_enrl_by_crn_graph", "figure"),
        Output("max_v_enrl_by_course_graph", "figure"),
        Output("enrl_by_instructor_graph", "figure"),
        Output("chp_by_course_graph", "figure"),
    ],
    [Input("datatable-interactivity", "derived_viewport_data")],
)


@app.callback(
    [
        Output("schedule_mon_div", "style"),
        Output("schedule_tue_div", "style"),
        Output("schedule_wed_div", "style"),
        Output("schedule_thu_div", "style"),
        Output("schedule_fri_div", "style"),
        Output("schedule_sat_div", "style"),
    ],
    [Input("weekdays-tabs", "value")],
)
def update_tab_display(tab):
    if (
        dash.callback_context.triggered
        and "weekdays-tabs" in dash.callback_context.triggered[0]["prop_id"]
    ):
        return [
            {"display": "block" if f"tab-{day.lower()[:3]}" == tab else "none"}
            for day in days
        ]
    return [{"display": "none"}] * 6


@app.callback(
    [
        Output("filter-query-input-container", "style"),
        Output("filter-query-output", "style"),
        Output("filter-query-output", "children"),
    ],
    [
        Input("filter-query-dropdown", "value"),
        Input("datatable-interactivity", "filter_query"),
    ],
)
def query_input_output(val, query):
    if val == "custom":
        return (
            {"marginLeft": "0px", "width": "100%", "display": "inline-block"},
            {"display": "none"},
            html.P(f'filter_query = "{query}"'),
        )
    return (
        {"display": "none"},
        {"display": "inline-block", "width": "100%"},
        html.P(f'filter_query = "{query}"'),
    )


@app.callback(
    [Output("datatable-interactivity", "filter_query")],
    [Input("apply_query_button", "n_clicks"), Input("filter-query-input", "n_submit")],
    [State("filter-query-dropdown", "value"), State("filter-query-input", "value")],
)
def apply_query(n_clicks, n_submit, dropdown_value, input_value):
    if n_clicks or n_submit:
        return [input_value if dropdown_value == "custom" else (dropdown_value or "")]
    return dash.no_update


@app.callback(
    Output("datatable-download", "data"),
    [
        Input("export-all-button", "n_clicks"),
        Input("export-filtered-button", "n_clicks"),
        Input("export-stacked-button", "n_clicks"),
    ],
    [
        State("datatable-interactivity", "data"),
        State("datatable-interactivity", "derived_virtual_data"),
    ],
    prevent_initial_call=True,
)
def handle_excel_downloads(
    all_clicks, filtered_clicks, stacked_clicks, all_data, filtered_data
):
    trigger_id = dash.ctx.triggered_id
    if not trigger_id:
        return dash.no_update

    if trigger_id == "export-filtered-button":
        df = pd.DataFrame(filtered_data)
        clicks = filtered_clicks
        filename_suffix = "FILTERED"
    else:
        df = pd.DataFrame(all_data)
        clicks = all_clicks if trigger_id == "export-all-button" else stacked_clicks
        filename_suffix = "STACKED" if trigger_id == "export-stacked-button" else "ALL"

    if clicks == 0 or df.empty:
        return dash.no_update

    report_term = detect_academic_term(df)
    term_code = convert_term_title_to_code(report_term)

    if trigger_id == "export-stacked-button":
        excel_content = to_excel(labs_combined(df), report_term)
    else:
        excel_content = to_excel(df, report_term)

    b64_content = base64.b64encode(excel_content).decode("utf-8")

    return {
        "base64": True,
        "content": b64_content,
        "filename": f"SWRCGSR_{term_code}_{filename_suffix}.xlsx",
    }


@dash.callback(
    Output("download-pdf-channel", "data"),
    [Input("btn-pdf-instructor", "n_clicks"), Input("btn-pdf-course", "n_clicks")],
    State("datatable-interactivity", "data"),
    prevent_initial_call=True,
)
def handle_pdf_exports(inst_clicks, course_clicks, filtered_data):
    if not filtered_data:
        return dash.no_update
    trigger_id = dash.ctx.triggered_id
    df = pd.DataFrame(filtered_data)

    if "S" in df.columns:
        df = df[df["S"].astype(str).str.strip() == "A"]
    if "Class" not in df.columns and "Subject" in df.columns and "Number" in df.columns:
        df["Class"] = df["Subject"].astype(str) + " " + df["Number"].astype(str)
    if "Loc" in df.columns and "Bldg" not in df.columns:
        df["Bldg"] = (
            df["Loc"]
            .astype(str)
            .apply(lambda x: x.split()[0] if len(x.split()) > 0 else "ONLI")
        )
        df["Room"] = (
            df["Loc"]
            .astype(str)
            .apply(lambda x: x.split()[1] if len(x.split()) > 1 else "")
        )

    pdf_buffer = io.BytesIO()
    report_term = detect_academic_term(df)

    if trigger_id == "btn-pdf-instructor":
        build_grouped_replica_pdf(df, "Instructor", report_term, pdf_buffer)
        pdf_buffer.seek(0)
        return dcc.send_bytes(pdf_buffer.read(), "Schedule_By_Instructor.pdf")
    elif trigger_id == "btn-pdf-course":
        build_grouped_replica_pdf(df, "Class", report_term, pdf_buffer)
        pdf_buffer.seek(0)
        return dcc.send_bytes(pdf_buffer.read(), "Schedule_By_Course.pdf")
    return dash.no_update


app.clientside_callback(
    """
    function(viewportData, toggleValue) {
        const emptyArr = [];
        const fallbackPie = {
            data: [],
            layout: {
                showlegend: false, height: 270, margin: { t: 15, b: 15, l: 15, r: 15 },
                annotations: [{ text: 'No Data', showarrow: false }]
            }
        };

        if (!viewportData || viewportData.length === 0) {
            return [emptyArr, emptyArr, fallbackPie, "Max Ratios"];
        }

        let rows = viewportData.map(row => {
            return {
                Instructor: String(row.Instructor || '').trim(),
                Course: String(row.Course || row.Subject + row.Number || '').trim(),
                Campus: String(row.Campus || '').trim().toUpperCase(),
                Time: String(row.Time || '').trim().toUpperCase(),
                Loc: String(row.Loc || '').trim().toUpperCase(),
                Credit: parseFloat(row.Credit) || 0,
                Enrolled: parseInt(row.Enrolled || row.ENR) || 0,
                Max: parseInt(row.Max || row.MAX) || 0,
                CHP: parseFloat(row.CHP) || 0,
                Ratio: parseFloat(row.Ratio) || 0
            };
        });

        // 1. GENERATE INSTRUCTOR DATA LIST
        let instMap = {};
        rows.forEach(r => {
            if (r.Credit !== 0) {
                if (!instMap[r.Instructor]) { instMap[r.Instructor] = { Total: 0, Sum: 0, Count: 0 }; }
                instMap[r.Instructor].Total += r.Enrolled;
                instMap[r.Instructor].Sum += r.Enrolled;
                instMap[r.Instructor].Count += 1;
            }
        });

        let instRecords = Object.keys(instMap).map(k => {
            return {
                'Instructor': k,
                'Total': instMap[k].Total,
                'Avg': instMap[k].Count > 0 ? parseFloat((instMap[k].Sum / instMap[k].Count).toFixed(2)) : 0
            };
        }).sort((a, b) => a.Instructor.localeCompare(b.Instructor));

        // 2. GENERATE COURSE DATA LIST
        let courseMap = {};
        rows.forEach(r => {
            if (r.Credit !== 0) {
                if (!courseMap[r.Course]) { courseMap[r.Course] = { CHP: 0, Enrolled: 0, Max: 0 }; }
                courseMap[r.Course].CHP += r.CHP;
                courseMap[r.Course].Enrolled += r.Enrolled;
                courseMap[r.Course].Max += r.Max;
            }
        });

        let courseRecords = Object.keys(courseMap).map(k => {
            return {
                'Course': k,
                'CHP': courseMap[k].CHP,
                'Enrolled': courseMap[k].Enrolled,
                'Max': courseMap[k].Max
            };
        }).sort((a, b) => a.Course.localeCompare(b.Course));

        // 3. GENERATE PIE CHART RATIOS
        let activeSplitRows = rows.filter(r => r.Credit > 0);
        let asyncCount = activeSplitRows.filter(r =>
            (r.Campus === 'I' && r.Time.includes('TBA')) ||
            (r.Campus === 'M' && r.Time.includes('TBA') && (r.Loc.includes('ASYN') || r.Loc.includes('ONLI') || r.Loc.includes('MOST')))
        ).length;

        let syncCount = activeSplitRows.filter(r =>
            (r.Campus === 'I' && !r.Time.includes('TBA')) || (r.Campus === 'M' && r.Loc.includes('SYNC'))
        ).length;

        let f2fVal = 0;
        let onlineVal = asyncCount + syncCount;

        if (toggleValue === 'Enrolled' || toggleValue === 'Max') {
            let totalVolume = activeSplitRows.reduce((s, r) => s + r[toggleValue], 0);
            let onlineVolume = activeSplitRows.filter(r =>
                (r.Campus === 'I' && r.Time.includes('TBA')) ||
                (r.Campus === 'M' && r.Time.includes('TBA') && (r.Loc.includes('ASYN') || r.Loc.includes('ONLI') || r.Loc.includes('MOST'))) ||
                (r.Campus === 'I' && !r.Time.includes('TBA')) || (r.Campus === 'M' && r.Loc.includes('SYNC'))
            ).reduce((s, r) => s + r[toggleValue], 0);

            f2fVal = Math.max(0, totalVolume - onlineVolume);
            onlineVal = onlineVolume;
        } else {
            f2fVal = Math.max(0, activeSplitRows.length - onlineVal);
        }

        const pieFig = {
            data: [{
                values: [f2fVal, onlineVal], labels: ['F2F', 'Online'],
                marker: { colors: ['#00447c', '#d11242'] }, hole: 0.7, type: 'pie',
                hoverinfo: 'label+value+percent',
            }],
            layout: {
                showlegend: false, height: 270, margin: { t: 15, b: 15, l: 15, r: 15 },
                annotations: [{ text: 'F2F<br />vs<br />Online', x: 0.5, y: 0.5, font: { size: 11 }, showarrow: false }]
            }
        };

        return [instRecords, courseRecords, pieFig, toggleValue + " Ratios"];
    }
    """,
    [
        Output("enrl_by_instructor_table", "data"),
        Output("chp_by_course_table", "data"),
        Output("graph_f2f", "figure"),
        Output("f2f-dynamic-title-header", "children"),
    ],
    [
        Input("datatable-interactivity", "derived_viewport_data"),
        Input("enrollment-max-actual", "value"),
    ],
)


# ==========================================
# PURE JAVASCRIPT SPLITS MATRIX PROCESSING ENGINE
# ==========================================
app.clientside_callback(
    """
    function(viewportData) {
        // Fallback matrices array structure generator
        const makeBlankOutput = () => {
            let silentGraph = {
                data: [{ x: [], y: [], type: 'bar' }],
                layout: {
                    margin: { l: 0, r: 0, t: 0, b: 0 },
                    height: 65,
                    xaxis: { visible: false },
                    yaxis: { visible: false },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    showlegend: false
                }
            };
            // Returns matching structural array metrics to placeholder grid elements
            return ["0", "0", "0", "0.0", "0", "0", "0.0", silentGraph];
        };

        let defaultReturn = [];
        for(let i=0; i<6; i++) { defaultReturn = defaultReturn.concat(makeBlankOutput()); }

        if (!viewportData || viewportData.length === 0) return defaultReturn;


        // 1. Core Data Classification Segments
        let segments = {
            lab: [], lvl1: [], lvl2: [], lvl3: [], lvl4: [], tot: []
        };

        viewportData.forEach(row => {
            // Process Status condition matching your original python backend engine logic
            let status = String(row.S || '').trim().toUpperCase();
            if (status !== 'A') return;

            // Exclude any classes where the maximum seat capacity is 0 from ALL logic
            let maxCapacity = parseInt(row.Max || row.MAX) || 0;
            if (maxCapacity === 0) return;

            // Exclude any rows where the Calc column is explicitly set to 'N'
            let calcType = String(row.Calc || '').trim().toUpperCase();
            if (calcType === 'N') return;

            if (calcType === 'L') {
                segments.lab.push(row);
                return; // Blocks the row from leaking down into level or total cards
            }

            let numStr = String(row.Number || '').trim();
            let firstDigit = numStr.charAt(0);

            // Grouping checks for remaining normal classes
            if (firstDigit === '1') segments.lvl1.push(row);
            else if (firstDigit === '2') segments.lvl2.push(row);
            else if (firstDigit === '3') segments.lvl3.push(row);
            else if (firstDigit === '4') segments.lvl4.push(row);

            segments.tot.push(row);
        });

        let globalMaxEnrolledVal = 0;
        viewportData.forEach(row => {
            let status = String(row.S || '').trim().toUpperCase();
            let maxCapacity = parseInt(row.Max || row.MAX) || 0;
            let calcType = String(row.Calc || '').trim().toUpperCase();

            if (status === 'A' && maxCapacity > 0 && calcType !== 'N') {
                let enrl = parseInt(row.Enrolled) || 0;
                if (enrl > globalMaxEnrolledVal) {
                    globalMaxEnrolledVal = enrl;
                }
            }
        });
        if (globalMaxEnrolledVal < 20) globalMaxEnrolledVal = 20;



        // 2. Metrics Mapping Calculation Loop
        let finalOutputs = [];
        const keys = ['lab', 'lvl1', 'lvl2', 'lvl3', 'lvl4', 'tot'];

        keys.forEach(k => {
                        let rows = segments[k];
            if (rows.length === 0) {
                let emptyGraphJSON = {
                    data: [{ x: [], y: [], type: 'bar' }],
                    layout: {
                        margin: { l: 0, r: 0, t: 0, b: 0 },
                        height: 65,
                        xaxis: { visible: false },
                        yaxis: { visible: false },
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        showlegend: false
                    }
                };

                finalOutputs.push("0", "0", "0.0", "0", "0", "0.0%", "0.0", emptyGraphJSON);
                return;
            }


            let sectCount = rows.length;

            // Unique Course Count Logic Tracking Maps
            let uniqueCourses = {};
            let totalEnrl = 0;
            let minEnrl = Infinity;
            let totalWl = 0;
            let totalChp = 0;
            let enrlArray = [];

            rows.forEach(r => {
                let courseKey = String(r.Course || (String(r.Subject || '') + String(r.Number || ''))).trim();
                if (courseKey) uniqueCourses[courseKey] = true;

                let enrl = parseInt(r.Enrolled) || 0;
                if (enrl > 0 && minEnrl > enrl) minEnrl = enrl;
                let wl   = parseInt(r.WLst) || 0;
                let chp  = parseInt(r.CHP) || 0;

                totalEnrl += enrl;
                totalWl += wl;
                totalChp += chp;
                enrlArray.push(enrl);
            });

            let courseCount = Object.keys(uniqueCourses).length;
            let avgEnrl = (totalEnrl / sectCount).toFixed(1);
            let totalMax = 0;
            let fillRate = totalMax > 0 ? ((totalEnrl / totalMax) * 100).toFixed(1) + "%" : "0.0%";

            // 3. Mini Micro Distribution Plotly JSON Builder Engine
            // Count distribution of enrolled frequencies
            let xArr = [];
            let yArr = [];

            for (let i = 0; i <= globalMaxEnrolledVal; i++) {
                xArr.push(i);

                let count = enrlArray.filter(v => v === i).length;
                yArr.push(count);
            }


            let graphJSON = {
                data: [{
                    x: xArr,
                    y: yArr,
                    type: 'bar',
                    marker: { color: '#00447C' },
                    hoverinfo: 'x+y'
                }],
                layout: {
                    margin: { l: 5, r: 5, t: 2, b: 5 },
                    height: 45,
                    xaxis: {
                        visible: true,
                        showline: true,
                        linecolor: '#00447C',
                        showgrid: false,
                        zeroline: false,
                        showticklabels: false,
                        range: [-0.5, globalMaxEnrolledVal + 0.5]
                    },
                    yaxis: { showgrid: false, zeroline: false, visible: false },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    showlegend: false
                }
            };

            finalOutputs.push(
                parseInt(sectCount).toLocaleString(),
                parseInt(courseCount).toLocaleString(),
                parseInt(totalEnrl).toLocaleString(),
                parseFloat(avgEnrl).toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 }),
                parseInt(totalChp).toLocaleString(),
                minEnrl === Infinity ? "0" : parseInt(minEnrl).toLocaleString(),
                parseInt(totalWl).toLocaleString(),
                graphJSON
            );
        });

        return finalOutputs;
    }
    """,
    [
        # LAB OUTPUT TARGETS
        Output("lab_sections", "children"),
        Output("lab_courses", "children"),
        Output("lab_total_enrl", "children"),
        Output("lab_avg_enrl", "children"),
        Output("lab_total_chp", "children"),
        Output("lab_min_enrl", "children"),
        Output("lab_wlst", "children"),
        Output("lab_mini_graph", "figure"),
        # 1000 LEVEL OUTPUT TARGETS
        Output("lvl1_sections", "children"),
        Output("lvl1_courses", "children"),
        Output("lvl1_total_enrl", "children"),
        Output("lvl1_avg_enrl", "children"),
        Output("lvl1_total_chp", "children"),
        Output("lvl1_min_enrl", "children"),
        Output("lvl1_wlst", "children"),
        Output("lvl1_mini_graph", "figure"),
        # 2000 LEVEL OUTPUT TARGETS
        Output("lvl2_sections", "children"),
        Output("lvl2_courses", "children"),
        Output("lvl2_total_enrl", "children"),
        Output("lvl2_avg_enrl", "children"),
        Output("lvl2_total_chp", "children"),
        Output("lvl2_min_enrl", "children"),
        Output("lvl2_wlst", "children"),
        Output("lvl2_mini_graph", "figure"),
        # 3000 LEVEL OUTPUT TARGETS
        Output("lvl3_sections", "children"),
        Output("lvl3_courses", "children"),
        Output("lvl3_total_enrl", "children"),
        Output("lvl3_avg_enrl", "children"),
        Output("lvl3_total_chp", "children"),
        Output("lvl3_min_enrl", "children"),
        Output("lvl3_wlst", "children"),
        Output("lvl3_mini_graph", "figure"),
        # 4000 LEVEL OUTPUT TARGETS
        Output("lvl4_sections", "children"),
        Output("lvl4_courses", "children"),
        Output("lvl4_total_enrl", "children"),
        Output("lvl4_avg_enrl", "children"),
        Output("lvl4_total_chp", "children"),
        Output("lvl4_min_enrl", "children"),
        Output("lvl4_wlst", "children"),
        Output("lvl4_mini_graph", "figure"),
        # TOTAL VIEW OUTPUT TARGETS
        Output("tot_sections", "children"),
        Output("tot_courses", "children"),
        Output("tot_total_enrl", "children"),
        Output("tot_avg_enrl", "children"),
        Output("tot_total_chp", "children"),
        Output("tot_min_enrl", "children"),
        Output("tot_wlst", "children"),
        Output("tot_mini_graph", "figure"),
    ],
    [Input("datatable-interactivity", "derived_virtual_data")],
    prevent_initial_call=False,
)


@app.callback(
    Output("enrl_by_instructor", "children"),
    Input("datatable-interactivity", "derived_viewport_data"),
    prevent_initial_call=False,
)
def render_clientside_instructor_table_bridge(data):
    # This minimal server callback builds the UI framework wrapper once, while sorting/filtering remains inside the browser
    if not data:
        return []
    return [
        html.H6("Enrollment by Instructor"),
        dash_table.DataTable(
            id="instructor-table-backend-receiver",
            columns=[{"name": i, "id": i} for i in ["Instructor", "Total", "Avg"]],
            data=[],
            fixed_rows={"headers": True},
            style_table={"height": "400px", "overflowY": "auto"},
            sort_action="native",
        ),
    ]


@app.callback(
    Output("chp_by_course", "children"),
    Input("datatable-interactivity", "derived_viewport_data"),
    prevent_initial_call=False,
)
def render_clientside_course_table_bridge(data):
    if not data:
        return []
    return [
        html.H6("Course CHP and Enrollment"),
        dash_table.DataTable(
            id="course-table-backend-receiver",
            columns=[
                {"name": i, "id": i} for i in ["Course", "CHP", "Enrolled", "Max"]
            ],
            data=[],
            fixed_rows={"headers": True},
            style_table={"height": "400px", "overflowY": "auto"},
            sort_action="native",
        ),
    ]


# Link the clientside computations straight onto the internal grid elements generated above
app.clientside_callback(
    "function(data) { return data || []; }",
    Output("instructor-table-backend-receiver", "data"),
    Input("datatable-interactivity", "style_cell_conditional"),
)

app.clientside_callback(
    "function(data) { return data || []; }",
    Output("course-table-backend-receiver", "data"),
    Input("datatable-interactivity", "style_header_conditional"),
)

if __name__ == "__main__":
    app.run(debug=DEBUG, port="8001", dev_tools_hot_reload=False)
