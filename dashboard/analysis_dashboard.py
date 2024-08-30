# -*- coding: utf-8 -*-

from utilities import *

import dash
from dash import html, dcc, dash_table
import numpy as np
import plotly.express as px
import base64
import io
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


DEBUG = False
mathserver = False

# Initialize server
app = dash.Dash(
    __name__,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width'}],
    prevent_initial_callbacks=True,
)

server = app.server

app.title = 'Analysis'

app.config.update({
    'suppress_callback_exceptions': True,
})

# specifics for the math.msudenver.edu server
if mathserver:
    app.config.update({
       'url_base_pathname':'/analysis/',
       'routes_pathname_prefix':'/analysis/',
       'requests_pathname_prefix':'/analysis/',
    })


def instructor_rank(df, name, term, print_rank=False):
    a = df.loc[df['Instructor']==name].values.flatten().tolist()[1:]

    try:
        b = np.array([term - _a for _a in a])
        rank_index = np.where(np.isclose(b,b[b>=0].min()))[0]
        if rank_index > 4:
            rank_desc = 'Professor'
        elif rank_index > 3:
            rank_desc = 'Associate Professor'
        elif rank_index > 2:
            rank_desc = 'Assistant Professor'
        elif rank_index > 1:
            rank_desc = 'Senior Lecturer'
        elif rank_index > 0:
            rank_desc = 'Lecturer'
        else:
            rank_desc = 'Adjunct'


    except ValueError:
        rank_desc = 'NAN'
        rank_index = 0
        # rank_index = -1

    if print_rank:
        print(rank_desc)

    return rank_index



