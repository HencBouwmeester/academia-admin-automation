# -*- coding: utf-8 -*-

# Import required libraries
import dash
import pandas as pd
import io
from dash import html, dcc
import plotly.io as pio
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from utils import parse_enrollment_file, process_excel_import, \
        build_grouped_pdf, build_grouped_replica_pdf, detect_academic_term, \
        blankFigure, convert_to_24hr, convert_term_title_to_code, \
        generate_weekday_tab, generate_tab_fig, parse_contents_integrated, \
        create_datatable, update_grid, to_excel
from utils_analytics import *

DEBUG = False

if DEBUG:
    print('Dash Version: {:s}'.format(dash.__version__))

# Include pretty graph formatting
pio.templates.default = 'plotly_white'

# Initialize server
app = dash.Dash(
    __name__,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
    prevent_initial_callbacks=True,
    requests_pathname_prefix='/dashboard/',
    routes_pathname_prefix='/dashboard/',
)

server = app.server
app.title = 'Schedule and Analytics Portal'

app.config.update({
    'suppress_callback_exceptions': True,
})

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


# Create app layout
app.layout = html.Div(
    [
        html.Div(
            [
                # App Header
                html.Div(
                    [
                        html.Div([
                            html.Img(id='msudenver-logo',
                                     src=app.get_asset_url('msudenver-logo.png'),
                                     style={'height': '36px', 'marginRight': '16px', 'display': 'inline-block', 'verticalAlign': 'middle'}),
                            # html.H1('Course Scheduling Control Panel',
                                    # style={'display': 'inline-block', 'margin': '0', 'fontSize': '2.4rem', 'fontWeight': '300', 'color': '#0f172a', 'verticalAlign': 'middle'}),
                                    # # Inside your app.layout Division:
html.H1('MSU Denver MAST Schedule & Enrollment Analytics Portal',
        style={'display': 'inline-block', 'margin': '0', 'fontSize': '2.4rem', 'fontWeight': '300', 'color': '#0f172a', 'verticalAlign': 'middle'}),
                        ], style={'display': 'flex', 'alignItems': 'center'}),

                        dcc.Upload(id='upload-data',
                                   children=html.Button(['Upload Native Roster File'],
                                                        id='upload-data-button',
                                                        n_clicks=0,
                                                        className='btn-primary'),
                                   multiple=False,
                                   accept='.txt, .xlsx, .xls'),
                    ],
                    id='header',
                    style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'padding': '20px 0', 'borderBottom': '1px solid #e2e8f0', 'marginBottom': '24px'},
                ),

                # Active Dynamic Dashboard Area Wrapper
                html.Div(
                    [
                        # NEW: Main Dashboard Navigation Tabs
                        dcc.Tabs(
                            id='main-dashboard-tabs',
                            value='tab-schedule-grid',
                            children=[

                                # TAB 1: Weekday Schedule Grid View
                                dcc.Tab(
                                    label='📅 Weekday Schedule Grid',
                                    value='tab-schedule-grid',
                                    children=[
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        dcc.Tabs([generate_weekday_tab(day) for day in days],
                                                                 id='weekdays-tabs',
                                                                 value='tab-mon',
                                                                 style={'height': '40px'})
                                                    ], style={'borderBottom': '1px solid #e2e8f0', 'marginBottom': '16px', 'marginTop': '20px'}
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [generate_tab_fig(day, 'tab-mon', None) for day in days],
                                                            id='weekdays-tabs-content',
                                                            style={'width': '100%', 'background': 'white'}
                                                        ),
                                                    ]
                                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Button('Update Preview Grid', id='update-grid-button', n_clicks=0, className='btn-primary', style={'marginRight': '8px'}),
                                                html.Button('+ Add Row Record', id='add-row-button', n_clicks=0, className='btn-secondary', style={'marginRight': '8px', 'color': '#ffffff', 'background-color': '#16a34a', 'borderColor': '#bbf7d0'}),
                                                html.Button('Delete Row(s)', id='delete-rows-button', n_clicks=0, className='btn-danger', style={'marginRight': '8px'}),
                                            ],
                                            style={'display': 'flex', 'flexWrap': 'wrap', 'alignItems': 'center'}
                                        ),
                                        html.Div(
                                            [
                                                html.Button('Reset Highlights', id='reset-colors-button', n_clicks=0, className='btn-secondary', style={'marginRight': '8px'}),
                                                dcc.Dropdown(id='color-select',
                                                             options=[
                                                             {'label': 'Blue Accent', 'value': '#b3cde3'},
                                                             {'label': 'Red Accent', 'value': '#fbb4ae'},
                                                             {'label': 'Green Accent', 'value': '#ccebc5'},
                                                             {'label': 'Purple Accent', 'value': '#decbe4'},
                                                             {'label': 'Orange Accent', 'value': '#fed9a6'},
                                                             {'label': 'Yellow Accent', 'value': '#ffffcc'},
                                                             {'label': 'Tan Accent', 'value': '#e5d8bd'},
                                                             {'label': 'Pink Accent', 'value': '#fddaec'},
                                                             {'label': 'Muted Gray', 'value': '#f2f2f2'},
                                                             ],
                                                             value='#b3cde3',
                                                             clearable=False,
                                                             className='custom-dropdown',
                                                             ),
                                            ],
                                            style={'display': 'flex', 'flexWrap': 'wrap', 'alignItems': 'center'}
                                        ),
                                    ],
                                    style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '20px', 'background': '#f8fafc', 'padding': '14px', 'borderRadius': '8px', 'border': '1px solid #e2e8f0'}
                                ),
                                            ],
                                            className='control-card'
                                        ),
                                    ]
                                ),

                                # TAB 2: Analytics & Plots View (Placeholder Container)
                                dcc.Tab(
                                    label='📊 Analytics & Plots View',
                                    value='tab-analytics-plots',
                                    id='analytics-plots-tab-container',
                                    children=[
                                        html.Div([
                                        # Key Performance Indicator Cards Row
                                        html.Div([
                                            html.Div([
                                                html.Div([
                                                    html.Div([html.H6("0", id="total_sections_text"), html.P("Sections")], id="sections", className="mini_container"),
                                                    html.Div([html.H6("0", id="total_courses_text"), html.P("Courses")], id="total_courses", className="mini_container"),
                                                    html.Div([html.H6("0", id="total_credits_text"), html.P("Credits")], id="total_credits", className="mini_container"),
                                                    html.Div([html.H6("0.00", id="total_enrollment_text"), html.P("Enrollment")], id="total_enrollment", className="mini_container"),
                                                    html.Div([html.H6("0", id="total_CHP_text"), html.P("CHP")], id="total_CHP", className="mini_container"),
                                                    html.Div([html.H6("0.0", id="avg_enrollment_text"), html.P("Average Enrollment by CRN")], id="avg_enrollment", className="mini_container"),
                                                    html.Div([html.H6("0.00%", id="avg_fill_rate_text"), html.P("Average Fill Rate")], id="avg_fill_rate", className="mini_container"),
                                                    html.Div([html.H6("0.00", id="avg_waitlist_text"), html.P("Average Waitlist")], id="avg_waitlist", className="mini_container"),
                                                    ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginTop': '15px'}),
                                                ], className="pretty_container twelve columns"),
                                            ], className="row flex-display"),
                                        # Class Division Breakdown Data Matrices Row
                                        html.Div([
                                            # html.Div([
                                                # html.Div([
                                                    # html.Div(summary_stats(pd.DataFrame(), '', 0), id="lab_enrollment", className="mini_container two columns"),
                                                    # html.Div(summary_stats(pd.DataFrame(), '', 0), id="1000_enrollment", className="mini_container two columns"),
                                                    # html.Div(summary_stats(pd.DataFrame(), '', 0), id="2000_enrollment", className="mini_container two columns"),
                                                    # html.Div(summary_stats(pd.DataFrame(), '', 0), id="3000_enrollment", className="mini_container two columns"),
                                                    # html.Div(summary_stats(pd.DataFrame(), '', 0), id="4000_enrollment", className="mini_container two columns"),
                                                    # html.Div(summary_stats(pd.DataFrame(), '', 0), id="calc_total_enrollment", className="mini_container two columns"),
                                                    # ], style={'display': 'flex'}),
                                                # ], className="pretty_container twelve columns"),
                                            ], className="row flex-display", id="calc_row"),

                                        # Institutional Notes Panel
                                        html.Div([
                                            html.H6("Notes:"),
                                            html.Ul([
                                                html.Li("Lab enrollments, marked with an 'L' in the datatable, are not included in Total calculations."),
                                                html.Li("5000 level courses are only included in the Total calculations."),
                                                ]),
                                            ], id="notes_enrollment", style={'padding': '10px 20px'}),
                                        # Visual Charts Rows - Breakdown Distributions
                                        html.Div([
                                            html.Div([dcc.Graph(figure=blankFigure(), id="max_v_enrl_by_crn_graph")], className="pretty_container six columns"),
                                            html.Div([dcc.Graph(figure=blankFigure(), id="max_v_enrl_by_course_graph")], className="pretty_container six columns"),
                                            ], className="row flex-display"),

                                        html.Div([
                                            html.Div([html.Div([], id="enrl_by_instructor", style={'width': '96%', 'display': 'block', 'margin': '0 auto'})], className="pretty_container four columns"),
                                            html.Div([html.Div([], id="chp_by_course", style={'width': '96%', 'display': 'block', 'margin': '0 auto'})], className="pretty_container four columns"),
                                            html.Div([
                                                dcc.Graph(figure=blankFigure(), id="graph_f2f"),
                                                html.Label([
                                                    "Enrollment Split View:",
                                                    dcc.RadioItems(
                                                        id='enrollment-max-actual',
                                                        options=[
                                                            {'label': 'Max', 'value': 'Max'},
                                                            {'label': 'Actual', 'value': 'Enrolled'},
                                                            {'label': 'Sections', 'value': 'Section'},
                                                            ],
                                                        labelStyle={'display': 'inline-block', 'marginRight': '10px'},
                                                        className="dcc_control",
                                                        value='Max'
                                                        ),
                                                    ]),
                                                ], className="pretty_container four columns"),
                                            ], className="row flex-display"),
                        # Instructor Profiles Distribution Visualizations Row
                        html.Div([
                            html.Div([dcc.Graph(figure=blankFigure(), id="enrl_by_instructor_graph")], className="pretty_container six columns"),
                            html.Div([dcc.Graph(figure=blankFigure(), id="chp_by_course_graph")], className="pretty_container six columns"),
                            ], className="row flex-display"),
                                            ],
                                            className='control-card'
                                        ),
                    ]
                ),
                            ]
                        ),

                        # Shared Controls: Filter Roster & Active Queries (Accessible to both tabs)
                        html.Div(
                            [
                                html.P('Filter Roster & Active Queries', className='section-title'),
                                html.Div(
                                    [
                                        html.Div([
                                            dcc.Dropdown(
                                                id='filter-query-dropdown',
                                                options=[
                                                    {'label': 'Custom Expression Filter...', 'value': 'custom'},
                                                    {'label': 'Active Math Classes', 'value': '{S} contains A'},
                                                    {'label': 'Math w/o Labs', 'value': '{Subject} contains M && {S} contains A && ({Number} < 1081 || {Number} > 1082) && ({Number} != "1101") && ({Number} != "1111") && ({Number} < 1115 || {Number} > 1116) && ({Number} < 1311 || {Number} > 1312)'},
                                                    {'label': 'Math Labs', 'value': '{Subject} contains M && {S} contains A && ({Number} = 1082 || {Number} = 1101 || {Number} = 1116 || {Number} = 1312)'},
                                                    {'label': 'Math Labs with Parents', 'value': '{Subject} contains M && {S} contains A && ({Number} = 1081 || {Number} = 1111 || {Number} = 1115 || {Number} = 1311 || {Number} = 1082 || {Number} = 1101 || {Number} = 1116 || {Number} = 1312)'},
                                                    {'label': 'Math Lower Division', 'value': '{Subject} contains M && {Number} < 3000 && {S} contains A'},
                                                    {'label': 'Math Upper Division', 'value': '{Subject} contains M && {Number} >= 3000 && {S} contains A'},
                                                    {'label': 'Applied Group', 'value': '{Subject} contains M && {S} contains A && ({Number} = 3130 || {Number} = 3400 || {Number} = 3420 || {Number} = 3430 || {Number} = 3440 || {Number} = 4480 || {Number} = 4490)'},
                                                    {'label': 'MathEd Group', 'value': '({S} contains A && {Subject} contains M && ({Number} = 1610 || {Number} = 2620 || {Number} = 3470 || {Number} = 3640 || {Number} = 3650)) || ({S} contains A && {Subject} contains MTL)'},
                                                    {'label': 'Statistics Group', 'value': '{Subject} contains M && {S} contains A && ({Number} = 3210 || {Number} = 3220 || {Number} = 3230 || {Number} = 3240 || {Number} = 3270 || {Number} = 3510 || {Number} = 4210 || {Number} = 4230 || {Number} = 4250 || {Number} = 4290)'},
                                                    {'label': 'Theoretical Group', 'value': '{Subject} contains M && {S} contains A && ({Number} = 3100 || {Number} = 3110 || {Number} = 3170 || {Number} = 3140 || {Number} = 4110 || {Number} = 4150 || {Number} = 4410 || {Number} = 4420 || {Number} = 4450)'},
                                                    {'label': 'Canceled CRNs', 'value': '{S} contains C'},
                                                ],
                                                placeholder='Select a baseline preset query rule',
                                                value='',
                                                className='custom-dropdown'),
                                        ], style={'flexGrow': '1', 'marginRight': '12px'}),

                                        html.Button('Apply Expression Rule', id='apply_query_button', className='btn-primary'),
                                        html.Label('All rooms:', style={'display': 'none'}, id='all-rooms-label'),
                                    ],
                                    style={'display': 'flex', 'alignItems': 'center', 'width': '100%'}
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        dcc.Input(id='filter-query-input',
                                                                  placeholder='syntax template: {Subject} contains "MTH" && {Number} >= 3000',
                                                                  className='custom-input',
                                                                  style={'width': '100%', 'boxSizing': 'border-box'}),
                                                    ],
                                                    id='filter-query-input-container',
                                                    style={'width': '100%', 'display': 'none'}
                                                ),
                                                html.Div(['filter_query = "None"'],
                                                         id='filter-query-output',
                                                         style={'width': '100%', 'fontSize': '1.05rem', 'color': '#64748b', 'fontFamily': 'monospace', 'backgroundColor': '#f8fafc', 'padding': '10px 14px', 'borderRadius': '6px', 'border': '1px dashed #cbd5e1', 'marginTop': '12px'}
                                                         ),
                                            ],
                                            style={'width': '100%'}
                                        )
                                    ]
                                ),
                            ],
                            className='control-card'
                        ),

                        # Shared Registry Table Panel (Accessible beneath both views)
                        html.Div(
                            [
                                html.P('Active Datatable Registry Controls', className='section-title'),

                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Button('Export Excel (All)', id='export-all-button', n_clicks=0, className='btn-secondary', style={'marginRight': '8px'}),
                                                dcc.Download(id='datatable-download'),
                                                html.Button('Export Excel (Filtered)', id='export-filtered-button', n_clicks=0, className='btn-secondary', style={'marginRight': '8px'}),
                                                dcc.Download(id='datatable-filtered-download'),
                                                dbc.Button("Export PDF (Instructor)", id="btn-pdf-instructor",  className='btn-secondary', style={'marginRight': '8px'}),
                                                dbc.Button("Export PDF (Course)", id="btn-pdf-course",  className='btn-secondary', style={'marginRight': '8px'}),
                                            ],
                                            style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center', 'whiteSpace': 'nowrap'}
                                        ),
                                    ],
                                    style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '20px', 'background': '#f8fafc', 'padding': '14px', 'borderRadius': '8px', 'border': '1px solid #e2e8f0'}
                                ),
                                dcc.Download(id="download-pdf-channel"),

                                html.Div(
                                    id='datatable-interactivity-container',
                                    children=create_datatable(pd.DataFrame(), ''),
                                    style={'width': '100%', 'display': 'block', 'borderRadius': '8px', 'overflow': 'hidden', 'border': '1px solid #e2e8f0'},
                                ),
                            ],
                            className='control-card'
                        ),
                    ],
                    id='output-data-upload',
                    style={'display': 'none'}
                )
            ],
            style={'maxWidth': '1440px', 'width': '95%', 'margin': '0 auto', 'paddingBottom': '60px'}
        )
    ],
    id='mainContainer',
    style={'display': 'flex', 'flexDirection': 'column'},
)

