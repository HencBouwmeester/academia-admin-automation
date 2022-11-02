# -*- coding: utf-8 -*-

# Import required libraries
import dash
from dash import html, dcc, dash_table
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
# import numpy as np
import base64
import io
from dash.dependencies import Input, Output, State, ClientsideFunction
import plotly.graph_objects as go
import datetime
import dash_daq as daq

DEBUG = False
mathserver = False

# Include pretty graph formatting
pio.templates.default = 'plotly_white'

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

def updateTitles(df):
    if DEBUG:
        print("function: updateTitles")
    course_titles = [
        ['MTH 1051', 'Principles of Math in Chem Lab',],
        ['MTH 1080', 'Mathematics for Liberal Arts',],
        ['MTH 1081', 'Math. for Lib. Arts with Lab',],
        ['MTH 1082', 'Math. for Liberal Arts Lab',],
        ['MTH 1101', 'College Algebra for Calc Lab',],
        ['MTH 1108', 'College Algebra Stretch Part I',],
        ['MTH 1109', 'College Alg. Stretch Part II',],
        ['MTH 1110', 'College Algebra for Calculus',],
        ['MTH 1111', 'College Alg. for Calc with Lab',],
        ['MTH 1112', 'College Algebra thru Modeling',],
        ['MTH 1115', 'College Alg thru Mdlng w Lab',],
        ['MTH 1116', 'College Alg thru Mdlng Lab',],
        ['MTH 1120', 'College Trigonometry',],
        ['MTH 1210', 'Introduction to Statistics',],
        ['MTH 1310', 'Finite Math - Mgmt & Soc Scncs',],
        ['MTH 1311', 'Finite Math-Mgmt -with Lab',],
        ['MTH 1312', 'Finite Mathematics Lab',],
        ['MTH 1320', 'Calculus - Mgmt & Soc Sciences',],
        ['MTH 1400', 'Precalculus Mathematics',],
        ['MTH 1410', 'Calculus I',],
        ['MTH 1610', 'Integrated Mathematics I',],
        ['MTH 2140', 'Computational Matrix Algebra',],
        ['MTH 2410', 'Calculus II',],
        ['MTH 2420', 'Calculus III',],
        ['MTH 2520', 'R Programming',],
        ['MTH 2540', 'Scientific Computing',],
        ['MTH 2620', 'Integrated Mathematics II',],
        ['MTH 3100', 'Intro to Mathematical Proofs',],
        ['MTH 3110', 'Abstract Algebra I',],
        ['MTH 3130', 'Applied Methods in Linear Algebra',],
        ['MTH 3140', 'Linear Algebra',],
        ['MTH 3170', 'Discrete Math for Comp Science',],
        ['MTH 3210', 'Probability and Statistics',],
        ['MTH 3220', 'Statistical Methods',],
        ['MTH 3240', 'Environmental Statistics',],
        ['MTH 3270', 'Data Science',],
        ['MTH 3400', 'Chaos & Nonlinear Dynamics',],
        ['MTH 3420', 'Differential Equations',],
        ['MTH 3430', 'Mathematical Modeling',],
        ['MTH 3440', 'Partial Differential Equations',],
        ['MTH 3470', 'Intro Discrete Math & Modeling',],
        ['MTH 3510', 'SAS Programming',],
        ['MTH 3650', 'Foundations of Geometry',],
        ['MTH 4110', 'Abstract Algebra II',],
        ['MTH 4150', 'Elementary Number Theory',],
        ['MTH 4210', 'Probability Theory',],
        ['MTH 4230', 'Regression/Computational Stats',],
        ['MTH 4250', 'Statistical Theory',],
        ['MTH 4290', 'Senior Statistics Project',],
        ['MTH 4410', 'Real Analysis I',],
        ['MTH 4420', 'Real Analysis II',],
        ['MTH 4450', 'Complex Variables',],
        ['MTH 4480', 'Numerical Analysis I',],
        ['MTH 4490', 'Numerical Analysis II',],
        ['MTH 4640', 'History of Mathematics',],
        ['MTH 4660', 'Introduction to Topology',],
        ['MTL 3600', 'Mathematics of Elementary Curriculum',],
        ['MTL 3620', 'Mathematics of Secondary Curriculum',],
        ['MTL 3630', 'Teaching Secondary Mathematics',],
        ['MTL 3638', 'Secondry Mathematics Field Experience',],
        ['MTL 3750', 'Number & Alg in the K-8 Curriculum',],
        ['MTL 3760', 'Geom & Stats in the K-8 Curriculum',],
        ['MTL 3850', 'STEM Teaching and Learning',],
        ['MTL 3858', 'STEM Practicum',],
        ['MTL 4630', 'Teaching Secondary Mathematics',],
        ['MTL 4690', 'Student Teaching & Seminar: Secondary 7-12',],
        ['MTLM 5020', 'Integrated Mathematics II',],
        ['MTLM 5600', 'Mathematics of the Elementary Curriculum',],
    ]

    df_titles = pd.DataFrame(course_titles, columns=['Class', 'Title'])

    cols = df.columns
    df = df.set_index('Class')
    df.update(df_titles.set_index('Class'))
    df.reset_index(inplace=True)
    df = df[cols]


    return df

