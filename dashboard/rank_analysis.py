# -*- coding: utf-8 -*-

# Import required libraries
import dash
from dash import html, dcc, dash_table
import pandas as pd
import numpy as np
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
from dash.exceptions import PreventUpdate


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

app.title = 'Rank Analysis'

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

# blank figure when no data is present
blankFigure={
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
        rank_index = -1

    if print_rank:
        print(rank_desc)

    # regroup to only Cat I, Cat II, and Adjuncts
    if rank_index > 2:
        rank_index = 5
    elif rank_index > 0:
        rank_index = 2
    else:
        rank_index = 0

    return rank_index



def assignRank(df):
    if DEBUG:
        print("function: assignRank")
    rank_df = pd.read_csv('instructor_ranks.csv')

    df.insert(len(df.columns), 'Rank', 0)
    for row in df.index.to_list():
        name = df.loc[row, 'Instructor']
        term = int(df.loc[row, 'Term'])
        df.loc[row, 'Rank'] = instructor_rank(rank_df, name, term, False)

    return df

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

    _df = _df[_df['Term']>"201640"]

    # create missing columns, if necessary
    if not 'S' in _df.columns:
        _df.insert(len(_df.columns), 'S', 'A')
    if not 'Begin/End' in _df.columns:
        _df.insert(len(_df.columns), 'Begin/End', '01/01-01/01')
    if not 'Max' in _df.columns:
        _df.insert(len(_df.columns), 'Max', 1)
    if not 'Credit' in _df.columns:
        _df.insert(len(_df.columns), 'Credit', 3)

    _df = _df[_df['Credit']>0]
    _df = _df[_df['Enrolled']>0]

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

    _df.insert(len(_df.columns), "SUF", "S")
    for row in _df[_df["Term"].str.endswith("40", na=False)].index.tolist():
        _df.loc[row, "SUF"] = "U"
    for row in _df[_df["Term"].str.endswith("50", na=False)].index.tolist():
        _df.loc[row, "SUF"] = "F"

    _df = assignRank(_df)

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
                    'Enrl', 'Days', 'Time', 'Loc', 'Instructor', 'SUF', 'Rank'
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
                                    '5.5%', '4.5%', '3.5%', '6%', '5.5%', '11%', '3%', '3%'])
                ],
                fixed_rows={'headers': True, 'data': 0},
                page_size=10000,
                virtualization=True,
                data=df.to_dict('records'),
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
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
                html.H3('Rank Analysis'),
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
                    value="CHP per Term",
                    options = [{'label': 'CHP per Term', 'value': 'CHP per Term'},
                               {'label': 'CHP per Term (%)', 'value': 'CHP per Term (%)'},
                               {'label': 'Rank Count per Term', 'value': 'Rank Count per Term'},
                               {'label': 'Rank Count per Term (%)', 'value': 'Rank Count per Term (%)'}],
                    style={'width': '100%', 'display': 'block'},
                    id='fig_select_dropdown',
                ),
            ],
            style={'display': 'flex'},
            id='dropdowns',
        ),
        html.Div([
            dcc.Graph(
                figure = blankFigure,
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
                    [],
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
        Output('datatable-container', 'children'),
    ],
    [
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        State('upload-data-button', 'n_clicks'),
    ]
)
def initial_data_loading(contents, name, n_clicks):
    data_children = create_datatable(pd.DataFrame())


    if contents is not None and n_clicks > 0:
        df = parse_contents(contents, name)
        data_children = create_datatable(df)

    return data_children

@app.callback(
    [
        Output('x_vs_y', 'children'),
    ],
    [
        Input('datatable', 'derived_viewport_data'),
        Input('fig_select_dropdown', 'value'),
    ]
)
def update_graph(data, fig_select):

    df = pd.DataFrame(data)

    df['Rank Desc'] = 'Adjunct'
    for row in df.index.to_list():
        if df.loc[row, 'Rank'] == 5:
            df.loc[row, 'Rank Desc'] = 'Cat I'
        if df.loc[row, 'Rank'] == 2:
            df.loc[row, 'Rank Desc'] = 'Cat II'

    orderedTerms = np.sort(df['Term'].unique())

    if fig_select == 'CHP per Term':
        df = df[['Term', 'Rank Desc', 'CHP']]
        _df = df.groupby(['Term', 'Rank Desc']).agg({'CHP': sum}).reset_index()

        fig = (
            px.bar(
                _df,
                x="Term",
                y="CHP",
                color="Rank Desc",
                title='CHP per Term',
                hover_data={"Rank Desc": False, "Term": False},
                category_orders={"Term": orderedTerms, "Rank Desc": ['Adjunct', 'Cat II', 'Cat I']},
            )
            .update_traces(
                hovertemplate='%{y:d}'
            )
        )

    if fig_select == 'CHP per Term (%)':
        df = df[['Term', 'Rank Desc', 'CHP']]
        _df = df.groupby(['Term', 'Rank Desc']).agg({'CHP': sum}).reset_index()

        _df['Percentage'] = 100*_df['CHP'] / _df.groupby('Term')['CHP'].transform(sum)

        fig = (
            px.bar(
                _df,
                x="Term",
                y="Percentage",
                color="Rank Desc",
                title='CHP per Term (%)',
                hover_data={"Rank Desc": False, "Term": False, "Percentage": True},
                category_orders={"Term": orderedTerms, "Rank Desc": ['Adjunct', 'Cat II', 'Cat I']},
            )
            .update_traces(
                hovertemplate='%{y:.1f}%'
            )
        )

    if fig_select == 'Rank Count per Term':
        df = df[['Term', 'Rank Desc', 'Instructor']].drop_duplicates()
        _df = df.groupby(['Term', 'Rank Desc']).agg({'Instructor': 'count'}).reset_index()

        fig = (
            px.bar(
                _df,
                x="Term",
                y="Instructor",
                color="Rank Desc",
                title='Rank Count per Term',
                hover_data={"Rank Desc": False, "Term": False},
                category_orders={"Term": orderedTerms, "Rank Desc": ['Adjunct', 'Cat II', 'Cat I']},
            )
            .update_traces(
                hovertemplate='%{y:d}'
            )
        )

    if fig_select == 'Rank Count per Term (%)':
        df = df[['Term', 'Rank Desc', 'Instructor']].drop_duplicates()
        _df = df.groupby(['Term', 'Rank Desc']).agg({'Instructor': 'count'}).reset_index()

        _df['Percentage'] = 100*_df['Instructor'] / _df.groupby('Term')['Instructor'].transform(sum)

        fig = (
            px.bar(
                _df,
                x="Term",
                y="Percentage",
                color="Rank Desc",
                title='Rank Count per Term (%)',
                hover_data={"Rank Desc": False, "Term": False},
                category_orders={"Term": orderedTerms, "Rank Desc": ['Adjunct', 'Cat II', 'Cat I']},
            )
            .update_traces(
                hovertemplate='%{y:.1f}%'
            )
        )


    # except KeyError:
        # raise PreventUpdate

    return [dcc.Graph( figure = fig,)]

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
        app.run_server(debug=DEBUG, port='8054')