@app.callback(
    Output('output-data-upload', 'style'),
    Input('upload-data', 'contents')
)
def show_contents(contents):
    if contents is not None:
        return {'display': 'block'}


@app.callback(
    [Output('weekdays-tabs-content', 'children'),
     Output('datatable-interactivity-container', 'children'),
     Output('upload-data-button', 'n_clicks'),],
    [Input('update-grid-button', 'n_clicks'),
     Input('reset-colors-button', 'n_clicks'),
     Input('color-select', 'value'),
     State('weekdays-tabs', 'value'),
     State('upload-data', 'filename'),
     Input('upload-data', 'contents'),
     Input("datatable-interactivity", "data_timestamp"),
     State("datatable-interactivity", "filter_query"),
     State("datatable-interactivity", "data"),
     State('datatable-interactivity', 'derived_virtual_data'),
     State('datatable-interactivity', 'derived_virtual_indices'),
     State('datatable-interactivity', 'derived_virtual_selected_rows'),
     State('upload-data-button', 'n_clicks'),
    ]
)
def data_loading(
    update_n_clicks,
    reset_n_clicks,
    slctd_color,
    tab,
    name,
    contents,
    timestamp,
    filter_query,
    rows,
    filtered_rows,
    vtl_indices,
    slctd_row_indices,
    n_clicks,
):

    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""

    df = pd.DataFrame(rows)

    if contents is not None and input_id == 'upload-data' and n_clicks > 0:
        # Upgraded to run the unified file parsing engine from utils.py
        df = parse_contents_integrated(contents, name)
        df['colorRec'] = '#b3cde3'

    elif input_id == 'reset-colors-button':
        if not df.empty:
            df['colorRec'] = '#b3cde3'

    elif input_id == "color-select" and not df.empty:
        _index = slctd_row_indices
        if filtered_rows and len(rows) != len(filtered_rows):
            _index = vtl_indices

        if _index:
            df.loc[_index, 'colorRec'] = slctd_color

    # Regenerate datatable state matching current underlying dataset state
    data_children = create_datatable(df, filter_query)

    if input_id == 'update-grid-button':
        df_grid = pd.DataFrame(filtered_rows) if filtered_rows else df
        figs = update_grid(df_grid.to_dict('records'), df_grid.to_dict('records'), [])
    else:
        figs = update_grid(df.to_dict('records'), df.to_dict('records'), [])

    tabs_children = [generate_tab_fig(day, tab, fig) for day, fig in zip(days, figs)]

    return tabs_children, data_children, n_clicks


