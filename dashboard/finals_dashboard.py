# -*- coding: utf-8 -*-

# Import required libraries
import dash
from dash import html, dcc, dash_table
import pandas as pd
import plotly.graph_objects as go
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

pd.set_option('display.max_rows',None)

# Initialize server
app = dash.Dash(
    __name__,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width'}],
    prevent_initial_callbacks=True,
)

server = app.server

app.title = 'Finals Schedule'

app.config.update({
    'suppress_callback_exceptions': True,
})

# specifics for the math.msudenver.edu server
if mathserver:
    app.config.update({
       'url_base_pathname':'/scheduling/',
       'routes_pathname_prefix':'/scheduling/',
       'requests_pathname_prefix':'/scheduling/',
    })

room_capacities = {
    "CN 109": 47,
    "KC 307": 48,
    "KC 313": 48,
    "PL 329": 24,
    "PL M204": 110,
    "PL M206": 46,
    "SI 1007": 25,
    "SI 1008": 44,
    "SI 1010": 40,
    "SI 1011": 42,
    "SI 1015": 36,
    "SI 1058": 40,
    "SI 1068": 16,
    "SI 1113": 54,
    "SSB 213": 24,
}

df_rooms = pd.DataFrame({'Room': room_capacities.keys(), 'Cap': room_capacities.values()})

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
        ['MTH 3130', 'Advd Matrix Mthds Phy Sciences',],
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

    # reset to the start of the IO stream
    # file_contents.seek(0)

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
    # for row in _df[_df['Subj'].str.contains('MTH') & _df['Nmbr'].str.contains('1109') & _df['S'].str.contains('A')].index.tolist():
        # for col in ['Subj', 'Nmbr', 'CRN', 'Sec', 'S', 'Cam', 'T', 'Title', 'Max', 'Enrl', 'WCap', 'WLst', 'Instructor']:
            # _df.loc[row + 1, col] = _df.loc[row, col]
        # _df.loc[row + 1, 'Credit'] = 0

    # correct report to also include missing data for MTH 1108
    # for row in _df[_df['Subj'].str.contains('MTH') & _df['Nmbr'].str.contains('1108') & _df['S'].str.contains('A')].index.tolist():
        # for col in ['Subj', 'Nmbr', 'CRN', 'Sec', 'S', 'Cam', 'T', 'Title', 'Max', 'Enrl', 'WCap', 'WLst', 'Instructor']:
            # _df.loc[row + 1, col] = _df.loc[row, col]
        # _df.loc[row + 1, 'Credit'] = 0
        # row_dict = _df.loc[row].to_dict()
        # row_dict['Instructor'] = ','
        # row_dict['Credit'] = 0
        # # _df = _df.append(row_dict, ignore_index=True)  # DEPRECATED
        # pd.concat((_df, pd.Series(row_dict)), ignore_index=True)

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
    _df.drop(['T', 'Max', 'WCap', 'WList', 'Rcap', 'Full'], axis=1, inplace=True)

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

    _df = _df[['Subject', 'Number', 'CRN', 'Section', 'S', 'Campus', 'Title',
              'Credit', 'Enrolled', 'Days', 'Time', 'Loc', 'Begin/End', 'Instructor']]

    _df.insert(len(_df.columns), 'Class', ' ')
    _df['Class'] = _df['Subject'] + ' ' + _df['Number']
    _df = updateTitles(_df)

    # print(_df)
    # there might be CRNs that are unknown (blank), so fill sequentially starting
    # from 99999 and go down
    i = 1
    for row in _df[_df['CRN'].isna()].index.tolist():
        _df.loc[row, 'CRN'] = str(100000 - i)
        i += 1

    return _df

def parse_enrollment(contents, filename):#, date):
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

