# -*- coding: utf-8 -*-

from utilities import *

# Import required libraries
import dash
from dash import html, dcc, dash_table
import plotly.graph_objects as go
import plotly.io as pio
import base64
from dash.dependencies import Input, Output, State, ClientsideFunction
import datetime
import dash_daq as daq

DEBUG = False
mathserver = False

if DEBUG:
    print('Dash Version: {:s}'.format(dash.__version__))

# Include pretty graph formatting
pio.templates.default = 'plotly_white'

# Initialize server
app = dash.Dash(
    __name__,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width'}],
    prevent_initial_callbacks=True,
)

server = app.server

app.title = 'Scheduling'

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

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


def generate_weekday_tab(day):
    if DEBUG:
        print("generate_weekday_tab")
    tab_style = {
        'height': '30px',
        'padding': '2px',
    }
    selected_tab_style = {
        'borderTop': '2px solid #064779',
        'height': '30px',
        'padding': '2px',
    }

    return dcc.Tab(label=day,
                   value='tab-'+day.lower()[:3],
                   style=tab_style,
                   selected_style=selected_tab_style,
                  )


def parse_contents(contents, filename):#, date):
    if DEBUG:
        print("function: parse_contents")

    _, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    df = pd.DataFrame()
    if 'txt' in filename:
        # Assume that the user uploaded a banner fixed width file with .txt extension
        df, _, _ = tidy_txt(io.StringIO(decoded.decode('utf-8')))
    # elif 'csv' in filename:
        # Assume the user uploaded a banner Shift-F1 export quasi-csv file with .csv extension
        # df = tidy_csv(io.StringIO(decoded.decode('utf-8')))
    elif 'xlsx' in filename:
        df, _, _ = tidy_xlsx(io.BytesIO(decoded))

    df = df[['Subject', 'Number', 'CRN', 'Section', 'S', 'Campus', 'Title', 'Credit', 'Max', 'Enrolled', 'Days', 'Time', 'Loc', 'Begin/End', 'Instructor', 'Class']].copy()
    df.loc[:,'Time'] = df['Time'].apply(lambda x: convertAMPMtime(x))
    return df

    # except Exception as e:
    #     return html.Div(['There was an error processing this file.'])


def create_datatable(df, filter_query):
    if filter_query is None:
        filter_query = ''

    return [
        dash_table.DataTable(
            id='datatable-interactivity',
            data=df.to_dict('records'),
            columns = [
                {'name': 'Subject', 'id': 'Subject'},
                {'name': 'Number', 'id': 'Number'},
                {'name': 'CRN', 'id': 'CRN'},
                {'name': 'Section', 'id': 'Section'},
                {'name': 'S', 'id': 'S'},
                {'name': 'Campus', 'id': 'Campus'},
                {'name': 'Title', 'id': 'Title'},
                {'name': 'Credit', 'id': 'Credit'},
                {'name': 'Max', 'id': 'Max'},
                {'name': 'Enrl', 'id': 'Enrolled'},
                {'name': 'Days', 'id': 'Days'},
                {'name': 'Time', 'id': 'Time'},
                {'name': 'Loc', 'id': 'Loc'},
                {'name': 'Begin/End', 'id': 'Begin/End'},
                {'name': 'Instructor', 'id': 'Instructor'},
                {'name': '', 'id': 'colorRec'},
            ],
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
                               ['5%', '5.5%', '5.5%', '4.5%', '3.5%', '4.5%', '19.5%',
                                '3.5%', '3.5%', '3.0%', '5.5%', '9%', '7.5%', '8%', '10%', '2%'])
            ],
            style_data_conditional=[{'if': {'filter_query': '{colorRec} = ' + color, 'column_id': 'colorRec' }, 'color': color, 'backgroundColor': color, } for color in df['colorRec']],
            fixed_rows={'headers': True, 'data': 0},
            # page_size=500,
            editable=True,
            # virtualization=True,
            filter_action='native',
            sort_action='native',
            sort_mode='multi',
            filter_query = filter_query,
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
        )
    ]