@app.callback(
    [Output('schedule_mon_div', 'style'),
     Output('schedule_tue_div', 'style'),
     Output('schedule_wed_div', 'style'),
     Output('schedule_thu_div', 'style'),
     Output('schedule_fri_div', 'style'),
     Output('schedule_sat_div', 'style')],
    [Input('weekdays-tabs', 'value')],
)
def update_tab_display(tab):
    ctx = dash.callback_context
    if ctx.triggered and 'weekdays-tabs' in ctx.triggered[0]['prop_id']:
        styles = []
        for t in ['tab-mon', 'tab-tue', 'tab-wed', 'tab-thu', 'tab-fri', 'tab-sat']:
            styles.append({'display': 'block' if t == tab else 'none'})
        return styles[:]
    return [{'display': 'none'}] * 6


@app.callback(
    [Output('datatable-interactivity', 'data'),
     Output('datatable-interactivity', 'derived_virtual_data')],
    [Input('add-row-button', 'n_clicks'),
     Input('delete-rows-button', 'n_clicks'),
     State('datatable-interactivity', 'derived_virtual_indices'),
     State('datatable-interactivity', 'data')]
)
def alter_row(add_n_clicks, delete_n_clicks, selected_rows, rows):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else ""

    if input_id == 'add-row-button':
        rows.append(
            {'Subject': '', 'Number':'', 'CRN': '', 'Section': '', 'S': 'A',
             'Campus': '', 'Title': '', 'Credit': '', 'Max': '', 'Enrolled': '', 'Days': '',
             'Time': '', 'Loc': 'TBA', 'Begin/End': '', 'Instructor': ',',
             'colorRec': '#b3cde3'}
        )

    if input_id == 'delete-rows-button' and selected_rows and len(selected_rows) != len(rows):
        for row in selected_rows[::-1]:
            rows.pop(row)

    return rows, rows