def parse_finals(contents):

    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    _file = io.StringIO(decoded.decode('utf-8')).read()
    _file = _file.replace('\r','')

    file_contents = []
    line = ''
    for char in _file:
        if char == '\n':
            file_contents.append(line)
            line = ''
        else:
            line += char

    rows = []
    for line in file_contents:
        line = line.replace('"','')
        fields = line.split(',')


        # only pick up classes for MTH or MTL
        if fields[1][:3] == "MTH" or fields[1][:3] == "MTL":
            CRN = fields[1].split(' ')[1]
            Loc = fields[3]
            try:
                Date = datetime.datetime.strptime(fields[6], '%m/%d/%Y').strftime('%m/%d/%Y')
            except ValueError:
                Date = datetime.datetime.strptime(fields[6], '%x').strftime('%m/%d/%Y')

            # reformat the time to match the SWRCGSR formatting
            start_time = fields[7].replace(':','')[:-2].zfill(4)
            end_time = fields[8].replace(':','')[:-2].zfill(4)
            AMPM = fields[8][-2:]
            Time = start_time + '-' + end_time + AMPM

            # find the day of week and code it to MTWRFSU
            day_str = datetime.datetime.strptime(Date, '%m/%d/%Y').strftime('%A')
            if day_str == "Monday":
                Days = "M"
            elif day_str == "Tuesday":
                Days = "T"
            elif day_str == "Wednesday":
                Days = "W"
            elif day_str == "Thursday":
                Days = "R"
            elif day_str == "Friday":
                Days = "F"
            elif day_str == "Saturday":
                Days = "S"
            else:
                Days = "U"

            rows.append([CRN, Days, Time, Loc, Date])

    df = pd.DataFrame(rows, columns=['CRN', 'Days', 'Time', 'Loc', 'Date'])

    return df

def to_excel(df):
    if DEBUG:
        print("function: to_excel")
    _df = df.copy()

    # only grab needed columns and correct ordering
    cols = ['Subject', 'Number', 'CRN', 'Section', 'Title', 'Instructor',
            'Final_Day', 'Final_Time', 'Final_Loc', 'Final_Date', 'Error',]
    _df = _df[cols]

    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(
        xlsx_io, engine='xlsxwriter', options={'strings_to_numbers': False}
    )
    _df.to_excel(writer, sheet_name='Final Exam Schedule', index=False)

    # Save it
    writer.save()
    xlsx_io.seek(0)
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = base64.b64encode(xlsx_io.read()).decode('utf-8')

    return data