def convertAMPMtime(timeslot):
    if DEBUG:
        print("function: convertAMPMtime")
    """Convert time format from 12hr to 24hr and account for TBA times.

    Args:
        timeslot: dataframe cell contents.

    Returns:
        reformmated dataframe cell contents."""

    try:
        starthour = int(timeslot[0:2])
        endhour = int(timeslot[5:7])
        if timeslot[-2:] == 'PM':
            endhour = endhour + 12 if endhour < 12 else endhour
            starthour = starthour + 12 if starthour + 12 <= endhour else starthour
        timeslot = '{:s}:{:s}-{:s}:{:s}'.format(
            str(starthour).zfill(2), timeslot[2:4], str(endhour).zfill(2), timeslot[7:9]
        )
    except ValueError:  # catch the TBA times
        pass

    return timeslot

def tidy_txt(file_contents):
    if DEBUG:
        print("function: tidy_txt")
    """Take in SWRCGSR output and format into pandas-compatible format.

    Args:
        file_contents:
            input decoded filestream of SWRCGSR output from an uploaded textfile.

    Returns:
        Dataframe.
    """

    _LINE_PATTERN = [
        (0, 5),
        (5, 10),
        (10, 16),
        (16, 20),
        (20, 22),
        (22, 26),
        (26, 28),
        (28, 44),
        (44, 51),
        (51, 56),
        (56, 61),
        (61, 66),
        (66, 71),
        (71, 79),
        (79, 91),
        (91, 99),
        (99, 104),
        (104, 109),
        (109, 121),
        (121, 140),
    ]

    # move cursor to first nonempty line
    for i in range(5):
        line = file_contents.readline()

    # read into a dataframe based on specified column spacing
    _df = pd.read_fwf(file_contents, colspecs=_LINE_PATTERN)

    # read the report Term and Year from file
    term_code = str(_df.iloc[0][1])[3:] + str(_df.iloc[0][2])[:-2]

    # rename the columns
    # make allowances for newer version of pandas
    if pd.__version__ == '1.4.1':
        k = 1
    else:
        k = 2
    _df.columns = _df.iloc[k]


    # manual filtering of erroneous data which preserves data for MTH 1108/1109
    _df = _df.dropna(how='all')
    _df = _df[~_df['Subj'].str.contains('Subj', na=False)]
    _df = _df[~_df['Subj'].str.contains('---', na=False)]
    _df = _df[~_df['Subj'].str.contains('SWRC', na=False)]
    _df = _df[~_df['Subj'].str.contains('Ter', na=False)]
    _df = _df[~_df['Instructor'].str.contains('Page', na=False)]
    _df = _df.drop(_df.index[_df['Loc'].str.startswith('BA', na=False)].tolist())
    _df = _df[_df['Begin/End'].notna()]

    # reset index and remove old index column
    _df = _df.reset_index()
    _df = _df.drop([_df.columns[0]], axis=1)

    # correct report to also include missing data for MTH 1109
    for row in _df[_df['Subj'].str.contains('MTH') & _df['Nmbr'].str.contains('1109') & _df['S'].str.contains('A')].index.tolist():
        for col in ['Subj', 'Nmbr', 'CRN', 'Sec', 'S', 'Cam', 'T', 'Title', 'Max', 'Enrl', 'WCap', 'WLst', 'Instructor']:
            _df.loc[row + 1, col] = _df.loc[row, col]
        _df.loc[row + 1, 'Credit'] = 0

    # correct report to also include missing data for MTH 1108
    for row in _df[_df['Subj'].str.contains('MTH') & _df['Nmbr'].str.contains('1108') & _df['S'].str.contains('A')].index.tolist():
        for col in ['Subj', 'Nmbr', 'CRN', 'Sec', 'S', 'Cam', 'T', 'Title', 'Max', 'Enrl', 'WCap', 'WLst', 'Instructor']:
            _df.loc[row + 1, col] = _df.loc[row, col]
        _df.loc[row + 1, 'Credit'] = 0
        row_dict = _df.loc[row].to_dict()
        row_dict['Instructor'] = ','
        row_dict['Credit'] = 0
        _df = _df.append(row_dict, ignore_index=True)

    # update all titles to show full name
    _df.insert(len(_df.columns), 'Class', ' ')
    _df['Class'] = _df['Subj'] + ' ' + _df['Nmbr']
    _df = updateTitles(_df)

    # remove all rows with irrelevant data
    _df = _df[_df['CRN'].notna()]
    _df = _df[_df.CRN.apply(lambda x: x.isnumeric())]
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
    _df[['Credit', 'Max', 'Enrolled', 'WCap', 'WList']] = _df[
        ['Credit', 'Max', 'Enrolled', 'WCap', 'WList']
    ].apply(pd.to_numeric, errors='coerce')

    _df = _df.sort_values(by=['Subject', 'Number', 'Section'])
    _df.drop(['T', 'Enrolled', 'WCap', 'WList', 'Rcap', 'Full'], axis=1, inplace=True)

    return _df