def update_grid(data, filtered_data, slctd_row_indices):
    if DEBUG:
        print("function: update_grid")

    _dfLoc = pd.DataFrame(data)
    if len(filtered_data) > 0:
        _df = pd.DataFrame(filtered_data)
    else:
        return [ blankFigure() for k in range(6)]

    # replace all NaN or None in Loc with TBA
    for row in _df.index.tolist():
        if _df.loc[row, 'Loc'] != _df.loc[row, 'Loc'] or _df.loc[row, 'Loc'] == None:
            _df.loc[row, 'Loc'] = 'TBA'

    # remove classes without rooms
    _dfLoc = _dfLoc[_dfLoc['Campus'] != 'I']
    _dfLoc = _dfLoc[_dfLoc['Loc'] != 'TBA']
    _dfLoc = _dfLoc[_dfLoc['Loc'] != 'OFFC  T']
    _df = _df[_df['Campus'] != 'I']
    _df = _df[_df['Loc'] != 'TBA']
    _df = _df[_df['Loc'] != 'OFFC  T']

    # remove canceled classes
    _dfLoc = _dfLoc[_dfLoc['S'] != 'C']
    _df = _df[_df['S'] != 'C']

    # add columns for rectangle dimensions and annotation
    if not 'xRec' in _df.columns:
        _df.insert(len(_df.columns), 'xRec', 0)
    if not 'yRec' in _df.columns:
        _df.insert(len(_df.columns), 'yRec', 0)
    if not 'wRec' in _df.columns:
        _df.insert(len(_df.columns), 'wRec', 1)
    if not 'hRec' in _df.columns:
        _df.insert(len(_df.columns), 'hRec', 0)
    if not 'textRec' in _df.columns:
        _df.insert(len(_df.columns), 'textRec', '')
    if not 'alphaRec' in _df.columns:
        _df.insert(len(_df.columns), 'alphaRec', 1.0)

    if not 'timeLoc' in _df.columns:
        _df.insert(len(_df.columns), 'timeLoc', 0)
    _df['timeLoc'] = _df['Time'] + _df['Loc']


    # create figures for all tabs
    figs = []
    for d in ['M', 'T', 'W', 'R', 'F', 'S']:

        if DEBUG:
            print("function: update_grid {:s}".format(d))

        # create mask for particular tab
        mask = _df['Days'].str.contains(d, case=True, na=False)

        # apply the mask and use a copy of the dataframe
        df = _df[mask].copy()
        if DEBUG:
            print("function: update_grid {:s} {:d}".format(d, len(df.index.tolist())))

        # unique rooms and total number of unique rooms
        # if toggle:
        #     rooms = _dfLoc['Loc'].dropna().unique()
        # else:
        #     rooms = df['Loc'].dropna().unique()

        rooms = _dfLoc['Loc'].dropna().unique()

        Loc = dict(zip(sorted(rooms), range(len(rooms))))
        nLoc = len(list(Loc.keys()))

        # compute dimensions based on class time
        timeLoc = {}
        for row in df.index.tolist():

            # calculate x,y position and height of rectangles
            strTime = df.loc[row, 'Time']
            s = strTime[:5]
            e = strTime[-5:]
            try:
                yRec = 12*(int(s[:2])-8) + int(s[3:])//5
            except ValueError:
                yRec = 0
            try:
                hRec = 12*(int(e[:2])-8) + int(e[3:])//5 - yRec
            except ValueError:
                hRec = 0
            try:
                df.loc[row, 'xRec'] = Loc[df.loc[row, 'Loc']]
            except:
                df.loc[row, 'xRec'] = 0

            df.loc[row, 'yRec'] = yRec
            df.loc[row, 'hRec'] = hRec

            # create annotation for rectangle
            try:
                df.loc[row, 'textRec'] = df.loc[row, 'Subject'] + ' ' + df.loc[row, 'Number'] + '-' + df.loc[row, 'Section']
            except TypeError:
                df.loc[row, 'textRec'] = ''

            # check if time/location block is already in use
            if df.loc[row, 'timeLoc'] in timeLoc:
                timeLoc[df.loc[row, 'timeLoc']].append(row) # already in use, add to list
            else:
                timeLoc[df.loc[row, 'timeLoc']] = [row] # not in use, so create list

        # where times are already in use, change size of rectangles to place them
        # side-by-side in the grid
        for row in timeLoc.values():
            if len(row) > 1:
                for k in range(len(row)):
                    df.loc[row[k], 'xRec'] += k/len(row)
                    df.loc[row[k], 'wRec'] -= (len(row)-1)/len(row)

        fig = go.Figure()

        # we create a dictionary of all the shapes and annotations that will be on the grid
        ply_shapes = {}
        ply_annotations = {}
        for row in df.index.tolist():
            wRec = df.loc[row, 'wRec']
            hRec = df.loc[row, 'hRec']
            xRec = df.loc[row, 'xRec']
            yRec = df.loc[row, 'yRec']
            textRec = df.loc[row, 'textRec']
            colorRec = df.loc[row, 'colorRec']
            alphaRec = df.loc[row, 'alphaRec']

            ply_shapes['shape_' + str(row)] = go.layout.Shape(
                type='rect',
                xref='x', yref='y',
                y0 = xRec, x0 = yRec,
                y1 = xRec + wRec, x1 = (yRec + hRec),
                line=dict(
                    color='LightGray',
                    width=1,
                ),
                fillcolor=colorRec,
                opacity=alphaRec,
            )
            ply_annotations['annotation_' + str(row)] = go.layout.Annotation(
                xref='x', yref='y',
                y = xRec + wRec/2,
                x = (yRec + hRec/2),
                text = textRec,
                hoverlabel = {'bgcolor': '#064779'},
                hovertext = "Course: {}<br>Title: {}<br>CRN: {}<br>Time: {}<br>Credits: {}<br>Instr: {}".format(textRec, df.loc[row, 'Title'], df.loc[row, 'CRN'], df.loc[row, 'Time'], df.loc[row, 'Credit'], df.loc[row, 'Instructor']),
                showarrow = False,
                # we are getting a 0 font size when there are many classes, so take at least
                # the smallest font size to be 1.
                font = dict(size=max(1,min(int(.75*hRec),12))),
            )

        # alternating vertical shading for rooms
        for k in range(nLoc):
            if k%2:
                ply_shapes['shape_vertbar_' + str(k)] = go.layout.Shape(
                    type='rect',
                    xref='x', yref='y',
                    y0 = k, y1 = k+1,
                    x0 = 0, x1 = 170,
                    fillcolor='#f2f2f2',
                    layer='below', line_width=0,
                )
            else:
                ply_shapes['shape_vertbar_' + str(k)] = go.layout.Shape(
                    xref='x', yref='y',
                    y0 = k, y1 = k+1,
                    x0 = 0, x1 = 170,
                    fillcolor='white',
                    layer='below', line_width=0,
                )
        lst_shapes=list(ply_shapes.values())
        lst_annotations=list(ply_annotations.values())

        # setup the axes and tick marks
        if nLoc:
            fig.update_layout(
                autosize=False,
                height=45*nLoc,
                margin=dict(
                    l=50,
                    r=70,
                    b=10,
                    t=10,
                    pad=0
                ),
                yaxis = dict(
                    range=[0,nLoc],
                    tickvals=[k+.5 for k in range(nLoc)],
                    ticktext=list(Loc.keys()),
                    showgrid=False,
                    linecolor='#CCC',
                ),
                xaxis = dict(
                    range=[0,168.2],
                    tickvals=[k*12 for k in range(15)],
                    ticktext=[('0{:d}:00'.format(k))[-5:] for k in range(8,23)],
                    showgrid=True,
                    side='top',
                    gridwidth=1,
                    gridcolor='#DDD',
                    linecolor='#CCC',
                ),
                showlegend=False,
                annotations = lst_annotations,
                shapes=lst_shapes,
            )
        else:
            # nLoc is zero which makes the height zero, so show a blank figure
            fig.update_layout(
                height=90,
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
                },
                showlegend=False,
            )

        # place one point on the grid and hide it so that zoom reset works
        fig.add_trace(go.Scatter(x=[0.5*nLoc],y=[-85],
                                 hoverinfo='none',
                                 marker={'opacity': 0}))
        figs.append(fig)

    return figs

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
        xlsx_io, engine='xlsxwriter', engine_kwargs={'options':{'strings_to_numbers': False}}
    )
    _df.to_excel(writer, sheet_name='Schedule', index=False)

    # Save it
    writer.close()
    # writer.save()
    xlsx_io.seek(0)
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = base64.b64encode(xlsx_io.read()).decode('utf-8')

    return data