# Create app layout

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Tabs([
                dcc.Tab(
                    label='Combined',
                    value='tab-combined',
                    style={
                        'height': '30px',
                        'padding': '2px',
                    },
                    selected_style = {
                        'borderTop': '2px solid #064779',
                        'height': '30px',
                        'padding': '2px',
                    },
                ),
                dcc.Tab(
                    label='Enrollment Report',
                    value='tab-enrollment',
                    style={
                        'height': '30px',
                        'padding': '2px',
                    },
                    selected_style = {
                        'borderTop': '2px solid #064779',
                        'height': '30px',
                        'padding': '2px',
                    },
                ),
                dcc.Tab(
                    label='Finals Export',
                    value='tab-finals',
                    style={
                        'height': '30px',
                        'padding': '2px',
                    },
                    selected_style = {
                        'borderTop': '2px solid #064779',
                        'height': '30px',
                        'padding': '2px',
                    },
                ),
            ],
                id='table-tabs',
                value='tab-combined',
            ),
        ],
            id='tableTabsContainer',
        ),
        html.Div([
            html.Div([
            ],
                id='datatable-combined-div',
                style = {
                    'background': 'white',
                    'display': 'block',
                    'width': '100%',
                }
            ),
            html.Div([
            ],
                id='datatable-enrollment-div',
                style = {
                    'background': 'white',
                    'display': 'none',
                    'width': '100%',
                }
            ),
            html.Div([
            ],
                id='datatable-finals-div',
                style = {
                    'background': 'white',
                    'display': 'none',
                    'width': '100%',
                }
            ),
        ],
            id='tab-contents',
        ),
    ],
        id='leftContainer',
        style={
            'background': 'white',
            'width': '78%',
            'height': '900px',
            'display': 'inline-block',
            'marginLeft': 'auto',
            'marginRight': 'auto',
            'padding': '5px',
            'vertical-align': 'top',
        },
    ),
    html.Div([
        html.Div([
            dash_table.DataTable(
                id='datatable-rooms',
                columns=[{'name': n, 'id': i} for n,i in zip([
                    'Room', 'Cap'], [ *df_rooms.columns ])],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                },
                style_cell={
                    'font-family': 'sans-serif',
                    'font-size': '1rem',
                    'textAlign': 'left',
                    'whiteSpace': 'normal',
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)",
                    }
                ],
                fixed_rows={'headers': True, 'data': 0},
                data=df_rooms.to_dict('records'),
                editable=True,
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
            ),
            html.Button('Add Row', id='editing-rows-button', n_clicks=0),
        ],
        ),
        html.Div([
            html.Hr(),
            html.Label('Load:'),
            dcc.Upload(
                id='upload-enrollment',
                children= html.Button(
                    'Enrlmnt Report',
                    id='load-enrollmentreport-button',
                    n_clicks=0,
                    style={
                        'padding': '0px',
                        'textAlign': 'center',
                        'width': '95%',
                    },
                    className='button'
                ),
                multiple=False,
                accept='.txt, .csv, .xlsx',
            ),
            dcc.Upload(
                id='upload-finals',
                children= html.Button(
                    'Finals Export',
                    id='load-finalsexport-button',
                    n_clicks=0,
                    style={'padding': '0px', 'textAlign': 'center', 'width': '95%'},
                    className='button'
                ),
                multiple=False,
                accept='.txt, .csv, .xlsx',
            ),
            html.Hr(),
            html.Label('Action:'),
            html.Button(
                'Update',
                id='update-button',
                n_clicks=0,
                disabled=True,
                style={'padding': '0px', 'textAlign': 'center', 'width': '95%'},
                className='button'
            ),
            html.Button(
                'Download',
                id='download-button',
                n_clicks=0,
                disabled=True,
                style={'padding': '0px', 'textAlign': 'center', 'width': '95%'},
                className='button'
            ),
            dcc.Download(id='datatable-download'),
        ],
            id='buttonContainer',
        ),
    ],
        id='rightContainer',
        style={
            'background': 'white',
            'width': '18%',
            'height': '900px',
            'display': 'inline-block',
            'marginLeft': 'auto',
            'marginRight': 'auto',
            'padding': '5px',
            'vertical-align': 'top',
        },
    ),
],
    id='mainContainer',
    style={
        'height': '900px',
        'width': '100%',
    },
    className="container",
)

@app.callback(
    [Output('datatable-combined-div', 'style'),
     Output('datatable-enrollment-div', 'style'),
     Output('datatable-finals-div', 'style'),],
    [Input('table-tabs', 'value')],
)
def update_tab_display(tab):
    if DEBUG:
        print("function: update_tab_display")
    ctx = dash.callback_context
    if 'table-tabs' in ctx.triggered[0]['prop_id']:
        styles = []
        for t in ['tab-combined', 'tab-enrollment', 'tab-finals']:
            if t == tab:
                styles.append({'display': 'block'})
            else:
                styles.append({'display': 'none'})
        return styles[:]


@app.callback(
    Output('datatable-enrollment-div', 'children'),
    [Input('upload-enrollment', 'contents'),
     State('upload-enrollment', 'filename'),
     State('load-enrollmentreport-button', 'n_clicks')]
)
def load_enrollment_data(contents, name, n_clicks):
    if DEBUG:
        print('function: load_enrollment')
    if contents is not None and n_clicks > 0:
        df_enrollment = parse_enrollment(contents, name)
        # print(df_enrollment.columns)
        data_children = [
            dash_table.DataTable(
                id='datatable-enrollment',
                columns=[{'name': n, 'id': i} for n,i in zip([
                    'Subj', 'Nmbr', 'CRN', 'Sec', 'S', 'Cam', 'Title', 'Credit',
                    'Enrl', 'Days', 'Time', 'Loc', 'Begin/End', 'Instructor'
                ],[ *df_enrollment.columns ])],
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
                    for i,w in zip([ *df_enrollment.columns ],
                                   ['5%', '5.5%', '5.5%', '4.5%', '3.5%', '4.5%', '19.5%',
                                    '5.5%', '4.5%', '5.5%', '9%', '7.5%', '9%', '11%'])
                ],
                fixed_rows={'headers': True, 'data': 0},
                page_size=500,
                data=df_enrollment.to_dict('records'),
                editable=True,
                # virtualization=True,
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                # row_selectable='multi',
                # row_deletable=True,
                selected_rows=[],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
            )
        ]

    else:
        data_children = []
    return data_children