def tidy_csv(file_contents):
    if DEBUG:
        print("function: tidy_csv")
    """ Converts the CSV format to the TXT format from Banner

    Args:
        file_contents:
            input decoded filestream of SWRCGSR output from an uploaded textfile.

    Returns:
        Dataframe.
    """

    _file = file_contents.read()
    _file = _file.replace('\r','')

    _list = []
    line = ''
    for char in _file:
        if char == '\n':
            line = line.replace('"','')
            _list.append(line[:-1])
            line = ''
        else:
            line += char

    # delete information in first line to match txt file type
    _list = _list[1:]
    _list.insert(0, '')

    return tidy_txt(io.StringIO('\n'.join(_list)))

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

def parse_contents(contents, filename):#, date):
    if DEBUG:
        print("function: parse_contents")
    """Assess filetype of uploaded file and pass to appropriate processing functions,
    then return html of enrollment statistics.

    Args:
        contents: the encoded file contents
        filename: the filename
        date: the timestamp

    Returns:
        html Div element containing statistics and dash graphs
        class EnrollmentData containing data and attributes
    """

    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'txt' in filename:
            # Assume that the user uploaded a banner fixed width file with .txt extension
            df = tidy_txt(io.StringIO(decoded.decode('utf-8')))
            df['Time'] = df['Time'].apply(lambda x: convertAMPMtime(x))
        elif 'csv' in filename:
            # Assume the user uploaded a banner Shift-F1 export quasi-csv file with .csv extension
            df = tidy_csv(io.StringIO(decoded.decode('utf-8')))
            df['Time'] = df['Time'].apply(lambda x: convertAMPMtime(x))
        elif 'xlsx' in filename:
            df = tidy_xlsx(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])

    return df