def generate_tab_fig(day, tab, fig):
    if DEBUG:
        print("function: generate_tab_fig")

    if fig is None:
        fig = blankFigure()

    modeBarButtonsToRemove = ['zoom2d',
                              'pan2d',
                              'select2d',
                              'lasso2d',
                              'zoomIn2d',
                              'zoomOut2d',
                              'autoScale2d',
                              'resetScale2d',
                              'hoverClosestCartesian',
                              'hoverCompareCartesian',
                              'zoom3d',
                              'pan3d',
                              'resetCameraDefault3d',
                              'resetCameraLastSave3d',
                              'hoverClosest3d',
                              'orbitRotation',
                              'tableRotation',
                              'zoomInGeo',
                              'zoomOutGeo',
                              'resetGeo',
                              'hoverClosestGeo',
                              # 'toImage',
                              'sendDataToCloud',
                              'hoverClosestGl2d',
                              'hoverClosestPie',
                              'toggleHover',
                              'resetViews',
                              'toggleSpikelines',
                              'resetViewMapbox']


    day_abbrv = day.lower()[:3]

    if day_abbrv == tab[-3:]:
        div_style = {'background': 'white', 'display': 'block', 'width': '100%'}
    else:
        div_style = {'background': 'white', 'display': 'none', 'width': '100%'}

    return html.Div([
        dcc.Loading(id='loading-icon-'+day_abbrv, children=[
            dcc.Graph(
                figure=fig,
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': modeBarButtonsToRemove,
                    'showAxisDragHandles': True,
                    'toImageButtonOptions': {'filename': day_abbrv},
                },
                id='schedule_'+day_abbrv,
            )], type='circle', color='#064779')],
        style=div_style,
        id='schedule_' + day_abbrv + '_div',
    )