@app.callback(
    [Output('filter-query-input-container', 'style'),
     Output('filter-query-output', 'style'),
     Output('filter-query-output', 'children')],
    [Input('filter-query-dropdown', 'value'),
     Input('datatable-interactivity', 'filter_query')],
)
def query_input_output(val, query):
    if val == 'custom':
        input_style = {'marginLeft': '0px', 'width': '100%', 'display': 'inline-block'}
        output_style = {'display': 'none'}
    else:
        input_style = {'display': 'none'}
        output_style = {'display': 'inline-block', 'width': '100%'}
    return input_style, output_style , html.P('filter_query = "{}"'.format(query)),


@app.callback(
    [Output('datatable-interactivity', 'filter_query')],
    [Input('apply_query_button', 'n_clicks'),
     Input('filter-query-input', 'n_submit'),
     State('filter-query-dropdown', 'value'),
     State('filter-query-input', 'value')]
)
def apply_query(n_clicks, n_submit, dropdown_value, input_value):
    if n_clicks or n_submit:
        if dropdown_value == 'custom':
            return [input_value]
        else:
            if dropdown_value is None:
                return ['']
            return [dropdown_value]


@app.callback(
    Output('datatable-download', 'data'),
    [Input('export-all-button', 'n_clicks'),
     State('datatable-interactivity', 'data')]
)
def export_all(n_clicks, data):
    df = pd.DataFrame(data)
    if n_clicks > 0 and not df.empty:
        report_term = detect_academic_term(df)
        term_code = convert_term_title_to_code(report_term)
        return {'base64': True,
                'content': to_excel(df, report_term),
                'filename': "SWRCGSR_{0}.xlsx".format(term_code)}