def assignRank(df):
    if DEBUG:
        print("function: assignRank")
    _a = [
        ["Boneh, S",          0,       0,       0,       0,       0,       201150],
        ["Bouwmeester, H",    200830,  0,       0,       201650,  202250,  0],
        ["Carter, J",         0,       0,       0,       201050,  201750,  202250],
        ["Davis, D",          0,       0,       0,       200750,  201250,  201850],
        ["Dyhr, B",           0,       0,       0,       201050,  201650,  202250],
        ["Ethier, J",         0,       0,       0,       200850,  201450,  202050],
        ["Evans, B",          0,       0,       0,       200350,  200950,  201650],
        ["Fry, B",            0,       0,       0,       201650,  202050,  0],
        ["Gilmore, D",        0,       0,       0,       0,       0,       200050],
        ["Grevstad, N",       0,       0,       0,       200350,  200950,  201550],
        ["Harder, C",         0,       0,       0,       201150,  201750,  0],
        ["Heer, H",           0,       201450,  0,       0,       0,       0],
        ["Koester, M",        0,       0,       0,       201050,  201650,  202150],
        ["Li, Y",             0,       0,       0,       202350,  0,       0],
        ["McKenna, P",        0,       0,       0,       200050,  200650,  201650],
        ["Mocanasu, M",       0,       0,       0,       200950,  201450,  201950],
        ["Niemeyer, R",       0,       0,       0,       201950,  202350,  0],
        ["Poole, S",          0,       0,       0,       201450,  201950,  202350],
        ["Ribble, E",         0,       0,       0,       201350,  201750,  202150],
        ["Ruch, D",           0,       0,       0,       199450,  200050,  200650],
        ["Sundbye, L",        0,       0,       0,       200050,  200650,  201950],
        ["Schaeffer Fry,",    0,       0,       0,       201350,  201750,  202250],
        ["Bertram, J",        201150,  201750,  202050,  0,       0,       0],
        ["Freeman, A",        0,       202150,  0,       0,       0,       0],
        ["Schauble, J",       200850,  201550,  202150,  0,       0,       0],
        ["Kuang, Y",          201130,  0,       0,       0,       0,       0],
        ["Azeem, S",          201150,  0,       0,       0,       0,       0],
        ["Jabri, A",          202030,  0,       0,       0,       0,       0],
        ["Janowiak-Mille",    200950,  0,       0,       0,       0,       0],
        ["Karaoglu, M",       201950,  0,       0,       0,       0,       0],
        ["Kirk, Z",           200830,  0,       0,       0,       0,       0],
        ["Nguyen, D",         201730,  0,       0,       0,       0,       0],
        ["Burke, J",          201850,  0,       0,       0,       0,       0],
        ["Van Camp, T",       200850,  0,       0,       0,       0,       0],
        ["Weiss, M",          201650,  0,       0,       0,       0,       0],
        ["Yang, Q",           0,       200650,  201150,  0,       0,       0],
        ["Zarrini, H",        200950,  0,       0,       0,       0,       0],
        ["Linnen, L",         200940,  0,       0,       0,       0,       0],
        ["Aveyard, R",        200830,  0,       0,       0,       0,       0],
        ["Yokomizo, G",       200830,  0,       0,       0,       0,       0],
        ["Slotta, O",         201050,  0,       0,       0,       0,       0],
        ["Henningsen, G",     200830,  0,       0,       0,       0,       0],
        ["Jadunath, G",       201030,  0,       0,       0,       0,       0],
        ["Brones, J",         200830,  0,       0,       0,       0,       0],
        ["Jovic, S",          201130,  0,       0,       0,       0,       0],
        ["Foster, E",         0,       200930,  201450,  0,       0,       0],
        ["Gregory, M",        200830,  0,       0,       0,       0,       0],
        ["Pfeiffer, T",       201130,  0,       0,       0,       0,       0],
        ["Flanders, H",       200830,  0,       0,       0,       0,       0],
        ["Hindie, J",         200830,  0,       0,       0,       0,       0],
        ["Prevot, K",         0,       0,       0,       200250,  200450,  200850],
        ["Monash, E",         200830,  0,       0,       0,       0,       0],
        ["Omar, F",           200830,  0,       0,       0,       0,       0],
        ["Burgdorff, V",      200830,  0,       0,       0,       0,       0],
        ["Lemay, N",          200830,  0,       0,       0,       0,       0],
        ["Bierling, A",       200830,  0,       0,       0,       0,       0],
        ["Glass, C",          200830,  0,       0,       0,       0,       0],
        ["Craft, M",          200830,  0,       0,       0,       0,       0],
        ["Packer, L",         0,       0,       0,       200250,  200450,  200850],
        ["Aaker, B",          200830,  0,       0,       0,       0,       0],
        ["Emerson, W",        0,       0,       0,       200250,  200450,  200850],
        ["Verbsky, A",        200830,  0,       0,       0,       0,       0],
        ["Victor, J",         200830,  0,       0,       0,       0,       0],
        ["Loats, J",          0,       0,       0,       200250,  200450,  200850],
        ["Dollard, C",        0,       0,       0,       200050,  200450,  200850],
        ["DuMaine, P",        200830,  0,       0,       0,       0,       0],
        ["Zakotnik-Gutie",    0,       201750,  0,       0,       0,       0],
        ["Peddicord, J",      200830,  0,       0,       0,       0,       0],
        ["Hector, D",         200830,  0,       0,       0,       0,       0],
        ["Wohlen, S",         200830,  0,       0,       0,       0,       0],
        ["Pillitteri, O",     200830,  0,       0,       0,       0,       0],
        ["Jensen, K",         200830,  0,       0,       0,       0,       0],
        ["Zolnikov, K",       200830,  0,       0,       0,       0,       0],
        ["Nazeri, H",         200830,  0,       0,       0,       0,       0],
        ["Parenti, V",        200830,  0,       0,       0,       0,       0],
        ["Williams, K",       200830,  201550,  201950,  0,       0,       0],
        ["Sefton, R",         200830,  0,       0,       0,       0,       0],
        ["Swanson, J",        200830,  0,       0,       0,       0,       0],
        ["Wo, S",             200830,  0,       0,       0,       0,       0],
        ["Coates, S",         200830,  0,       0,       0,       0,       0],
        ["Van Dine, D",       200830,  0,       0,       0,       0,       0],
        ["DeBay, D",          200830,  0,       0,       0,       0,       0],
        ["Klie, D",           200830,  0,       0,       0,       0,       0],
        ["Wray, S",           200830,  0,       0,       0,       0,       0],
        ["Zerwick, A",        200830,  0,       0,       0,       0,       0],
        ["Anderson, B",       200830,  0,       0,       0,       0,       0],
        ["Cline, E",          200830,  0,       0,       0,       0,       0],
        ["Baouchi, A",        200830,  0,       0,       0,       0,       0],
        ["Mlynar, K",         200830,  0,       0,       0,       0,       0],
        ["Terry, M",          200830,  201850,  0,       0,       0,       0],
        ["Konuk, N",          200830,  0,       0,       201850,  0,       0],
        ["Husseini, G",       200830,  0,       0,       0,       0,       0],
        ["Watson, W",         200830,  0,       0,       0,       0,       0],
        ["Butcher, L",        200830,  0,       0,       0,       0,       0],
        ["Benson, D",         200830,  0,       0,       0,       0,       0],
        ["Nguyen, M",         200830,  0,       0,       0,       0,       0],
        ["Hu, J",             200830,  0,       0,       0,       0,       0],
        ["Ruiz, J",           200830,  0,       0,       0,       0,       0],
        ["McClellan, T",      200830,  0,       0,       0,       0,       0],
        ["Padgett, C",        200830,  0,       0,       0,       0,       0],
        ["Pryor, F",          200830,  0,       0,       0,       0,       0],
        ["Burr, G",           200830,  0,       0,       0,       0,       0],
        ["Naylor, R",         200830,  0,       0,       0,       0,       0],
        ["Darji, K",          200830,  0,       0,       0,       0,       0],
        ["Reichlin, S",       200830,  0,       0,       0,       0,       0],
        ["Dinh, H",           200830,  0,       0,       0,       0,       0],
        ["Khan, M",           200830,  0,       0,       0,       0,       0],
        ]

    rank_df = pd.DataFrame(_a)
    rank_df.columns = ['Instructor', 'Adjunct', 'Lecturer', 'Senior Lecturer', \
                       'Assistant Professor', 'Associate Professor', 'Professor']


    df.insert(len(df.columns), 'Rank', 0)
    for row in df.index.to_list():
        name = df.loc[row, 'Instructor']
        term = int(df.loc[row, 'Term'])
        df.loc[row, 'Rank'] = instructor_rank(rank_df, name, term, False)

    return df