def create_datatable(df):
        return [
            dash_table.DataTable(
                id='datatable',
                columns=[{'name': n, 'id': i} for n,i in zip([
                    'Term', 'Subj', 'Nmbr', 'CRN', 'Sec', 'S', 'Cam', 'Title', 'Credit',
                    'Enrl', 'Days', 'Time', 'Loc', 'Instructor'
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
                                    '5.5%', '4.5%', '5.5%', '9%', '7.5%', '11%'])
                ],
                fixed_rows={'headers': True, 'data': 0},
                page_size=5000,
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

def to_excel(df):
    if DEBUG:
        print("function: to_excel")
    _df = df.copy()

    # only grab needed columns and correct ordering
    cols = ['Subject', 'Number', 'CRN', 'Section', 'S', 'Campus', 'Title',
            'Credit', 'Max', 'Days', 'Time', 'Loc', 'Begin/End', 'Instructor']
    _df = _df[cols]

    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(
        xlsx_io, engine='xlsxwriter', options={'strings_to_numbers': False}
    )
    _df.to_excel(writer, sheet_name='Schedule', index=False)

    # Save it
    writer.save()
    xlsx_io.seek(0)
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = base64.b64encode(xlsx_io.read()).decode('utf-8')

    return data

# Create app layout
app.layout = html.Div(
    [
        html.Div([
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
                       accept='.txt, .csv, .xlsx'),
        ],
            id='header',
            style={'display': 'flex',
                   'justifyContent': 'space-between',
                   'alignItems': 'center'},
        ),
        html.Div([
            html.Div(
                [
                ],
                id='column-select',
                style={'width': '25rem'},
            ),
            dcc.Loading(id='loading-icon-upload',
                        children=[
                            html.Div([],
                                     style={
                                         'width': '100%',
                                         'display': 'block',
                                         'marginLeft': 'auto',
                                         'marginRight': 'auto'},
                                     id="enrl_v_column"
                            ),
                            html.Div([],
                                     style={
                                         'width': '100%',
                                         'display': 'block',
                                         'marginLeft': 'auto',
                                         'marginRight': 'auto'},
                                     id='datatable-interactivity-container',
                                    )
                        ],
                        type='circle',
                        fullscreen=True,
                        color='#064779'),
        ]),
    ],
    id='mainContainer',
    style={'display': 'flex', 'flexDirection': 'column'},
)

@app.callback(
    Output('output-data-upload', 'style'),
    Input('upload-data', 'contents')
)
def show_contents(contents):
    if DEBUG:
        print("function: show_contents")
    if contents is not None:
        return {'display': 'block'}

@app.callback(
    [Output('loading-icon-upload', 'children'),
     Output('column-select', 'children'),
     Output('upload-data-button', 'n_clicks'),
     Output('loading-icon-upload', 'fullscreen')],
    [Input('upload-data', 'contents'),
     State('upload-data', 'filename'),
     State('upload-data-button', 'n_clicks'),
     State('loading-icon-upload', 'fullscreen')],
)
def initial_data_loading(contents, name, n_clicks, fullscreen):
    if DEBUG:
        print("function: initial_data_loading")
    if contents is not None and n_clicks > 0:
        df = parse_contents(contents, name)
        data_children = create_datatable(df)
        print([{'label': c, 'value': c} for c in df.columns.sort_values() if c not in ['Enrolled']])
        dropdown_children = [
            html.Div([
            dcc.Dropdown(
                options = [
                    {'label': c, 'value': c} for c in df.columns.sort_values() if c not in ['Enrolled']
                ],
                value='Time',
                style={'width': '100%', 'display': 'block'},
                id='column_select_dropdown'),
            dcc.Dropdown(
                options = [{'label': 'Bar', 'value': 'bar'}, {'label': 'Line', 'value': 'line'}],
                value='bar',
                style={'width': '100%', 'display': 'block'},
                id='figure_select_dropdown'),
            ],
                style={'display': 'flex'},
            ),
        ]
        _df = df.groupby("Time").agg({"Enrolled": "sum"})
        fig = (
            px.bar(
                _df,
                y=["Enrolled"],
                title="Enrollment per {:s}".format("Time"),
            )
            .update_xaxes(showticklabels=True)
            .update_layout(
                showlegend=False,
                xaxis_type="category",
                yaxis_title="Enrolled",
                barmode="overlay",
            )
        )

        n_clicks = 0
        fullscreen = False
    else:
        data_children = []
        dropdown_children = []
        fig = {
            'data': [],
            'layout': go.Layout(
                xaxis={
                    'showticklabels': False,
                    'ticks': '',
                    'showgrid': False,
                    'zeroline': False
                },
                yaxis={
                    'showticklabels': False,
                    'ticks': '',
                    'showgrid': False,
                    'zeroline': False
                }
            )
        }

    loading_children = [
        html.Div([
            dcc.Graph(
                figure = fig,
            )],
                id="enrl_v_column"
        ),
        html.Div([
html.Div([
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='filter-query-dropdown',
                    options=[
                        {'label': 'Only Math Classes', 'value': '{Subject} contains M'},
                        # {'label': 'Active Classes', 'value': '{S} contains A'},
                        # {'label': 'Active Math Classes', 'value': '{Subject} contains M && {S} contains A'},
                        {'label': 'Active MTL Classes', 'value': '({Subject} contains MTL || {Number} contains 1610 || {Number} contains 2620) && {S} contains A'},
                        # {'label': 'Active Math without MTL', 'value': '{Subject} > M && {Subject} < MTL && ({Number} <1610 || {Number} >1610) && ({Number} <2620 || {Number} >2620) && {S} contains A'},
                        {'label': 'Math w/o Labs', 'value': '{Subject} contains M && {S} contains A && ({Number} < 1081 || {Number} > 1082) && ({Number} < 1101 || {Number} > 1101) && ({Number} < 1111 || {Number} > 1111) && ({Number} < 1115 || {Number} > 1115) && ({Number} < 1116 || {Number} > 1116) && ({Number} < 1311 || {Number} > 1312)'},
                        {'label': 'Math Labs', 'value': '{Subject} contains M && {S} contains A && ({Number} = 1082 || {Number} = 1101 || {Number} = 1116 || {Number} = 1312)'},
                        {'label': 'Math Labs with Parents', 'value': '{Subject} contains M && {S} contains A && ({Number} = 1081 || {Number} = 1111 || {Number} = 1115 || {Number} = 1311 || {Number} = 1082 || {Number} = 1101 || {Number} = 1116 || {Number} = 1312)'},
                        # {'label': 'Active Unassigned Math w/o Labs', 'value': '{Subject} contains M && {S} contains A && ({Number} < 1082 || {Number} > 1082) && ({Number} < 1101 || {Number} > 1101) && ({Number} < 1116 || {Number} > 1116) && ({Number} < 1312 || {Number} > 1312) && {Instructor} Is Blank'},
                        # {'label': 'Active Unassigned Math Labs', 'value': '{Subject} contains M && {S} contains A && ({Number} = 1082 || {Number} = 1101 || {Number} = 1116 || {Number} = 1312) && {Instructor} Is Blank'},
                        {'label': 'Math Lower Division', 'value': '{Subject} contains M && {Number} < 3000 && {S} contains A'},
                        {'label': 'Math Upper Division', 'value': '{Subject} contains M && {Number} >= 3000 && {S} contains A'},
                        {'label': 'Applied Group', 'value': '{Subject} contains M && {S} contains A && ({Number} = 3130 || {Number} = 3400 || {Number} = 3420 || {Number} = 3430 || {Number} = 3440 || {Number} = 4480 || {Number} = 4490)'},
                        {'label': 'Statistics Group', 'value': '{Subject} contains M && {S} contains A && ({Number} = 3210 || {Number} = 3220 || {Number} = 3230 || {Number} = 3240 || {Number} = 3270 || {Number} = 3510 || {Number} = 4210 || {Number} = 4230 || {Number} = 4250 || {Number} = 4290)'},
                        {'label': 'Theoretical Group', 'value': '{Subject} contains M && {S} contains A && ({Number} = 3100 || {Number} = 3110 || {Number} = 3170 || {Number} = 3140 || {Number} = 3470 || {Number} = 4110 || {Number} = 4150 || {Number} = 4410 || {Number} = 4420 || {Number} = 4450)'},
                        # {'label': 'Active Math Lower Division (except MTL)', 'value': '{Subject} > M && {Subject} < MTL && ({Number} <1610 || {Number} >1610) && ({Number} <2620 || {Number} >2620) && {Number} <3000 && {S} contains A'},
                        # {'label': 'Active Math Upper Division (except MTL)', 'value': '({Subject} > M && {Subject} < MTL) && {Number} >=3000 && {S} contains A'},
                        # {'label': 'Active Asynchronous', 'value': '{Loc} contains O && {S} contains A'},
                        # {'label': 'Active Face-To-Face', 'value': '{Campus} contains M && {S} contains A'},
                        # {'label': 'Active Synchronous', 'value': '{Loc} contains SY && {S} contains A'},
                        # {'label': 'Active Math Asynchronous', 'value': '{Subject} contains M && {Loc} contains O && {S} contains A'},
                        # {'label': 'Active Math Face-To-Face', 'value': '{Subject} contains M && {Campus} contains M && {S} contains A'},
                        # {'label': 'Active Math Synchronous', 'value': '{Subject} contains M && {Loc} contains SY && {S} contains A'},
                        {'label': 'Canceled CRNs', 'value': '{S} contains C'},
                        {'label': 'Custom...', 'value': 'custom'},
                    ],
                    placeholder='Select a query',
                    value=''),
            ],
                style={'display': 'inline-block', 'width':'100%'}
            ),
            html.Div([
                html.Button('Apply Query', id='apply_query_button', className='button')
            ],
                style={'display': 'inline-block'}
            ),
            html.Label('All rooms:',
                           style={'display': 'none'},
                           id='all-rooms-label'),
            daq.BooleanSwitch(id='toggle-rooms',
                              on=True,
                              disabled=False,
                              color='#e6e6e6',
                              style={'display': 'none'}),
            ],
            style={'marginTop': '7px', 'marginLeft': '5px', 'display': 'flex',
                   'justifyContent': 'space-between'}
            ),
            html.Div([
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
                    style={'marginTop': '15px', 'marginLeft': '5px', 'display': 'flex',
                           'justifyContent': 'space-between'}
                )
            ]),
])
            ]),

        html.Div(
            data_children,
                 style={
                     'width': '100%',
                     'display': 'block',
                     'marginLeft': 'auto',
                     'marginRight': 'auto',
                 },
                 id='datatable-container',
                )]

    return loading_children, dropdown_children, n_clicks, fullscreen