@app.callback(
    Output('datatable-filtered-download', 'data'),
    [Input('export-filtered-button', 'n_clicks'),
     State('datatable-interactivity', 'derived_virtual_data')]
)
def export_filtered(n_clicks, data):
    df = pd.DataFrame(data)
    if n_clicks > 0 and not df.empty:
        report_term = detect_academic_term(df)
        term_code = convert_term_title_to_code(report_term)
        return {'base64': True,
                'content': to_excel(df, report_term),
                'filename': "SWRCGSR_{0}.xlsx".format(term_code)}

@dash.callback(
    Output('download-pdf-channel', 'data'),
    [Input('btn-pdf-instructor', 'n_clicks'),
     Input('btn-pdf-course', 'n_clicks')],
    State('datatable-interactivity', 'data'),
    prevent_initial_call=True
)
def handle_pdf_exports(inst_clicks, course_clicks, filtered_data):
    if not filtered_data:
        return dash.no_update

    trigger_id = dash.ctx.triggered_id
    if not trigger_id:
        return dash.no_update

    df = pd.DataFrame(filtered_data)

    # Remove canceled classes (Keep only active status 'A')
    if 'S' in df.columns:
        df = df[df['S'].astype(str).str.strip() == 'A']

    # Normalize missing columns to prevent ReportLab index formatting crashes
    if 'Class' not in df.columns and 'Subject' in df.columns and 'Number' in df.columns:
        df['Class'] = df['Subject'].astype(str) + " " + df['Number'].astype(str)

    # Reconstruct layout strings from parsed 'Loc' column fields if separate tags don't exist
    if 'Loc' in df.columns and 'Bldg' not in df.columns:
        df['Bldg'] = df['Loc'].astype(str).apply(lambda x: x.split()[0] if len(x.split()) > 0 else 'ONLI')
        df['Room'] = df['Loc'].astype(str).apply(lambda x: x.split()[1] if len(x.split()) > 1 else '')

    pdf_buffer = io.BytesIO()

    # Run the dynamic visual block building loop directly from your previous standalone setup
    if trigger_id == 'btn-pdf-instructor':
        report_term = detect_academic_term(df)
        build_grouped_replica_pdf(df, 'Instructor', report_term, pdf_buffer)
        pdf_buffer.seek(0)
        return dcc.send_bytes(pdf_buffer.read(), "Schedule_By_Instructor.pdf")

    elif trigger_id == 'btn-pdf-course':
        report_term = detect_academic_term(df)
        build_grouped_replica_pdf(df, 'Class', report_term, pdf_buffer)
        pdf_buffer.seek(0)
        return dcc.send_bytes(pdf_buffer.read(), "Schedule_By_Course.pdf")

    return dash.no_update