@app.callback(
    Output('datatable-finals-div', 'children'),
    [Input('upload-finals', 'contents'),
     State('load-finalsexport-button', 'n_clicks')]
)
def load_finals_data(contents, n_clicks):
    if DEBUG:
        print('function: load_finals')
    if contents is not None and n_clicks > 0:
        df_finals = parse_finals(contents)
        data_children = [
            dash_table.DataTable(
                id='datatable-finals',
                columns=[{'name': n, 'id': i} for n,i in zip([
                    'CRN', 'Day', 'Time', 'Loc', 'Date'
                ],[ *df_finals.columns ])],
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
                    for i,w in zip([ *df_finals.columns ], ['20%',  '20%',  '20%',  '20%',  '20%'])
                ],
                fixed_rows={'headers': True, 'data': 0},
                page_size=500,
                data=df_finals.to_dict('records'),
                editable=True,
                # virtualization=True,
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                # row_selectable='multi',
                # row_deletable=True,
                selected_rows=[],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                page_action='none',
                style_table={'height': '1600px', 'overflowY': 'auto'},
            ),
            html.Button('Add Row', id='addrow-finals-button', n_clicks=0),
        ]

    else:
        data_children = []
    return data_children

@app.callback(
    Output('update-button', 'disabled'),
    [Input('upload-enrollment', 'contents'),
     Input('upload-finals', 'contents')]
)
def enable_update_button(enrollment_contents, finals_contents):
    if DEBUG:
        print('function: enable_update_button')
    if enrollment_contents is not None and finals_contents is not None:
        return False
    return True

@app.callback(
    Output('download-button', 'disabled'),
    Input('update-button', 'n_clicks'),
)
def enable_update_button(n_clicks):
    if DEBUG:
        print('function: enable_disable_button')
    if n_clicks > 0:
        return False
    return True