def tidy_xlsx(file_contents):
    if DEBUG:
        print("function: tidy_xlsx")
    """ Converts an Excel Spreadsheet

    Make sure that you copy and paste all data as values before trying to import.

    Args:
        file_contents:
            input decoded filestream of SWRCGSR output from an uploaded textfile.

    Returns:
        Dataframe.
    """

    _df = pd.read_excel(file_contents,
                        engine='openpyxl',
                        converters={
                            'Term':str,
                            'Subject':str,
                            'Number':str,
                            'CRN':str,
                            'Section':str,
                            'Campus':str,
                            'Title':str,
                            'Days':str,
                            'Time':str,
                            'Loc':str,
                            'Instructor':str,
                        },
                       )

    # create missing columns, if necessary
    if not 'S' in _df.columns:
        _df.insert(len(_df.columns), 'S', 'A')
    if not 'Begin/End' in _df.columns:
        _df.insert(len(_df.columns), 'Begin/End', '01/01-01/01')
    if not 'Max' in _df.columns:
        _df.insert(len(_df.columns), 'Max', 1)
    if not 'Credit' in _df.columns:
        _df.insert(len(_df.columns), 'Credit', 3)

    _df.rename(
        columns={
            'Subj': 'Subject',
            'Nmbr': 'Number',
            'Sec': 'Section',
            'Cam': 'Campus',
            'Enrl': 'Enrolled',
            'WLst': 'WList',
            '%Ful': 'Full',
        },
        inplace=True,
    )

    _df = _df[['Term', 'Subject', 'Number', 'CRN', 'Section', 'S', 'Campus', 'Title',
              'Credit', 'Enrolled', 'Days', 'Time', 'Loc', 'Instructor']]

    _df = assignRank(_df)

    _df = _df[_df['Credit']>0]
    _df = _df[_df['Enrolled']>0]

    _df.insert(len(_df.columns), "SUF", "S")
    for row in _df[_df["Term"].str.endswith("40", na=False)].index.tolist():
        _df.loc[row, "SUF"] = "U"
    for row in _df[_df["Term"].str.endswith("50", na=False)].index.tolist():
        _df.loc[row, "SUF"] = "F"

    _df.loc[:, "CHP"] = _df["Credit"] * _df["Enrolled"]

    _df.insert(len(_df.columns), 'Class', ' ')
    _df['Class'] = _df['Subject'] + ' ' + _df['Number']
    _df = updateTitles(_df)

    # there might be CRNs that are unknown (blank), so fill sequentially starting
    # from 99999 and go down
    i = 1
    for row in _df[_df['CRN'].isna()].index.tolist():
        _df.loc[row, 'CRN'] = str(100000 - i)
        i += 1

    return _df