@app.callback(
    [Output("total_sections_text", "children"),
     Output("total_courses_text", "children"),
     Output("total_credits_text", "children"),
     Output("total_enrollment_text", "children"),
     Output("total_CHP_text", "children"),
     Output("avg_enrollment_text", "children"),
     Output("avg_fill_rate_text", "children"),
     Output("avg_waitlist_text", "children"),
     Output('calc_row', 'children')],
    [Input('datatable-interactivity', 'derived_viewport_data'),
     State('datatable-interactivity', 'data')]
)
def update_analytics_dashboard_metrics(viewport_data, all_data):
    if not viewport_data:
        return ["0", "0", "0", "0", "0.00", "0.00%", "0.00", "0.00", html.Div()]

    df_view = pd.DataFrame(viewport_data)
    df_all = pd.DataFrame(all_data)

    # 1. Protect calculations against empty string fields or non-numeric types
    sections_count = str(df_view["CRN"].nunique()) if "CRN" in df_view.columns else "0"

    if "Subject" in df_view.columns and "Number" in df_view.columns:
        df_view["Course"] = df_view["Subject"].astype(str) + df_view["Number"].astype(str)
        courses_count = str(df_view["Course"].nunique())
    else:
        courses_count = "0"

    credits_sum = "{:,.0f}".format(pd.to_numeric(df_view["Credit"], errors='coerce').sum()) if "Credit" in df_view.columns else "0"
    chp_sum = "{:,.0f}".format(pd.to_numeric(df_view["CHP"], errors='coerce').sum()) if "CHP" in df_view.columns else "0"
    enrl_sum = "{:,.0f}".format(pd.to_numeric(df_view["Enrolled"], errors='coerce').sum()) if "Enrolled" in df_view.columns else "0"

    avg_enrl = round(pd.to_numeric(df_view["Enrolled"], errors='coerce').mean(), 2) if "Enrolled" in df_view.columns else 0.0
    avg_fill = f"{round(pd.to_numeric(df_view['Ratio'], errors='coerce').mean(), 2)}%" if "Ratio" in df_view.columns else "0.00%"
    avg_wlst = round(pd.to_numeric(df_view["WLst"], errors='coerce').mean(), 2) if "WLst" in df_view.columns else 0.0

    # avg_inst = 0.0
    # if "Instructor" in df_view.columns and "Enrolled" in df_view.columns:
        # df_view["Enrolled"] = pd.to_numeric(df_view["Enrolled"], errors='coerce').fillna(0)
        # inst_groups = df_view.groupby("Instructor")["Enrolled"].sum()
        # if not inst_groups.empty:
            # avg_inst = round(inst_groups.mean(), 2)

    # 2. Re-trigger layout distribution boxes dynamically
    matrices_layout = create_calc_row_layout(df_view, df_all)

    return [
        sections_count, courses_count, credits_sum, enrl_sum, chp_sum,
        avg_enrl, avg_fill, avg_wlst, matrices_layout
    ]

@app.callback(
    [Output('max_v_enrl_by_crn_graph', 'figure'),
     Output('max_v_enrl_by_course_graph', 'figure'),
     Output('enrl_by_instructor_graph', 'figure'),
     Output('chp_by_course_graph', 'figure')],
    [Input('datatable-interactivity', 'derived_viewport_data')]
)
def update_analytics_plots_visualization(viewport_data):
    if not viewport_data:
        blank = blankFigure()
        return [blank, blank, blank, blank]

    df = pd.DataFrame(viewport_data).copy()

    # Clean workspace typing data constraints
    df["Credit"] = pd.to_numeric(df["Credit"], errors='coerce').fillna(0)
    df["Enrolled"] = pd.to_numeric(df["Enrolled"], errors='coerce').fillna(0)
    df["Max"] = pd.to_numeric(df["Max"], errors='coerce').fillna(0)
    df["CHP"] = pd.to_numeric(df["CHP"], errors='coerce').fillna(0)
    df["Ratio"] = pd.to_numeric(df["Ratio"], errors='coerce').fillna(0)
    df_active = df[df["Credit"] != 0].copy()

    # Convert CRN from integer/float format to string type for a categorical X-axis
    df_active["CRN"] = df_active["CRN"].astype(str)

    # Sort records descending based on the Max metric
    df_active = df_active.sort_values(by="Max", ascending=False)

    # Define explicitly mapped colors for Max & Enrolled groups
    custom_colors = {"Max": "#00447c", "Enrolled": "#b22222"}

    # Plot 1: Sections Bar Chart Setup
    fig_crn = (
        px.bar(
            df_active,
            x="CRN",
            y=["Max", "Enrolled"],
            color_discrete_map = {"Max": '#00447c', "Enrolled": '#d11242'},
            title="Enrollment per Section",
            hover_name="CRN",
            hover_data={
                "Course": True,
                "CRN": False,
                "Instructor": True,
                "Ratio": ':0.1f',
                "variable": False,
                "WLst": True,
            },
        )
        .update_xaxes(categoryorder="max descending", showticklabels=True)
        .update_layout(
            showlegend=False,
            xaxis_type="category",
            yaxis_title="Enrolled",
            barmode="overlay",
        )
    )

    # Plot 2: Course Bar Chart Setup
    if "Course" not in df_active.columns and "Subject" in df_active.columns and "Number" in df_active.columns:
        df_active["Course"] = df_active["Subject"].astype(str) + df_active["Number"].astype(str)

    df_course = df_active.groupby("Course").agg({"Enrolled": "sum", "Max": "sum", "Ratio": "mean", "WLst": "sum"}).reset_index()
    fig_course = (
        px.bar(
            df_course,
            x="Course",
            y=["Max", "Enrolled"],
            color_discrete_map = {"Max": '#00447c', "Enrolled": '#d11242'},
            title="Enrollment per Course",
            hover_data={"Ratio": ':0.1f', "WLst": True},
        )
        .update_layout(
            showlegend=False,
            xaxis_type="category",
            yaxis_title="Enrolled",
            barmode="overlay",
        )
    )

    # Plot 3: Instructor Bar Chart Setup
    fig_inst = (
            px.bar(
                df,
                x="Instructor",
                y="Enrolled",
                color="Ratio",
                title="Enrollment by Instructor",
                color_continuous_scale=['#d11242', '#717073', '#00447c'],
                hover_name="CRN",
                hover_data={
                    "Course": True,
                    "Enrolled": True,
                    "Instructor": True,
                    "Ratio": False,
                    },
                )
            .update_xaxes(categoryorder="category ascending")
            .update_layout(showlegend=False, xaxis_type="category")
            )

    # Plot 4: Credit Hour Production Breakdown
    fig_chp = (
            px.bar(
                df,
                x="Course",
                y="CHP",
                title="Credit Hour Production by Course",
                color="Ratio",
                color_continuous_scale=['#d11242', '#717073', '#00447c'],
                hover_data={
                    "Course": True,
                    "CHP": True,
                    "Ratio": ':0.1f',
                    }
                )
            .update_xaxes(categoryorder="category descending")
            .update_layout(showlegend=False)
            )
    return [fig_crn, fig_course, fig_inst, fig_chp]