@app.callback(
    Output('datatable-finals', 'data'),
    Input('addrow-finals-button', 'n_clicks'),
    State('datatable-finals', 'data'),
    State('datatable-finals', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output('datatable-rooms', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('datatable-rooms', 'data'),
    State('datatable-rooms', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output('datatable-download', 'data'),
    [Input('download-button', 'n_clicks'),
     State('datatable-combined', 'data')]
)
def export_all(n_clicks, data):
    if DEBUG:
        print("function: download")
    _df = pd.DataFrame(data)
    if n_clicks > 0:
        return {'base64': True, 'content': to_excel(_df), 'filename': 'Final Exam Schedule.xlsx', }

    # 'DEPT/CID CALL and Title', 'CRN', 'Day', 'Final Exam Time',
    # 'EndTime', 'Final Exam Date', 'Final Exam Rm', 'ContactName'

@app.callback(
    [Output('datatable-combined-div', 'children'),
     Output('table-tabs', 'value')],
    [Input('update-button', 'n_clicks'),
     State('datatable-enrollment', 'data'),
     State('datatable-finals', 'data'),
     State('datatable-rooms', 'data')]
)
def create_combined_table(n_clicks, data_enrollment, data_finals, data_rooms):
    df_enrollment = pd.DataFrame(data_enrollment)
    df_enrollment.rename(
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
    df_finals = pd.DataFrame(data_finals)
    df_rooms = pd.DataFrame(data_rooms)

    room_capacities = {
        df_rooms.loc[row, 'Room']: df_rooms.loc[row, 'Cap'] for row in df_rooms.index.tolist()
    }

    # remove all canceled classes
    df_enrollment.drop(df_enrollment[df_enrollment.S == "C"].index, inplace=True)

    # remove any times that have TBA
    df_enrollment.drop(df_enrollment[df_enrollment.Time == "TBA"].index, inplace=True)

    # remove any classes not on the main campus
    df_enrollment.drop(df_enrollment[df_enrollment.Campus != "M"].index, inplace=True)

    # remove labs
    df_enrollment.drop(df_enrollment[df_enrollment.Number == "1082"].index, inplace=True)
    df_enrollment.drop(df_enrollment[df_enrollment.Number == "1101"].index, inplace=True)
    df_enrollment.drop(df_enrollment[df_enrollment.Number == "1116"].index, inplace=True)
    df_enrollment.drop(df_enrollment[df_enrollment.Number == "1312"].index, inplace=True)

    # change time format from 12HR to 24HR
    # df_enrollment['Time'] = df_enrollment['Time'].apply(lambda x: convertAMPMtime(x))

    # remove extraneous columns
    df_enrollment = df_enrollment.drop(columns=['Begin/End', 'S'])

    # reset the index
    df_enrollment = df_enrollment.reset_index(drop=True)

    # create columns for final information
    df_enrollment['Final_Day'] = ''
    df_enrollment['Final_Time'] = ''
    df_enrollment['Final_Loc'] = ''
    df_enrollment['Final_Time'] = ''
    df_enrollment['Final_Date'] = ''
    df_enrollment['Error'] = [[] for _ in range(len(df_enrollment))]

    # change time format from 12HR to 24HR
    df_finals['Time'] = df_finals['Time'].apply(lambda x: convertAMPMtime(x))

    # if DEBUG:
        # print(df_finals.sort_values(by='CRN'))
        # print(df_enrollment.sort_values(by='CRN'))
    # df_finals.to_csv('finals.csv', index=False)
    # df_enrollment.to_csv('enrollment.csv', index=False)

    # go through each row
    for row in df_enrollment.index.tolist():
        CRN = df_enrollment.loc[row, 'CRN']

        # check if there is a final for this CRN
        if df_finals[df_finals['CRN'] == CRN].shape[0] == 0:
            # ERROR 0: No final for this CRN
            df_enrollment.loc[row, 'Error'].append(0)

        # check for multiple finals for this CRN
        else:
            if df_finals[df_finals['CRN'] == CRN].shape[0] > 1:
                # ERROR 1: Multiple finals for this CRN
                df_enrollment.loc[row, 'Error'].append(1)

            else: # only one final found
                # check if day of final is one of the days of the class
                day = df_finals[df_finals['CRN'] == CRN]['Days'].iloc[0]
                date = df_finals[df_finals['CRN'] == CRN]['Date'].iloc[0]
                time = df_finals[df_finals['CRN'] == CRN]['Time'].iloc[0]
                room = df_finals[df_finals['CRN'] == CRN]['Loc'].iloc[0]
                days = df_enrollment.loc[row, 'Days']
                if days.find(day) < 0:

                    # day of week does not match, is this an Algebra class
                    if df_enrollment.loc[row, 'Number'] in ['1109', '1110', '1111']:
                        if day == "S":
                            df_enrollment.loc[row, 'Final_Day'] = day
                            df_enrollment.loc[row, 'Final_Date'] = date
                            df_enrollment.loc[row, 'Final_Time'] = time
                            df_enrollment.loc[row, 'Final_Loc'] = room
                        else:
                            # ERROR 2: Day of final incorrect
                            df_enrollment.loc[row, 'Error'].append(2)

                    else:
                        # ERROR 2: Day of final incorrect
                        df_enrollment.loc[row, 'Error'].append(2)

                else:
                    df_enrollment.loc[row, 'Final_Day'] = day
                    df_enrollment.loc[row, 'Final_Date'] = date
                    df_enrollment.loc[row, 'Final_Time'] = time
                    df_enrollment.loc[row, 'Final_Loc'] = room

    # check for instructor overlap
    instructors = df_enrollment['Instructor'].unique()
    for instructor in instructors:
        days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
        for day in days:
            # filter by location and day
            df = df_enrollment[(df_enrollment['Instructor'] == instructor) & (df_enrollment['Final_Day'] == day)]

            # check for instructor overlap of same time blocks (this does not calculate all overlaps)
            if df.shape[0] > 1 and (df['Time'].nunique() != df['Final_Time'].nunique()):
                for row in df.index.tolist():
                    # ERROR 3: Overlap of time block
                    df_enrollment.loc[row, 'Error'].append(3)

            # check nonconformal overlaps; this uses SUMPRODUCT
            times = df['Final_Time'].unique().tolist()
            n = len(times)
            if n > 1:
                start_times = [datetime.datetime.strptime(time[:5], "%H:%M") for time in times]
                end_times = [datetime.datetime.strptime(time[-5:], "%H:%M") for time in times]
                for k in range(n):
                    s = ([x > start_times[k] for x in end_times])
                    e = ([x < end_times[k] for x in start_times])
                    if sum([x*y for x,y in zip(s,e)]) > 1:
                        for row in df.index.tolist():
                            if df.loc[row, 'Final_Time'] == times[k]:
                                # ERROR 4: Overlap between time blocks
                                df_enrollment.loc[row, 'Error'].append(4)

                # check for instructor back-to-back (different rooms) within 5 minutes
                end_times = [datetime.datetime.strptime(time[-5:], "%H:%M")+datetime.timedelta(minutes=5) for time in times]
                for k in range(n):
                    s = ([x > start_times[k] for x in end_times])
                    e = ([x < end_times[k] for x in start_times])
                    if sum([x*y for x,y in zip(s,e)]) > 1:
                        for row in df.index.tolist():
                            if df.loc[row, 'Final_Time'] == times[k]:
                                # ERROR 5: Instructor back-to-back within 5 minutes
                                df_enrollment.loc[row, 'Error'].append(5)



    # check for room overlap
    rooms = df_enrollment['Final_Loc'].unique()
    for room in rooms:
        days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
        for day in days:
            # filter by location and day
            df = df_enrollment[(df_enrollment['Final_Loc'] == room) & (df_enrollment['Final_Day'] == day)]

            # check for room overlap of same time blocks (this does not calculate all overlaps)
            if df.shape[0] > 1 and (df['Time'].nunique() != df['Final_Time'].nunique()):
                for row in df.index.tolist():
                    # ERROR 6: Overlap of time block
                    df_enrollment.loc[row, 'Error'].append(6)

            # check nonconformal overlaps; this uses SUMPRODUCT
            times = df['Final_Time'].unique().tolist()
            n = len(times)
            if n > 1:
                start_times = [datetime.datetime.strptime(time[:5], "%H:%M") for time in times]
                end_times = [datetime.datetime.strptime(time[-5:], "%H:%M") for time in times]
                for k in range(n):
                    s = ([x > start_times[k] for x in end_times])
                    e = ([x < end_times[k] for x in start_times])
                    if sum([x*y for x,y in zip(s,e)]) > 1:
                        for row in df.index.tolist():
                            if df.loc[row, 'Final_Time'] == times[k]:
                                # ERROR 7: Overlap between time blocks
                                df_enrollment.loc[row, 'Error'].append(7)
                # check for back-to-back in same room
                for k in range(n):
                    s = ([x == start_times[k] for x in end_times[:-1]])
                    e = ([x == end_times[k] for x in start_times[1:]])
                    if sum(s+e) > 0:
                        for row in df.index.tolist():
                            if df.loc[row, 'Final_Time'] == times[k]:
                                # ERROR 8: Back-to-back in same room
                                df_enrollment.loc[row, 'Error'].append(8)

    # check that start time is within one hour of regular class start time
    for row in df_enrollment.index.tolist():
        class_start = datetime.datetime.strptime(df_enrollment.loc[row, 'Time'][:5], "%H:%M")
        plusone = class_start + datetime.timedelta(hours=1)
        minusone = class_start + datetime.timedelta(hours=-1)
        try:
            final_start = datetime.datetime.strptime(df_enrollment.loc[row, 'Final_Time'][:5], "%H:%M")
            final_day = df_enrollment.loc[row, 'Final_Day']
            if (final_start < minusone or final_start > plusone) and (final_day != "S"):
                # ERROR 9: Final start time not within one hour of regular start time
                df_enrollment.loc[row, 'Error'].append(9)

        except: # no final time provided
            pass

    # check enrollment by instructor, if room large enough, remove error
    rows = []
    for row in df_enrollment.index.tolist():
        # same room, different instructor
        if 3 in df_enrollment.loc[row, 'Error']:
            rows.append(row)
    # now add up all the enrollments and compare against room capacity
    df = df_enrollment[df_enrollment.index.isin(rows)]
    for row in rows:
        enrl = df[(df['Instructor'] == df.loc[row, 'Instructor']) & (df['Final_Time'] == df.loc[row, 'Final_Time'])]['Enrolled'].sum()
        if enrl < int(room_capacities[df.loc[row, 'Final_Loc']]):
            try: # only can be done if the room exists in the room_capacity dictionary
                df_enrollment.loc[row, 'Error'].remove(3)
            except:
                pass

    # check enrollment by room, if room large enough, remove error
    rows = []
    for row in df_enrollment.index.tolist():
        # same room, different CRN
        if 6 in df_enrollment.loc[row, 'Error']:
            rows.append(row)
    # now add up all the enrollments and compare against room capacity
    df = df_enrollment[df_enrollment.index.isin(rows)]
    for row in rows:
        enrl = df[(df['Final_Loc'] == df.loc[row, 'Final_Loc']) & (df['Final_Time'] == df.loc[row, 'Final_Time'])]['Enrolled'].sum()
        if enrl < int(room_capacities[df.loc[row, 'Final_Loc']]):
            try: # only can be done if the room exists in the room_capacity dictionary
                df_enrollment.loc[row, 'Error'].remove(6)
            except:
                pass


    df = df_enrollment[['Subject', 'Number', 'CRN', 'Section', 'Title', 'Instructor',
                       'Final_Day', 'Final_Time', 'Final_Loc', 'Final_Date', 'Error']]

    data_children = [
        dash_table.DataTable(
            id='datatable-combined',
            columns=[{'name': n, 'id': i} for n,i in zip([
                'Subj', 'Nmbr', 'CRN', 'Sec', 'Title', 'Instructor',
                'Day', 'Time', 'Loc', 'Date', 'Error'
            ],[*df.columns])],
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
                               ['5%', '5.5%', '5.5%', '4.5%', '13.5%', '4.5%', '4.5%',
                                '7.5%', '7.0%', '5.5%', '9%', '7.5%', '9%', '11%'])
            ],
            fixed_rows={'headers': True, 'data': 0},
            page_size=500,
            data=df.to_dict('records'),
            editable=True,
            # virtualization=True,
            filter_action='native',
            sort_action='native',
            sort_mode='multi',
            # row_selectable='multi',
            # row_deletable=True,
            selected_rows=[],
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
        ),
        html.Hr(),
        html.P(),
        html.Label('The error codes are'),
        html.Ul([
            html.Li('0: No final for this CRN'),
            html.Li('1: Multiple finals for this CRN'),
            html.Li('2: Day of final incorrect'),
            html.Li('3: Overlap of time block for instructor'),
            html.Li('4: Overlap between time blocks for instructor'),
            html.Li('5: Instructor back-to-back within 5 minutes'),
            html.Li('6: Overlap of time block in same room'),
            html.Li('7: Overlap between time blocks in same room'),
            html.Li('8: Back-to-back in same room'),
            html.Li('9: Final start time not within one hour of regular start time'),
        ],
            style={'list-style-type': 'none'},
        ),
    ]
    return data_children, 'tab-combined'

# Main
if __name__ == '__main__':
    if mathserver:
        app.run_server(debug=DEBUG)
    else:
        app.run_server(debug=True, host='10.0.2.15', port='8053')