# Create app layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.Img(id='msudenver-logo',
                         src=app.get_asset_url('msudenver-logo.png')),
                html.H3('Scheduling'),
                dcc.Upload(id='upload-data',
                           children=html.Button(['Upload file'],
                                                id='upload-data-button',
                                                n_clicks=0,
                                                style={'height': '38px'},
                                                className='button'),
                           multiple=False,
                           accept='.txt, .xlsx'),
                # accept='.txt, .csv, .xlsx'),
            ],
            id='header',
            style={'display': 'flex',
                   'justifyContent': 'space-between',
                   'alignItems': 'center'},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Tabs([generate_weekday_tab(day) for day in days ],
                                         id='weekdays-tabs',
                                         value='tab-mon')
                            ]
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        generate_tab_fig(day, 'tab-mon', None) for day in days
                                    ],
                                    id='weekdays-tabs-content',
                                    style={'width': '100%',
                                           'display': 'block',
                                           'marginLeft': 'auto',
                                           'marginRight': 'auto',
                                           'background': 'white'}
                                ),

                            ]
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div([
                                            dcc.Dropdown(
                                                id='filter-query-dropdown',
                                                options=[
                                                    {'label': 'Custom...', 'value': 'custom'},
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
                                                placeholder='Select a query',
                                                value=''),
                                        ],
                                                 style={'display': 'inline-block', 'width':'100%'}
                                                 ),
                                        html.Div(
                                            [
                                                html.Button('Apply Query', id='apply_query_button', className='button')
                                            ],
                                            style={'display': 'inline-block'}
                                        ),
                                        html.Label('All rooms:',
                                                   style={'display': 'none'},
                                                   id='all-rooms-label'),
                                        # daq.BooleanSwitch(id='toggle-rooms',
                                        #                   on=True,
                                        #                   disabled=False,
                                        #                   color='#e6e6e6',
                                        #                   style={'display': 'none'}),
                                    ],
                                    style={'marginTop': '7px', 'marginLeft': '5px', 'display': 'flex',
                                           'justifyContent': 'space-between'}
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
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
                                    ]
                                ),
                            ]
                        )
                    ]
                ),
                html.Div([ html.Hr(),]),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Button('Update Grid', id='update-grid-button', n_clicks=0,
                                            style={'marginLeft': '5px'},className='button'),
                                html.Button('Export All', id='export-all-button', n_clicks=0,
                                            style={'marginLeft': '5px'},className='button'),
                                dcc.Download(id='datatable-download'),
                                html.Button('Export Filtered', id='export-filtered-button',n_clicks=0,
                                            style={'marginLeft': '5px'},className='button'),
                                dcc.Download(id='datatable-filtered-download'),
                                html.Button('Add Row', id='add-row-button', n_clicks=0,
                                            style={'marginLeft': '5px'}, className='button'),
                                html.Button('Delete Row(s)', id='delete-rows-button', n_clicks=0,
                                            style={'marginLeft': '5px'}, className='button'),
                                html.Button('Reset Colors', id='reset-colors-button', n_clicks=0,
                                            style={'marginLeft': '5px'},className='button'),
                                html.Button('Change Color', id='change-color-button', n_clicks=0,
                                            style={'marginLeft': '5px'},className='button'),
                            ],
                            style={
                                'display': 'inline-block',
                            }
                        ),
                        html.Div(
                            [
                                dcc.Dropdown(id='color-select',
                                             options=[
                                             # {'label': html.Span(['Blue'], style={'background': '#b3cde3'}), 'value': '#b3cde3'}, # only dash 2.5 or above
                                             {'label': 'Blue', 'value': '#b3cde3'},
                                             {'label': 'Red', 'value': '#fbb4ae'},
                                             {'label': 'Green', 'value': '#ccebc5'},
                                             {'label': 'Purple', 'value': '#decbe4'},
                                             {'label': 'Orange', 'value': '#fed9a6'},
                                             {'label': 'Yellow', 'value': '#ffffcc'},
                                             {'label': 'Tan', 'value': '#e5d8bd'},
                                             {'label': 'Pink', 'value': '#fddaec'},
                                             {'label': 'Gray','value': '#f2f2f2'},
                                             ],
                                             value='#b3cde3',
                                             clearable=False,
                                             ),
                            ],
                            style={
                                'display': 'inline-block',
                                'width': '10%',
                            }
                        ),
                    ],
                    style={
                        'width': '100%',
                        'display': 'flex',
                    }
                ),
                html.Div([ html.Br(),]),
                html.Div(
                    id='datatable-interactivity-container',
                    children=[
                        dash_table.DataTable(
                            id='datatable-interactivity',
                            data = [{}],
                        )
                    ],
                    style={
                        'width': '100%',
                        'display': 'block',
                        'marginLeft': 'auto',
                        'marginRight': 'auto'},
                ),
            ],
            id='output-data-upload',
            style={'display': 'none'}
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
    if DEBUG:
        print("function: show_contents")
    if contents is not None:
        return {'display': 'block'}