@app.callback(
    Output('enrl_by_instructor', 'children'),
    [Input('datatable-interactivity', 'derived_viewport_data')]
)
def enrl_by_instructor(data):
    if data:
        df = pd.DataFrame(data).copy()
        df = df[df["Credit"] != 0]
        _df = (
            df.groupby("Instructor")
            .agg(enrl_sum=("Enrolled", "sum"), enrl_avg=("Enrolled", "mean"))
            .rename(columns={"enrl_sum":"Total", "enrl_avg":"Avg"})
            .sort_values(("Instructor"), ascending=True)
            .reset_index()
        )
        _df["Avg"] = _df["Avg"].round(2)
        children = [
            html.H6(
                "Enrollment by Instructor",
                id="enrollment_by_instructor_id",
            ),
            dash_table.DataTable(
                id="enrollment_data_table",
                columns=[
                    {"name": i, "id": i}
                    for i in _df.columns
                ],
                data=_df.to_dict("records"),
                fixed_rows={"headers": True, "data": 0},
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)",
                    }
                ],
                style_header={
                    "backgroundColor": "rgb(230, 230, 230)",
                    "fontWeight": "bold",
                },
                page_action="none",
                sort_action="native",
                style_table={"height": "400px", "overflowY": "auto"},
                style_cell={"font-family": "sans-serif"},
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'Instructor'},
                        'textAlign': 'left',
                        'minWidth': '50%', 'width': '50%', 'maxWidth': '50%',
                        'whiteSpace': 'normal'
                    },
                    {
                        'if': {'column_id': 'Total'},
                        'minWidth': '25%', 'width': '25%', 'maxWidth': '25%',
                        'whiteSpace': 'normal'
                    },
                    {
                        'if': {'column_id': 'Avg'},
                        'minWidth': '25%', 'width': '25%', 'maxWidth': '25%',
                        'whiteSpace': 'normal'
                    },
                ]
            ),
        ]
        return children
    else:
        return []

@app.callback(
    Output('chp_by_course', 'children'),
    [Input('datatable-interactivity', 'derived_viewport_data')]
)
def chp_by_course(data):
    if data:
        df = pd.DataFrame(data).copy()
        df = df[df["Credit"] != 0]
        _df = df.groupby("Course").agg(
            {"CHP": "sum", "Enrolled": "sum", "Max": "sum"}
        ).sort_values(
            ("Course"),
            ascending=True
        ).reset_index()
        children = [
            html.H6("Course CHP and Enrollment", id="chp_by_course_id"),
            dash_table.DataTable(
                id="chp_by_course_data_table",
                columns=[
                    {"name": i, "id": i}
                    for i in _df.columns
                ],
                data=_df.to_dict("records"),
                fixed_rows={"headers": True, "data": 0},
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)",
                    }
                ],
                style_header={
                    "backgroundColor": "rgb(230, 230, 230)",
                    "fontWeight": "bold",
                },
                page_action="none",
                sort_action="native",
                style_table={"height": "400px", "overflowY": "auto"},
                style_cell={"font-family": "sans-serif"},
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'Course'},
                        'textAlign': 'left',
                        'minWidth': '25%', 'width': '25%', 'maxWidth': '25%',
                        'whiteSpace': 'normal'
                    },
                    {
                        'if': {'column_id': 'CHP'},
                        'minWidth': '25%', 'width': '25%', 'maxWidth': '25%',
                        'whiteSpace': 'normal'
                    },
                    {
                        'if': {'column_id': 'Enrolled'},
                        'minWidth': '25%', 'width': '25%', 'maxWidth': '25%',
                        'whiteSpace': 'normal'
                    },
                    {
                        'if': {'column_id': 'Max'},
                        'minWidth': '25%', 'width': '25%', 'maxWidth': '25%',
                        'whiteSpace': 'normal'
                    },
                ]
            ),
        ]
        return children
    else:
        return []