def parse_contents(contents):#, filename):#, date):
    if DEBUG:
        print("function: parse_contents")

    _, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        df = tidy_xlsx(io.BytesIO(decoded))
        return df
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])



def create_datatable(df):
        return [
            dash_table.DataTable(
                id='datatable',
                columns=[{'name': n, 'id': i} for n,i in zip([
                    'Term', 'Subj', 'Nmbr', 'CRN', 'Sec', 'S', 'Cam', 'Title', 'Credit',
                    'Enrl', 'Days', 'Time', 'Loc', 'Instructor', 'Rank'
                ],[ *df.columns ])],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                },
                style_cell={'font-family': 'sans-serif', 'font-size': '1rem'},
                style_cell_conditional=[
                    {
                        'if': {'column_id': i},
                        'textAlign': 'left',
                        'minWidth': w, 'width': w, 'maxWidth': w,
                        'whiteSpace': 'normal'
                    }
                    for i,w in zip([ *df.columns ],
                                   ['9%', '5%', '5.5%', '5.5%', '4.5%', '3.5%', '4.5%', '19.5%',
                                    '5.5%', '4.5%', '5.5%', '8%', '5.5%', '11%', '3%'])
                ],
                fixed_rows={'headers': True, 'data': 0},
                page_size=10000,
                virtualization=True,
                data=df.to_dict('records'),
                # editable=True,
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                # row_selectable='multi',
                # row_deletable=True,
                selected_rows=[],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'none',
                },
            )
        ]