@app.callback(
    [Output('weekdays-tabs-content', 'children'),
     Output('datatable-interactivity-container', 'children')],
    [Input('update-grid-button', 'n_clicks'),
     Input('reset-colors-button', 'n_clicks'),
     Input('change-color-button', 'n_clicks'),
     State('weekdays-tabs', 'value'),
     State('upload-data', 'filename'),
     Input('upload-data', 'contents'),
     Input("datatable-interactivity", "data_timestamp"),
     State("datatable-interactivity", "filter_query"),
     State("datatable-interactivity", "data"),
     State('datatable-interactivity', 'derived_virtual_data'),
     State('datatable-interactivity', 'derived_virtual_indices'),
     State('datatable-interactivity', 'derived_virtual_selected_rows'),
     State('color-select', 'value')
    ]
)
def data_loading(
    update_n_clicks,
    select_n_clicks,
    deselect_n_clicks,
    tab,
    name,
    contents,
    timestamp,
    filter_query,
    rows,
    filtered_rows,
    vtl_indices,
    slctd_row_indices,
    slctd_color
):

    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if DEBUG:
        print('function: data_loading')
        print('Trigger: {:s}'.format(input_id))

    df = pd.DataFrame(rows)

    _index = slctd_row_indices

    if len(rows) != len(filtered_rows):
        _index = vtl_indices

    if contents is not None and input_id == 'upload-data':
        df = parse_contents(contents, name)
        # print(df.to_string())
        df['colorRec'] = '#b3cde3'

    if input_id == 'reset-colors-button':
        df['colorRec'] = '#b3cde3'

    if input_id == "change-color-button":
        df.loc[_index, 'colorRec'] = slctd_color

    data_children = create_datatable(df, filter_query)

    if input_id == 'update-grid-button':
        df = pd.DataFrame(filtered_rows)
        figs = update_grid(df.to_dict(), df.to_dict(), [])
        # figs = update_grid(True, df.to_dict(), df.to_dict(), [])
        tabs_children = [ generate_tab_fig(day, tab, fig) for day, fig in zip(days, figs)]
    else:
        figs = update_grid(df.to_dict(), df.to_dict(), [])
        # figs = update_grid(True, df.to_dict(), df.to_dict(), [])
        tabs_children = [ generate_tab_fig(day, tab, fig) for day, fig in zip(days, figs)]


    return tabs_children, data_children


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
    if DEBUG:
        print("function: update_tab_display")
    ctx = dash.callback_context
    if 'weekdays-tabs' in ctx.triggered[0]['prop_id']:
        styles = []
        for t in ['tab-mon', 'tab-tue', 'tab-wed', 'tab-thu', 'tab-fri', 'tab-sat']:
            if t == tab:
                styles.append({'display': 'block'})
            else:
                styles.append({'display': 'none'})
        return styles[:]


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
    input_id = (ctx.triggered[0]['prop_id'].split('.')[0])

    if DEBUG:
        print("function: alter_row")
        print('Trigger: {:s}'.format(input_id))

    if input_id == 'add-row-button':
        rows.append(
            {'Subject': '', 'Number':'', 'CRN': '', 'Section': '', 'S': 'A',
             'Campus': '', 'Title': '', 'Credit': '', 'Max': '', 'Enrl': '', 'Days': '',
             'Time': '', 'Loc': 'TBA', 'Being/End': '', 'Instructor': ',',
             'colorRec': '#b3cde3'}
        )

    # don't allow deleting of everything at once
    if input_id == 'delete-rows-button' and len(selected_rows) != len(rows):
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
    [Output('datatable-interactivity', 'filter_query')],
    [Input('apply_query_button', 'n_clicks'),
     Input('filter-query-input', 'n_submit'),
     State('filter-query-dropdown', 'value'),
     State('filter-query-input', 'value')]
)
def apply_query(n_clicks, n_submit, dropdown_value, input_value):
    if DEBUG:
        print("function: apply_query")
    # if n_clicks > 0:
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
    if DEBUG:
        print("function: export_all")
    _df = pd.DataFrame(data)
    if n_clicks > 0:
        return {'base64': True, 'content': to_excel(_df), 'filename': 'Schedule.xlsx', }