@app.callback(
    Output('graph_f2f', 'figure'),
    [Input('datatable-interactivity', 'derived_viewport_data'),
     Input('enrollment-max-actual', 'value'),],
    State('graph_f2f', 'figure'),
)
def graph_f2f(data, toggle, fig):
    if data:
        df = pd.DataFrame(data).copy()
        df = df[df["Credit"] != 0]

        # remove the zero credit hour sections
        df = df[pd.to_numeric(df["Credit"], errors='coerce')>0]

        # capture all ASYNC meaning ({'Campus'} == 'I' && {'Time'} == 'TBA') || ({'Campus'} == 'M' && {'Time'} == 'TBA' && ({'Loc'} == 'ASYN' || {'Loc'} == 'ONLI' || {'Loc'} == 'MOST'))
        i_df = df[df['Campus'] == 'I']
        mask = i_df[i_df['Time'].str.contains('TBA')].index.to_list()
        i_df = df[df['Campus'] == 'M']
        i_df =i_df[i_df['Time'].str.contains('TBA')]
        mask += i_df[i_df['Loc'].str.contains('ASYN') | i_df['Loc'].str.contains('ONLI') | i_df['Loc'].str.contains('MOST')].index.to_list()
        a = df.loc[mask]

        # capture all SYNC meaning ({'Campus'} == 'I' && {'Time'} != 'TBA') || ({'Campus'} == 'M' && {'Loc'} == 'SYNC')
        i_df = df[df['Campus'] == 'I']
        mask = i_df[~i_df['Time'].str.contains('TBA')].index.to_list()
        i_df = df[df['Campus'] == 'M']
        mask += i_df[i_df['Loc'].str.contains('SYNC')].index.to_list()
        s = df.loc[mask]

        if toggle in ["Max", "Enrolled"]:
            a = a[toggle].sum()
            s = s[toggle].sum()
            t = df[toggle].sum()

            fig = make_subplots(rows=2,
                                cols=1,
                                specs=[[{'type':'domain'}], [{'type':'domain'}]],
                                vertical_spacing=0.15,
                               )
            fig.add_trace(go.Pie(labels=["Async", "Sync"],
                                 values=[a, s],
                                 marker_colors=['#00447c', '#d11242'],
                                 name="Async vs Sync"),
                          1, 1)
            fig.add_trace(go.Pie(labels=["F2F", "Online"],
                                 values=[t-(a+s), a+s],
                                 marker_colors=['#00447c', '#d11242'],
                                 name="F2F vs Online"),
                          2, 1)
            fig.update_traces(hole=.7, hoverinfo="label+value+percent")

            return fig.update_layout(
                title_text=toggle +" Ratios",
                showlegend=False,
                annotations=[
                    dict(
                        text='Async<br />vs<br />Sync',
                        x=0.5, y=0.785,
                        font_size=10,
                        showarrow=False,
                        xanchor = "center",
                        yanchor = "middle",
                    ),
                    dict(
                        text='F2F<br />vs<br />Online',
                        x=0.5, y=0.215,
                        font_size=10,
                        showarrow=False,
                        xanchor = "center",
                        yanchor = "middle",
                    )
                ]
            )

        if toggle in ["Section"]:
            a = a[toggle].count()
            s = s[toggle].count()
            t = df[toggle].count()

            fig = make_subplots(rows=2,
                                cols=1,
                                specs=[[{'type':'domain'}], [{'type':'domain'}]],
                                vertical_spacing=0.15,
                               )
            fig.add_trace(go.Pie(labels=["F2F", "Online"],
                                 values=[t-(a+s), a+s],
                                 marker_colors=['#00447c', '#d11242'],
                                 name="F2F vs Online"),
                          2, 1)
            fig.update_traces(hole=.7, hoverinfo="label+value+percent")


            return fig.update_layout(
                title_text=toggle +" Ratios",
                showlegend=False,
                annotations=[
                    dict(
                        text='',
                        x=0.5, y=0.785,
                        font_size=10,
                        showarrow=False,
                        xanchor = "center",
                        yanchor = "middle",
                    ),
                    dict(
                        text='F2F<br />vs<br />Online',
                        x=0.5, y=0.215,
                        font_size=10,
                        showarrow=False,
                        xanchor = "center",
                        yanchor = "middle",
                    )
                ]
            )
    else:
        return fig


# Main
if __name__ == '__main__':
    app.run(debug=DEBUG, port='8001')