# Create app layout
app.layout = html.Div(
    [
        html.Div(
            children = [
                html.Img(id='msudenver-logo',
                         src=app.get_asset_url('msudenver-logo.png')),
                html.H3('Analysis'),
                dcc.Upload(id='upload-data',
                           children=html.Button(['Upload file'],
                                                id='upload-data-button',
                                                n_clicks=0,
                                                style={'height': '38px'},
                                                className='button'),
                           multiple=False,
                           accept='.xlsx'),
            ],
            id='header',
            style={'display': 'flex',
                   'justifyContent': 'space-between',
                   'alignItems': 'center'},
        ),
        html.Div(
            children = [
                dcc.Dropdown(
                    value="",
                    style={'width': '100%', 'display': 'block'},
                    id='x_select_dropdown',
                ),
                dcc.Dropdown(
                    value="",
                    style={'width': '100%', 'display': 'block'},
                    id='y_select_dropdown',
                ),
                dcc.Dropdown(
                    value="sum",
                    options = [{'label': 'Average', 'value': 'mean'},
                               {'label': 'Sum', 'value': 'sum'},
                               {'label': 'Count', 'value': 'count'}],
                    style={'width': '100%', 'display': 'block'},
                    id='agg_function',
                ),
            ],
            style={'display': 'flex'},
            id='dropdowns',
        ),
        html.Div(
            children = [
                html.Fieldset(
                    children = [
                        html.Legend(
                            'Semester',
                        ),
                        dcc.Checklist(
                            options=[
                                {'label': 'Spring', 'value': 'S'},
                                {'label': 'Summer', 'value': 'U'},
                                {'label': 'Fall', 'value': 'F'},
                            ],
                            value=['S', 'U', 'F'],
                            id='semester_checkmark',
                        ),
                    ],
                ),
                html.Fieldset(
                    children = [
                        html.Legend(
                            'Granularity',
                        ),
                        html.Div(
                            children = [
                                dcc.RadioItems(['None', 'Category','Rank'], 'None',id='granular_radioitem')
                            ],
                        ),
                    ],
                ),
                html.Fieldset(
                    children = [
                        html.Legend(
                            'Percentage',
                        ),
                        html.Div(
                            children = [
                                dcc.RadioItems(
                                    options = [
                                        {'label': 'No', 'value': False, 'disabled': False},
                                        {'label': 'Yes', 'value': True, 'disabled': False}
                                    ],
                                    value=False,
                                    id='percentage_radioitem',
                                ),
                            ],
                        ),
                    ],
                ),
                html.Fieldset(
                    children = [
                        html.Legend(
                            'Plot Type',
                        ),
                        html.Div(
                            children = [
                                dcc.RadioItems(
                                    options = [
                                        {'label': 'Bar', 'value': 'bar', 'disabled': False},
                                        {'label': 'Area', 'value': 'area', 'disabled': False}
                                    ],
                                    value='bar',
                                    id='plot_type_radioitem',
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            style={'display': 'flex'},
            id='checkmarks',
        ),
        html.Div([
            dcc.Graph(
                figure = blankFigure(),
            )],
                id="x_vs_y"
        ),
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='filter-query-dropdown',
                    options=[
                        {'label': 'Custom...', 'value': 'custom'},
                        {'label': 'Spring & Fall', 'value': '({SUF}="S" || {SUF}="F")'},
                        {'label': 'Spring', 'value': '{SUF}="S"'},
                        {'label': 'Summer', 'value': '{SUF}="U"'},
                        {'label': 'Fall', 'value': '{SUF}="F"'},
                        {'label': 'Lower Division', 'value': '{Number} < 3000 && {S} contains A'},
                        {'label': 'Upper Division', 'value': '{Number} >= 3000 && {S} contains A'},
                        {'label': 'Active Classes', 'value': '{S} contains A'},
                        {'label': 'Canceled CRNs', 'value': '{S} contains C'},
                        {'label': 'Math w/o Labs', 'value': '{Subject} contains M && {S} contains A && ({Number} < 1081 || {Number} > 1082) && ({Number} != "1101") && ({Number} != "1111") && ({Number} < 1115 || {Number} > 1116) && ({Number} < 1311 || {Number} > 1312)'},
                        {'label': 'Math Labs', 'value': '{Subject} contains M && {S} contains A && ({Number} = 1082 || {Number} = 1101 || {Number} = 1116 || {Number} = 1312)'},
                        {'label': 'Math Labs with Parents', 'value': '{Subject} contains M && {S} contains A && ({Number} = 1081 || {Number} = 1111 || {Number} = 1115 || {Number} = 1311 || {Number} = 1082 || {Number} = 1101 || {Number} = 1116 || {Number} = 1312)'},
                        {'label': 'Applied Group', 'value': '{Subject} contains M && {S} contains A && ({Number} = 3130 || {Number} = 3400 || {Number} = 3420 || {Number} = 3430 || {Number} = 3440 || {Number} = 4480 || {Number} = 4490)'},
                        {'label': 'MathEd Group', 'value': '({S} contains A && {Subject} contains M && ({Number} = 1610 || {Number} = 2620 || {Number} = 3470 || {Number} = 3640 || {Number} = 3650)) || ({S} contains A && {Subject} contains MTL)'},
                        {'label': 'Statistics Group', 'value': '{Subject} contains M && {S} contains A && ({Number} = 3210 || {Number} = 3220 || {Number} = 3230 || {Number} = 3240 || {Number} = 3270 || {Number} = 3510 || {Number} = 4210 || {Number} = 4230 || {Number} = 4250 || {Number} = 4290)'},
                        {'label': 'Theoretical Group', 'value': '{Subject} contains M && {S} contains A && ({Number} = 3100 || {Number} = 3110 || {Number} = 3170 || {Number} = 3140 || {Number} = 4110 || {Number} = 4150 || {Number} = 4410 || {Number} = 4420 || {Number} = 4450)'},
                    ],
                    placeholder='Select a query',
                    value=''),
            ],
                style={'display': 'inline-block', 'width': '100%'}
            ),
            html.Div([
                html.Button('Apply Query', id='apply_query_button', className='button')
            ],
                style={'display': 'inline-block'}
            ),
        ],
            style={'marginTop': '7px', 'marginLeft': '5px', 'display': 'flex',
                   'justifyContent': 'space-between'}
        ),
        html.Div([
            html.Div([
                dcc.Input(id='filter-query-input',
                          placeholder='Enter filter query',
                          className='dcc_control',
                          style={'width': '98.5%'}),
            ],
                id='filter-query-input-container',
                style={'marginLeft': '5px',
                       'width': '100%',
                       'display': 'none'}
            ),
            html.Div(['filter_query = "None"'],
                     id='filter-query-output',
                     style={'display': 'inline-block',
                            'marginLeft': '5px',
                            'width': '100%'}
                    ),
        ],
            style={'marginTop': '15px',
                   'marginBottom': '15px',
                   'marginLeft': '5px',
                   'display': 'flex',
                   'justifyContent': 'space-between'}
        ),
        html.Div(
            [
                html.Div(
                    [],#create_datatable(pd.DataFrame()),
                    style={
                        'width': '100%',
                        'display': 'block',
                        'marginLeft': 'auto',
                        'marginRight': 'auto'
                    },
                    id='datatable-container',
                ),
            ]
        ),
    ],
)


@app.callback(
    [
        Output('x_select_dropdown', 'options'),
        Output('y_select_dropdown', 'options'),
        Output('datatable-container', 'children'),
    ],
    [
        Input('upload-data', 'contents'),
        # State('upload-data', 'filename'),
        State('upload-data-button', 'n_clicks'),
    ]
)
# def initial_data_loading(contents, name, n_clicks):
def initial_data_loading(contents, n_clicks):
    x_options = []
    y_options = []
    data_children = create_datatable(pd.DataFrame())

    if contents is not None and n_clicks > 0:
        df = parse_contents(contents)#, name)
        data_children = create_datatable(df)
        x_options = [{'label': c, 'value': c} for c in df.columns.sort_values()]
        y_options = [{'label': c, 'value': c} for c in df.columns.sort_values()]

    return x_options, y_options, data_children

@app.callback(
    [Output('percentage_radioitem', 'value'),
     Output('agg_function', 'options'),
     Output('agg_function', 'value')],
    [Input('y_select_dropdown', 'value')]
)
def enable_options(y_select_dropdown):

    if y_select_dropdown in ['Credit', 'Enrolled', 'Rank', 'CHP']:
        agg_function_options = [
            {'label': 'Average', 'value': 'mean'},
            {'label': 'Sum', 'value': 'sum'},
        ]
        agg_function_value = 'sum'
    else:
        agg_function_options = [
            {'label': 'Count', 'value': 'count'}
        ]
        agg_function_value = 'count'

    return [False, agg_function_options, agg_function_value]

@app.callback(
    [
        Output('x_vs_y', 'children'),
        # Output('agg_function', 'value'),
    ],
    [
        Input('datatable', 'derived_viewport_data'),
        Input('x_select_dropdown', 'value'),
        Input('y_select_dropdown', 'value'),
        Input('agg_function', 'value'),
        Input('granular_radioitem', 'value'),
        Input('semester_checkmark', 'value'),
        Input('percentage_radioitem', 'value'),
        Input('plot_type_radioitem', 'value'),
    ]
)
def update_graph(data, x_select_dropdown, y_select_dropdown, agg_function, granularValue, semesterValue, percentageValue, plotTypeValue):

    if x_select_dropdown == None or y_select_dropdown == None or x_select_dropdown==y_select_dropdown:
        raise PreventUpdate

    df = pd.DataFrame(data)

    df = df[df['SUF'].isin(semesterValue)]


    # HENC: Can I sort the dataframe per the x_select_dropdown?  Does this make sense?

    df['Rank Desc'] = ''

    orderedTerms = np.sort(df['Term'].unique()).tolist()

    fig = blankFigure()
    categoryOrders={}
    colorDiscreteSequence=[]
    # colorBar = x_select_dropdown
    # bar_mode = "overlay"

    if granularValue == 'Rank':
        categoryOrders={"Term": orderedTerms, "Rank Desc": ['Adjunct', 'Lecturer', 'Senior Lecturer', 'Assistant Professor', 'Associate Professor', 'Professor']}
        colorDiscreteSequence=['#7570B3', '#FC8D62', '#D95F02', '#B3E2CD', '#66C2A5', '#1B9E77']

        df['Rank Desc'] = 'Adjunct'
        for row in df.index.to_list():
            if df.loc[row, 'Rank'] == 5:
                df.loc[row, 'Rank Desc'] = 'Professor'
            elif df.loc[row, 'Rank'] == 4:
                df.loc[row, 'Rank Desc'] = 'Associate Professor'
            elif df.loc[row, 'Rank'] == 3:
                df.loc[row, 'Rank Desc'] = 'Assistant Professor'
            elif df.loc[row, 'Rank'] == 2:
                df.loc[row, 'Rank Desc'] = 'Senior Lecturer'
            elif df.loc[row, 'Rank'] == 1:
                df.loc[row, 'Rank Desc'] = 'Lecturer'

        groupbyColumns = [x_select_dropdown, 'Rank Desc']
        # colorBar="Rank Desc"
        # bar_mode = "stack"

    elif granularValue == 'Category':
        categoryOrders={"Term": orderedTerms, "Rank Desc": ['Adjuncts', 'Cat II (Lecturers)  ', 'Cat I (Professors)  ']}
        colorDiscreteSequence=['#7570B3', '#D95F02', '#1B9E77']

        df['Rank Desc'] = 'Adjuncts'
        for row in df.index.to_list():
            if df.loc[row, 'Rank'] > 2:
                df.loc[row, 'Rank Desc'] = 'Cat I (Professors)  '
            elif df.loc[row, 'Rank'] > 0:
                df.loc[row, 'Rank Desc'] = 'Cat II (Lecturers)  '

        groupbyColumns = [x_select_dropdown, 'Rank Desc']
        # colorBar="Rank Desc"
        # bar_mode = "stack"

    else:
        groupbyColumns = [x_select_dropdown]

    if y_select_dropdown in ['Instructor']:
        df = df[[x_select_dropdown, y_select_dropdown, 'Rank Desc']].drop_duplicates()

    if x_select_dropdown == y_select_dropdown:
        _df = df.groupby(groupbyColumns).agg({y_select_dropdown: agg_function}).rename_axis(x_select_dropdown + '_1').reset_index()
    else:
        _df = df.groupby(groupbyColumns).agg({y_select_dropdown: agg_function}).reset_index()

    # print( 100*_df[y_select_dropdown] / _df.groupby(x_select_dropdown)[y_select_dropdown].transform(sum))
    # print("\n\nLine 1:", 100*_df[y_select_dropdown])
    # print("\n\nLine 2:", _df.groupby(x_select_dropdown)[y_select_dropdown].transform(sum))
    # # print(_df['Percentage'].to_string())
    if percentageValue:
        _df['Percentage'] = 100*_df[y_select_dropdown] / _df.groupby(x_select_dropdown)[y_select_dropdown].transform(sum)
        Y = 'Percentage'
    else:
        Y = y_select_dropdown

    str_title = x_select_dropdown + " vs " + y_select_dropdown + " (" + agg_function + ")"
    # # hoverData={"Rank Desc": False, "Term": False}

    fig = blankFigure()

    try:
        hoverTemplate='%{y:.1f}'
        if plotTypeValue == 'area':
            fig = (
                px.area(
                    _df,
                    x=x_select_dropdown,
                    y=Y,
                    # y=[y_select_dropdown],
                    title=str_title,
                    # color=colorBar,
                    color="Rank Desc",
                    category_orders=categoryOrders,
                    color_discrete_sequence=colorDiscreteSequence,
                    # hover_data=hoverData,
                )
            )
        else:
            fig = (
                px.bar(
                    _df,
                    x=x_select_dropdown,
                    y=Y,
                    # y=[y_select_dropdown],
                    title=str_title,
                    # color=colorBar,
                    color="Rank Desc",
                    category_orders=categoryOrders,
                    color_discrete_sequence=colorDiscreteSequence,
                    # hover_data=hoverData,
                )
            )


        print(_df.to_string())

        fig.update_traces(
            hovertemplate=hoverTemplate,
        )
        fig.update_xaxes(showticklabels=True)
        fig.update_layout(
            showlegend=True,
            xaxis_type="category",
            yaxis_title=y_select_dropdown,
            barmode="stack",
        )
    except:
        if plotTypeValue == 'area':
            fig = (
                px.area(
                    _df,
                    x=x_select_dropdown,
                    y=Y,
                    title=str_title,
                )
            )
        else:
            fig = (
                px.bar(
                    _df,
                    x=x_select_dropdown,
                    y=Y,
                    title=str_title,
                )
            )
        fig.update_xaxes(showticklabels=True)
        fig.update_yaxes(rangemode="tozero")
        fig.update_layout(
            showlegend=False,
            xaxis_type="category",
            yaxis_title=y_select_dropdown,
            barmode="overlay",
        )
            # px.bar(
            #     _df,
            #     x=x_select_dropdown,
            #     y=Y,
            #     title=str_title,
            # )
            # .update_xaxes(showticklabels=True)
            # .update_layout(
            #     showlegend=False,
            #     xaxis_type="category",
            #     yaxis_title=y_select_dropdown,
            #     barmode="overlay",
            # )
        # )

    return [dcc.Graph( figure = fig,)]#, agg_function

@app.callback(
    [Output('filter-query-input-container', 'style'),
     Output('filter-query-output', 'style'),
     Output('filter-query-output', 'children')],
    [Input('filter-query-dropdown', 'value'),
     Input('datatable','filter_query')],
)
def query_input_output(val, query):
    if DEBUG:
        print("function: query_input_output")
    if val == 'custom':
        input_style = {'marginLeft': '0px', 'width': '100%', 'display': 'inline-block'}
        output_style = {'display': 'none'}
    else:
        input_style = {'display': 'none'}
        output_style = {'display': 'inline-block',
                        'marginLeft': '5px',
                        'width': '100%'}
    return input_style, output_style , html.P('filter_query = "{}"'.format(query)),

@app.callback(
    [Output('datatable', 'filter_query')],
    [Input('apply_query_button', 'n_clicks'),
     Input('filter-query-input', 'n_submit'),
     State('filter-query-dropdown', 'value'),
     State('filter-query-input', 'value')]
)
def apply_query(n_clicks, n_submit, dropdown_value, input_value):
    if DEBUG:
        print("function: apply_query")
    if n_clicks or n_submit:
        if dropdown_value == 'custom':
            return [input_value]
        else:
            if dropdown_value is None:
                return ['']
            return [dropdown_value]


# Main
if __name__ == '__main__':
    if mathserver:
        app.run_server(debug=DEBUG)
    else:
        app.run_server(debug=DEBUG, port='8052')