@app.callback(
    Output('datatable-filtered-download', 'data'),
    [Input('export-filtered-button', 'n_clicks'),
     State('datatable-interactivity', 'derived_virtual_data')]
)
def export_filtered(n_clicks, data):
    if DEBUG:
        print("function: export_filtered")
    _df = pd.DataFrame(data)
    if n_clicks > 0:
        return {'base64': True, 'content': to_excel(_df), 'filename': 'Schedule.xlsx', }


# Main
if __name__ == '__main__':
    if mathserver:
        app.run_server(debug=DEBUG)
    else:
        # app.run_server(debug=DEBUG, host='10.0.2.15', port='8051')
        app.run_server(debug=DEBUG, port='8051')


'''
            aliceblue, antiquewhite, aqua, aquamarine, azure,
            beige, bisque, black, blanchedalmond, blue,
            blueviolet, brown, burlywood, cadetblue,
            chartreuse, chocolate, coral, cornflowerblue,
            cornsilk, crimson, cyan, darkblue, darkcyan,
            darkgoldenrod, darkgray, darkgrey, darkgreen,
            darkkhaki, darkmagenta, darkolivegreen, darkorange,
            darkorchid, darkred, darksalmon, darkseagreen,
            darkslateblue, darkslategray, darkslategrey,
            darkturquoise, darkviolet, deeppink, deepskyblue,
            dimgray, dimgrey, dodgerblue, firebrick,
            floralwhite, forestgreen, fuchsia, gainsboro,
            ghostwhite, gold, goldenrod, gray, grey, green,
            greenyellow, honeydew, hotpink, indianred, indigo,
            ivory, khaki, lavender, lavenderblush, lawngreen,
            lemonchiffon, lightblue, lightcoral, lightcyan,
            lightgoldenrodyellow, lightgray, lightgrey,
            lightgreen, lightpink, lightsalmon, lightseagreen,
            lightskyblue, lightslategray, lightslategrey,
            lightsteelblue, lightyellow, lime, limegreen,
            linen, magenta, maroon, mediumaquamarine,
            mediumblue, mediumorchid, mediumpurple,
            mediumseagreen, mediumslateblue, mediumspringgreen,
            mediumturquoise, mediumvioletred, midnightblue,
            mintcream, mistyrose, moccasin, navajowhite, navy,
            oldlace, olive, olivedrab, orange, orangered,
            orchid, palegoldenrod, palegreen, paleturquoise,
            palevioletred, papayawhip, peachpuff, peru, pink,
            plum, powderblue, purple, red, rosybrown,
            royalblue, rebeccapurple, saddlebrown, salmon,
            sandybrown, seagreen, seashell, sienna, silver,
            skyblue, slateblue, slategray, slategrey, snow,
            springgreen, steelblue, tan, teal, thistle, tomato,
            turquoise, violet, wheat, white, whitesmoke,
            yellow, yellowgreen
'''