@app.callback(
    [Output('filter-query-input-container', 'style'),
     Output('filter-query-output', 'style'),
     Output('filter-query-output', 'children')],
    [Input('filter-query-dropdown', 'value'),
     Input('datatable', 'filter_query')],
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
     State('filter-query-dropdown', 'value'),
     State('filter-query-input', 'value')]
)
def apply_query(n_clicks, dropdown_value, input_value):
    if DEBUG:
        print("function: apply_query")
    if n_clicks > 0:
        if dropdown_value == 'custom':
            return [input_value]
        else:
            if dropdown_value is None:
                return ['']
            return [dropdown_value]


@app.callback(
    Output('enrl_v_column', 'children'),
    Input('datatable', 'derived_viewport_data'),
    Input('column_select_dropdown', 'value'),
    Input('figure_select_dropdown', 'value')
)
def update_fig(data, column_option, figure_option):
    if column_option == "Term":
        _df = pd.DataFrame(data).groupby(column_option).agg({"Enrolled": "sum"})
        str_title = "Enrollment per {:s}".format(column_option)
    else:
        _df = pd.DataFrame(data).groupby(column_option).agg({"Enrolled": "mean"})
        str_title="Average Enrollment per {:s}".format(column_option)

    if figure_option == 'line':
        fig = (
            px.line(
                _df,
                y=["Enrolled"],
                title=str_title,
            )
            .update_xaxes(showticklabels=True)
            .update_yaxes(rangemode="tozero")
            .update_layout(
                showlegend=False,
                xaxis_type="category",
                yaxis_title="Enrolled",
                barmode="overlay",
            )
        )
    else:
        fig = (
            px.bar(
                _df,
                y=["Enrolled"],
                title=str_title,
            )
            .update_xaxes(showticklabels=True)
            .update_layout(
                showlegend=False,
                xaxis_type="category",
                yaxis_title="Enrolled",
                barmode="overlay",
            )
        )
    return [dcc.Graph(figure = fig)]

# Main
if __name__ == '__main__':
    if mathserver:
        app.run_server(debug=True)
    else:
        # app.run_server(debug=False, host='10.0.2.15', port='8052')
        app.run_server(debug=False, port='8052')

