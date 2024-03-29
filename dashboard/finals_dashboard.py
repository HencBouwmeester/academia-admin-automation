# -*- coding: utf-8 -*-
from utilities import *

# Import required libraries
from dash import html, dcc, dash_table, callback_context, Dash
from pandas import set_option, DataFrame, read_fwf, __version__, \
        to_numeric, read_excel, merge, ExcelWriter
from plotly import io as pio
from base64 import b64decode, b64encode
from io import StringIO, BytesIO
from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta
import plotly.graph_objects as go

DEBUG = False
mathserver = False

# Include pretty graph formatting
pio.templates.default = 'plotly_white'

set_option('display.max_rows', None)

# Initialize server
app = Dash(
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
       'url_base_pathname':'/finals/',
       'routes_pathname_prefix':'/finals/',
       'requests_pathname_prefix':'/finals/',
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

def generate_tab_fig(day, tab, fig):
    if DEBUG:
        print("function: generate_tab_fig")
    # blank figure when no data is present

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

def update_grid(data):#toggle, data, filtered_data, slctd_row_indices):
    if DEBUG:
        print("function: update_grid")

    _df = DataFrame(data)

    _df.rename(columns={'Final_Day':'Days', 'Final_Time': 'Time', 'Final_Loc': 'Loc'}, inplace=True)

    if not 'Campus' in _df.columns:
        _df.insert(len(_df.columns), 'Campus', 'M')
    if not 'S' in _df.columns:
        _df.insert(len(_df.columns), 'S', 'A')

    # replace all NaN or None in Loc with TBA
    for row in _df.index.tolist():
        if _df.loc[row, 'Loc'] != _df.loc[row, 'Loc'] or _df.loc[row, 'Loc'] == None:
            _df.loc[row, 'Loc'] = 'TBA'

    # remove classes without rooms
    _df = _df[_df['Campus'] != 'I']
    _df = _df[_df['Loc'] != 'TBA']
    _df = _df[_df['Loc'] != 'OFFC  T']

    # remove canceled classes
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

        rooms = df['Loc'].dropna().unique()

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
            colorRec = '#b3cde3'
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
                hovertext = "Course: {}<br>Title: {}<br>CRN: {}<br>Time: {}<br>Instr: {}".format(textRec, df.loc[row, 'Title'], df.loc[row, 'CRN'], df.loc[row, 'Time'], df.loc[row, 'Instructor']),
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


def create_time(row):
    return row['Start Time'][:-3].replace(':','').zfill(4) + '-' + row['End Time'][:-3].replace(':','').zfill(4) + row['End Time'][-2:]

def find_day(row):
    try:
        day_str = datetime.strptime(row['Date'][:-4], '%m/%d/%Y').strftime('%A')
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
    except:
        pass

    return Days


def correct_date(row):
    return row['Date'][:-4]


def convertAMPMtime_grid(timeslot):
    try:
        starthour = int(timeslot.split(':')[0])

        if timeslot[-2:].upper() == 'PM':
            starthour = starthour + 12 if starthour < 12 else starthour
        timeslot = '{:s}:{:s}'.format(
            str(starthour).zfill(2), timeslot.split(':')[1][:2]
        )
    except ValueError:  # catch the TBA times
        pass

    return timeslot

finals_grid = [
   '3','2', 'M W', '6:30am', '7:45am', 'W', '06:30-08:30',
   '3','2', 'M W', '8:00am', '9:15am', 'M', '08:00-10:00',
   '3','2', 'M W', '9:30am', '10:45am', 'W', '09:30-11:30',
   '3','2', 'M W', '11:00am', '12:15pm', 'M', '11:00-13:00',
   '3','2', 'M W', '12:30pm', '1:45pm', 'W', '12:30-14:30',
   '3','2', 'M W', '2:00pm', '3:15pm', 'M', '14:00-16:00',
   '3','2', 'M W', '3:30pm', '4:45pm', 'W', '15:30-17:30',
   '3','2', 'M W', '5:00pm', '6:15pm', 'M', '17:00-19:00',
   '3','2', 'M W', '6:30pm', '7:45pm', 'W', '18:30-20:30',
   '3','2', 'M W', '8:00pm', '9:15pm', 'M', '20:00-22:00',
   '3','2', 'M W', '9:30pm', '10:45pm', 'W', '21:30-23:30',
   '3','2', 'T R', '6:30am', '7:45am', 'R', '06:30-08:30',
   '3','2', 'T R', '8:00am', '9:15am', 'T', '08:00-10:00',
   '3','2', 'T R', '9:30am', '10:45am', 'R', '09:30-11:30',
   '3','2', 'T R', '11:00am', '12:15pm', 'T', '11:00-13:00',
   '3','2', 'T R', '12:30pm', '1:45pm', 'R', '12:30-14:30',
   '3','2', 'T R', '2:00pm', '3:15pm', 'T', '14:00-16:00',
   '3','2', 'T R', '3:30pm', '4:45pm', 'R', '15:30-17:30',
   '3','2', 'T R', '5:00pm', '6:15pm', 'T', '17:00-19:00',
   '3','2', 'T R', '6:30pm', '7:45pm', 'R', '18:30-20:30',
   '3','2', 'T R', '8:00pm', '9:15pm', 'T', '20:00-22:00',
   '3','2', 'T R', '9:30pm', '10:45pm', 'R', '21:30-23:30',
   '3','1', 'M', '8:00am', '10:50am', 'M', '08:00-10:00',
   '3','1', 'M', '9:30am', '12:20pm', 'M', '11:00-13:00',
   '3','1', 'M', '11:00am', '1:50pm', 'M', '11:00-13:00',
   '3','1', 'M', '12:30pm', '3:20pm', 'M', '14:00-16:00',
   '3','1', 'M', '2:00pm', '4:50pm', 'M', '14:00-16:00',
   '3','1', 'M', '3:30pm', '6:20pm', 'M', '17:00-19:00',
   '3','1', 'M', '5:00pm', '7:50pm', 'M', '17:00-19:00',
   '3','1', 'M', '6:30pm', '9:20pm', 'M', '20:00-22:00',
   '3','1', 'M', '8:00pm', '10:50pm', 'M', '20:00-22:00',
   '3','1', 'T', '8:00am', '10:50am', 'T', '08:00-10:00',
   '3','1', 'T', '9:30am', '12:20pm', 'T', '11:00-13:00',
   '3','1', 'T', '11:00am', '1:50pm', 'T', '11:00-13:00',
   '3','1', 'T', '12:30pm', '3:20pm', 'T', '14:00-16:00',
   '3','1', 'T', '2:00pm', '4:50pm', 'T', '14:00-16:00',
   '3','1', 'T', '3:30pm', '6:20pm', 'T', '17:00-19:00',
   '3','1', 'T', '5:00pm', '7:50pm', 'T', '17:00-19:00',
   '3','1', 'T', '6:30pm', '9:20pm', 'T', '20:00-22:00',
   '3','1', 'T', '8:00pm', '10:50pm', 'T', '20:00-22:00',
   '3','1', 'W', '8:00am', '10:50am', 'W', '09:30-11:30',
   '3','1', 'W', '9:30am', '12:20pm', 'W', '09:30-11:30',
   '3','1', 'W', '11:00am', '1:50pm', 'W', '12:30-14:30',
   '3','1', 'W', '12:30pm', '3:20pm', 'W', '12:30-14:30',
   '3','1', 'W', '2:00pm', '4:50pm', 'W', '15:30-17:30',
   '3','1', 'W', '3:30pm', '6:20pm', 'W', '15:30-17:30',
   '3','1', 'W', '5:00pm', '7:50pm', 'W', '18:30-20:30',
   '3','1', 'W', '6:30pm', '9:20pm', 'W', '18:30-20:30',
   '3','1', 'W', '8:00pm', '10:50pm', 'W', '21:30-23:30',
   '3','1', 'R', '8:00am', '10:50am', 'R', '09:30-11:30',
   '3','1', 'R', '9:30am', '12:20pm', 'R', '09:30-11:30',
   '3','1', 'R', '11:00am', '1:50pm', 'R', '12:30-14:30',
   '3','1', 'R', '12:30pm', '3:20pm', 'R', '12:30-14:30',
   '3','1', 'R', '2:00pm', '4:50pm', 'R', '15:30-17:30',
   '3','1', 'R', '3:30pm', '6:20pm', 'R', '15:30-17:30',
   '3','1', 'R', '5:00pm', '7:50pm', 'R', '18:30-20:30',
   '3','1', 'R', '6:30pm', '9:20pm', 'R', '18:30-20:30',
   '3','1', 'R', '8:00pm', '10:50pm', 'R', '21:30-23:30',
   '3','3', 'M W F', '6:00am', '6:50am', 'W', '06:30-08:30',
   '3','3', 'M W F', '7:00am', '7:50am', 'F', '07:00-09:00',
   '3','3', 'M W F', '8:00am', '8:50am', 'M', '08:00-10:00',
   '3','3', 'M W F', '9:00am', '9:50am', 'W', '09:30-11:30',
   '3','3', 'M W F', '10:00am', '10:50am', 'F', '10:00-12:00',
   '3','3', 'M W F', '11:00am', '11:50am', 'M', '11:00-13:00',
   '3','3', 'M W F', '12:00pm', '12:50pm', 'W', '12:30-14:30',
   '3','3', 'M W F', '1:00pm', '1:50pm', 'F', '13:00-15:00',
   '3','3', 'M W F', '2:00pm', '2:50pm', 'M', '14:00-16:00',
   '3','3', 'M W F', '3:00pm', '3:50pm', 'W', '15:30-17:30',
   '3','3', 'M W F', '4:00pm', '4:50pm', 'F', '16:00-18:00',
   '3','3', 'M W F', '5:00pm', '5:50pm', 'M', '17:00-19:00',
   '3','3', 'M W F', '6:00pm', '6:50pm', 'W', '18:30-20:30',
   '3','3', 'M W F', '7:00pm', '7:50pm', 'F', '19:00-21:00',
   '3','3', 'M W F', '8:00pm', '8:50pm', 'M', '20:00-22:00',
   '3','3', 'M W F', '9:00pm', '9:50pm', 'W', '21:30-23:30',
   '3','3', 'M W F', '10:00pm', '10:50pm', 'F', '22:00-24:00',
   '4','3', 'M W F', '8:00am', '9:10am', 'M', '08:00-10:00',
   '4','3', 'M W F', '9:30am', '10:40am', 'F', '10:00-12:00',
   '4','3', 'M W F', '11:00am', '12:10pm', 'M', '11:00-13:00',
   '4','3', 'M W F', '12:30pm', '1:40pm', 'F', '13:00-15:00',
   '4','3', 'M W F', '2:00pm', '3:10pm', 'M', '14:00-16:00',
   '4','3', 'M W F', '3:30pm', '4:40pm', 'F', '16:00-18:00',
   '4','3', 'M W F', '5:00pm', '6:10pm', 'M', '17:00-19:00',
   '4','3', 'M W F', '6:30pm', '7:40pm', 'F', '19:00-21:00',
   '4','3', 'M W F', '8:00pm', '9:10pm', 'M', '20:00-22:00',
   '4','1', 'M', '8:00am', '11:50am', 'M', '08:00-10:00',
   '4','1', 'M', '12:00pm', '3:50pm', 'M', '14:00-16:00',
   '4','1', 'M', '4:00pm', '7:50pm', 'M', '17:00-19:00',
   '4','1', 'T', '8:00am', '11:50am', 'T', '08:00-10:00',
   '4','1', 'T', '12:00pm', '3:50pm', 'T', '14:00-16:00',
   '4','1', 'T', '4:00pm', '7:50pm', 'T', '17:00-19:00',
   '4','1', 'W', '8:00am', '11:50am', 'W', '09:30-11:30',
   '4','1', 'W', '12:00pm', '3:50pm', 'W', '12:30-14:30',
   '4','1', 'W', '4:00pm', '7:50pm', 'W', '18:30-20:30',
   '4','1', 'R', '8:00am', '11:50am', 'R', '09:30-11:30',
   '4','1', 'R', '12:00pm', '3:50pm', 'R', '12:30-14:30',
   '4','1', 'R', '4:00pm', '7:50pm', 'R', '18:30-20:30',
   '4','1', 'F', '8:00am', '11:50am', 'F', '10:00-12:00',
   '4','1', 'F', '12:00pm', '3:50pm', 'F', '13:00-15:00',
   '4','1', 'F', '4:00pm', '7:50pm', 'F', '16:00-18:00',
   '5','3', 'M W F', '8:00am', '9:24am', 'M', '08:00-10:00',
   '5','3', 'M W F', '10:00am', '11:25am', 'F', '10:00-12:00',
   '5','3', 'M W F', '12:00pm', '1:25pm', 'W', '12:30-14:30',
   '5','3', 'M W F', '2:00pm', '3:25pm', 'M', '14:00-16:00',
   '5','3', 'M W F', '4:00pm', '5:25pm', 'F', '16:00-18:00',
   '5','3', 'M W F', '6:00pm', '7:25pm', 'W', '18:30-20:30',
   '5','3', 'M W F', '8:00pm', '9:25pm', 'M', '20:00-22:00',
   '4','2', 'M W', '8:00am', '9:50am', 'M', '08:00-10:00',
   '4','2', 'M W', '10:00am', '11:50am', 'W', '09:30-11:30',
   '4','2', 'M W', '12:00pm', '1:50pm', 'M', '11:00-13:00',
   '4','2', 'M W', '2:00pm', '3:50pm', 'M', '14:00-16:00',
   '4','2', 'M W', '4:00pm', '5:50pm', 'W', '15:30-17:30',
   '4','2', 'M W', '6:00pm', '7:50pm', 'M', '17:00-19:00',
   '4','2', 'M W', '8:00pm', '9:50pm', 'M', '20:00-22:00',
   '4','2', 'T R', '8:00am', '9:50am', 'T', '08:00-10:00',
   '4','2', 'T R', '10:00am', '11:50am', 'R', '09:30-11:30',
   '4','2', 'T R', '12:00pm', '1:50pm', 'T', '11:00-13:00',
   '4','2', 'T R', '2:00pm', '3:50pm', 'T', '14:00-16:00',
   '4','2', 'T R', '4:00pm', '5:50pm', 'R', '15:30-17:30',
   '4','2', 'T R', '6:00pm', '7:50pm', 'T', '17:00-19:00',
   '4','2', 'T R', '8:00pm', '9:50pm', 'T', '20:00-22:00',
   '2','2', 'M W', '8:00am', '9:50am', 'M', '08:00-10:00',
   '2','2', 'M W', '10:00am', '11:50am', 'W', '09:30-11:30',
   '2','2', 'M W', '12:00pm', '1:50pm', 'M', '11:00-13:00',
   '2','2', 'M W', '2:00pm', '3:50pm', 'M', '14:00-16:00',
   '2','2', 'M W', '4:00pm', '5:50pm', 'W', '15:30-17:30',
   '2','2', 'M W', '6:00pm', '7:50pm', 'M', '17:00-19:00',
   '2','2', 'M W', '8:00pm', '9:50pm', 'M', '20:00-22:00',
   '2','2', 'T R', '8:00am', '9:50am', 'T', '08:00-10:00',
   '2','2', 'T R', '10:00am', '11:50am', 'R', '09:30-11:30',
   '2','2', 'T R', '12:00pm', '1:50pm', 'T', '11:00-13:00',
   '2','2', 'T R', '2:00pm', '3:50pm', 'T', '14:00-16:00',
   '2','2', 'T R', '4:00pm', '5:50pm', 'R', '15:30-17:30',
   '2','2', 'T R', '6:00pm', '7:50pm', 'T', '17:00-19:00',
   '2','2', 'T R', '8:00pm', '9:50pm', 'T', '20:00-22:00',
   '2','1', 'M W', '8:00am', '9:50am', 'M', '08:00-10:00',
   '2','1', 'M W', '10:00am', '11:50am', 'W', '09:30-11:30',
   '2','1', 'M W', '12:00pm', '1:50pm', 'M', '11:00-13:00',
   '2','1', 'M W', '2:00pm', '3:50pm', 'M', '14:00-16:00',
   '2','1', 'M W', '4:00pm', '5:50pm', 'W', '15:30-17:30',
   '2','1', 'M W', '6:00pm', '7:50pm', 'M', '17:00-19:00',
   '2','1', 'M W', '8:00pm', '9:50pm', 'M', '20:00-22:00',
   '2','1', 'T R', '8:00am', '9:50am', 'T', '08:00-10:00',
   '2','1', 'T R', '10:00am', '11:50am', 'R', '09:30-11:30',
   '2','1', 'T R', '12:00pm', '1:50pm', 'T', '11:00-13:00',
   '2','1', 'T R', '2:00pm', '3:50pm', 'T', '14:00-16:00',
   '2','1', 'T R', '4:00pm', '5:50pm', 'R', '15:30-17:30',
   '2','1', 'T R', '6:00pm', '7:50pm', 'T', '17:00-19:00',
   '2','1', 'T R', '8:00pm', '9:50pm', 'T', '20:00-22:00',
]

df_grid = DataFrame({'Credit': finals_grid[::7], 'Meetings': finals_grid[1::7],
                        'Class_Days': finals_grid[2::7], 'Class_Start': finals_grid[3::7],
                        'Class_End': finals_grid[4::7], 'Final_Day': finals_grid[5::7],
                        'Final_Time': finals_grid[6::7]})
df_grid['Class_Start'] = df_grid['Class_Start'].apply(lambda x: convertAMPMtime_grid(x))
df_grid['Class_End'] = df_grid['Class_End'].apply(lambda x: convertAMPMtime_grid(x))


def tidy_csv_old(file_contents):
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

    return tidy_txt(StringIO('\n'.join(_list)))

def tidy_xlsx_old(file_contents):
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

    _df = read_excel(file_contents,
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
              'Credit', 'Max', 'Enrolled', 'Days', 'Time', 'Loc', 'Begin/End', 'Instructor']]

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

    decoded = b64decode(content_string)

    df = pd.DataFrame()
    if 'txt' in filename:
        df, _, _ = tidy_txt(StringIO(decoded.decode('utf-8')))
    elif 'csv' in filename:
        df = tidy_csv(StringIO(decoded.decode('utf-8')))
    elif 'xlsx' in filename:
        df, _, _ = tidy_xlsx(BytesIO(decoded))

    df = df[df['Credit']>0]
    df = df[df['S']!='C']
    df['Time'] = df['Time'].apply(lambda x: convertAMPMtime(x))
    df = df[['Subject', 'Number', 'CRN', 'Section', 'S', 'Campus', 'Title', 'Credit', 'Max', 'Enrolled', 'Days', 'Time', 'Loc', 'Begin/End', 'Instructor', 'Class']].copy()
    return df

def parse_finals_xlsx(contents, CRNs):
    content_type, content_string = contents.split(',')

    decoded = b64decode(content_string)
    df = read_excel(BytesIO(decoded),
                       engine='openpyxl',
                       converters={
                           'CRN': str,
                           'Final Exam Date': str,
                           'Start TIme': str,
                           'End Time': str,
                           'Location': str
                       },
                      )
    df = df[df['CRN'].notna()]
    indexCRN =  df[df['CRN']=="CRN"].index
    df.drop(indexCRN, inplace=True)
    df.rename(columns={'Final Exam Date': 'Date', 'Location': 'Loc', 'Days': 'Days_old'}, inplace=True)
    df.insert(len(df.columns), 'Time', ' ')
    df.insert(len(df.columns), 'Days', ' ')
    df['Time'] = df.apply(lambda row: create_time(row), axis=1)
    df['Days'] = df.apply(lambda row: find_day(row), axis=1)
    df['Date'] = df.apply(lambda row: correct_date(row), axis=1)

    df = df[['CRN', 'Class', 'Days', 'Time', 'Loc', 'Date']]

    df['Time'] = df['Time'].apply(lambda x: convertAMPMtime(x))

    df = merge(DataFrame({'CRN': CRNs}), df, how="left", on="CRN")
    df = df[df['Date'].notna()]

    df.drop_duplicates(inplace=True)
    return df


def parse_finals_csv(contents, CRNs):

    # subjects: list of subjects from enrollment report

    content_type, content_string = contents.split(',')

    decoded = b64decode(content_string)

    _file = StringIO(decoded.decode('utf-8')).read()
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

        fields = [field.replace('"','') for field in line.split(',')]

        # only pick up classes for CRN listed in enrollment report
        try:
            Class = fields[1].split(' ')[0]
            CRN = fields[1].split(' ')[1]
            if CRN in CRNs:
                Loc = fields[3]
                try:
                    Date = datetime.strptime(fields[6], '%m/%d/%Y').strftime('%m/%d/%Y')
                except ValueError:
                    Date = datetime.strptime(fields[6], '%x').strftime('%m/%d/%Y')

                # reformat the time to match the SWRCGSR formatting
                start_time = fields[7].replace(':','')[:-2].zfill(4)
                end_time = fields[8].replace(':','')[:-2].zfill(4)
                AMPM = fields[8][-2:]
                Time = start_time + '-' + end_time + AMPM

                # find the day of week and code it to MTWRFSU
                day_str = datetime.strptime(Date, '%m/%d/%Y').strftime('%A')
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

                rows.append([CRN, Class, Days, Time, Loc, Date])
        except IndexError:
            pass

    df = DataFrame(rows, columns=['CRN', 'Class', 'Days', 'Time', 'Loc', 'Date'])
    df['Time'] = df['Time'].apply(lambda x: convertAMPMtime(x))

    return df

def to_excel(df):
    if DEBUG:
        print("function: to_excel")
    _df = df.copy()

    # only grab needed columns and correct ordering
    cols = ['Subject', 'Number', 'CRN', 'Section', 'Title', 'Instructor',
            'Final_Day', 'Final_Time', 'Final_Loc', 'Final_Date', 'Error',]
    _df = _df[cols]
    _df.rename(columns={'Final_Day':'Days', 'Final_Time': 'Time', 'Final_Loc': 'Loc'}, inplace=True)

    xlsx_io = BytesIO()
    writer = ExcelWriter(
        xlsx_io, engine='xlsxwriter', engine_kwargs={'options':{'strings_to_numbers': False}}
    )
    _df.to_excel(writer, sheet_name='Final Exam Schedule', index=False)

    # Save it
    writer.close()
    xlsx_io.seek(0)
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = b64encode(xlsx_io.read()).decode('utf-8')

    return data

def no_final(e, f):
    indexFilter = []
    for row in e.index.tolist():
        CRN = e.loc[row, 'CRN']

        if f[f['CRN'] == CRN].shape[0] == 0:
            indexFilter.append(row)
    return indexFilter

def multiple_finals(e, f):
    indexFilter = []
    for row in e.index.tolist():
        CRN = e.loc[row, 'CRN']

        if f[f['CRN'] == CRN].shape[0] > 1:
            indexFilter.append(row)
    return indexFilter

def correct_final_day(e, f):
    indexFilter = []
    for row in e.index.tolist():
        CRN = e.loc[row, 'CRN']

        day = f[f['CRN'] == CRN]['Days'].iloc[0]
        days = e.loc[row, 'Days']

        if days.find(day) < 0:

            # day of week does not match, is this an Algebra class
            if e.loc[row, 'Number'] in ['1109', '1110', '1111']:
                if day != "S":
                    indexFilter.append(row)

            else:
                indexFilter.append(row)

    return indexFilter

def room_exist(e, f, r):
    indexFilter = []
    for row in e.index.tolist():
        CRN = e.loc[row, 'CRN']

        d = f[f['CRN'] == CRN]
        if d.iloc[0, 4] not in r['Room'].tolist():
            indexFilter.append(row)
    return indexFilter

def final_room_capacity(df, room_capacities):
    indexFilter = []
    for row in df.index.tolist():
        enrl = df[(df['Final_Loc'] == df.loc[row, 'Final_Loc']) & \
                  (df['Final_Time'] == df.loc[row, 'Final_Time']) & \
                  (df['Final_Day'] == df.loc[row, 'Final_Day'])]['Enrolled'].sum()
        if (enrl > int(room_capacities[df.loc[row, 'Final_Loc']])):
            indexFilter.append(row)
    return indexFilter

def within_one_hour(e):
    indexFilter = []
    for row in e.index.tolist():
        class_start = datetime.strptime(e.loc[row, 'Time'][:5], "%H:%M")
        plusone = class_start + timedelta(hours=1)
        minusone = class_start + timedelta(hours=-1)

        final_start = datetime.strptime(e.loc[row, 'Final_Time'][:5], "%H:%M")
        final_day = e.loc[row, 'Final_Day']
        if (final_start < minusone or final_start > plusone) and (final_day != "S"):
            indexFilter.append(row)
    return indexFilter

def instructor_overlap(enrl):
    indexFilter = []
    instructors = enrl['Instructor'].unique()
    for instructor in instructors:
        # filter by instructor
        _df = enrl[enrl['Instructor'] == instructor]
        days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
        for day in days:
            # filter by day
            df = _df[_df['Final_Day'] == day]

            # check for instructor overlap of same time blocks
            # (this does not calculate all overlaps)
            if df.shape[0] > 1:
                # every final time block should have a unique location
                for row in df.index.tolist():
                    if df[df['Final_Time'] == df.loc[row, 'Final_Time']]['Final_Loc'].nunique() > 1:
                        indexFilter.append(row)
    return indexFilter

def instructor_nonconformal_overlap(enrl):
    indexFilter = []
    instructors = enrl['Instructor'].unique()
    for instructor in instructors:
        # filter by instructor
        _df = enrl[enrl['Instructor'] == instructor]
        days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
        for day in days:
            # filter by day
            df = _df[_df['Final_Day'] == day]

            # check nonconformal overlaps; this uses SUMPRODUCT
            times = df['Final_Time'].unique().tolist()
            n = len(times)
            if n > 1:
                start_times = [datetime.strptime(time[:5], "%H:%M") for time in times]
                end_times = [datetime.strptime(time[-5:], "%H:%M") for time in times]
                for k in range(n):
                    s = ([x > start_times[k] for x in end_times])
                    e = ([x < end_times[k] for x in start_times])
                    if sum([x*y for x,y in zip(s,e)]) > 1:
                        for row in df.index.tolist():
                            if df.loc[row, 'Final_Time'] == times[k]:
                                indexFilter.append(row)
    return indexFilter

def instructor_back_to_back(enrl):
    indexFilter = []
    instructors = enrl['Instructor'].unique()
    for instructor in instructors:
        # filter by instructor
        _df = enrl[enrl['Instructor'] == instructor]
        days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
        for day in days:
            # filter by day
            df = _df[_df['Final_Day'] == day]

            # check nonconformal overlaps; this uses SUMPRODUCT
            times = df['Final_Time'].unique().tolist()
            n = len(times)
            if n > 1:
                # check for instructor back-to-back (different rooms) within 15 minutes
                start_times = [datetime.strptime(time[:5], "%H:%M") for time in times]
                end_times = [datetime.strptime(time[-5:], "%H:%M")+timedelta(minutes=15) for time in times]
                for k in range(n):
                    s = ([x > start_times[k] for x in end_times])
                    e = ([x < end_times[k] for x in start_times])
                    if sum([x*y for x,y in zip(s,e)]) > 1:
                        for row in df.index.tolist():
                            if df.loc[row, 'Final_Time'] == times[k]:
                                indexFilter.append(row)
    return indexFilter

def room_overlap(enrl):
    indexFilter = []
    rooms = enrl['Final_Loc'].unique()
    for room in rooms:
        # filter by location
        _df = enrl[enrl['Final_Loc'] == room]
        days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
        for day in days:
            # filter by day
            df = _df[_df['Final_Day'] == day]

            # check for room overlap of same time blocks (this does not calculate all overlaps)
            if df.shape[0] > 1 and (df['Time'].nunique() != df['Final_Time'].nunique()):
                for row in df.index.tolist():
                    indexFilter.append(row)

    return indexFilter

def room_nonconformal_overlap(enrl):
    indexFilter = []
    rooms = enrl['Final_Loc'].unique()
    for room in rooms:
        # filter by location
        _df = enrl[enrl['Final_Loc'] == room]
        days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
        for day in days:
            # filter by day
            df = _df[_df['Final_Day'] == day]

            # check nonconformal overlaps; this uses SUMPRODUCT
            times = df['Final_Time'].unique().tolist()
            n = len(times)
            if n > 1:
                start_times = [datetime.strptime(time[:5], "%H:%M") for time in times]
                end_times = [datetime.strptime(time[-5:], "%H:%M") for time in times]
                for k in range(n):
                    s = ([x > start_times[k] for x in end_times])
                    e = ([x < end_times[k] for x in start_times])
                    if sum([x*y for x,y in zip(s,e)]) > 1:
                        for row in df.index.tolist():
                            if df.loc[row, 'Final_Time'] == times[k]:
                                indexFilter.append(row)

    return indexFilter

def room_back_to_back(enrl):
    indexFilter = []
    rooms = enrl['Final_Loc'].unique()
    for room in rooms:
        # filter by location
        _df = enrl[enrl['Final_Loc'] == room]
        days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
        for day in days:
            # filter by day
            df = _df[_df['Final_Day'] == day]

            # check nonconformal overlaps; this uses SUMPRODUCT
            times = df['Final_Time'].unique().tolist()
            n = len(times)
            if n > 1:
                start_times = [datetime.strptime(time[:5], "%H:%M") for time in times]
                end_times = [datetime.strptime(time[-5:], "%H:%M") for time in times]
                # check for back-to-back in same room
                for k in range(n):
                    s = ([x == start_times[k] for x in end_times[:-1]])
                    e = ([x == end_times[k] for x in start_times[1:]])
                    if sum(s+e) > 0:
                        for row in df.index.tolist():
                            if df.loc[row, 'Final_Time'] == times[k]:
                                indexFilter.append(row)

    return indexFilter

def accord_with_finals_grid(df_enrl, df_finals, df_grid):
    indexFilter = []
    for row in df_enrl.index.tolist():
        CRN = df_enrl.loc[row, 'CRN']

        # convert everything to string to compare to datatable
        credit = str(int(df_enrl.loc[row, 'Credit']))
        start_time = df_enrl.loc[row, 'Time'][:5]
        days = df_enrl.loc[row, 'Days']
        meetings = str(len(days) - days.count(" ")) # do not count spaces

        df = df_grid[(df_grid['Credit']==credit) & (df_grid['Class_Start']==start_time) & (df_grid['Meetings']==meetings) & (df_grid['Class_Days']==days)]
        try:
            final_day = df_finals[df_finals['CRN']==CRN]['Days'].iloc[0]
            final_time = df_finals[df_finals['CRN']==CRN]['Time'].iloc[0]
            grid_day = df['Final_Day'].iloc[0]
            grid_time = df['Final_Time'].iloc[0]
            if (grid_day != final_day) or (grid_time != final_time):
                if (df_enrl.loc[row, 'Number'] in ['1109', '1110', '1111']) and (final_day == "S"):
                    pass
                else:
                    indexFilter.append(row)
        except IndexError:
            pass # could not find day/time in finals grid

    return indexFilter

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
                dcc.Tab(
                    label='Rooms',
                    value='tab-rooms',
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
                    label='Finals Grid',
                    value='tab-grid',
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
                    label='Week View',
                    value='tab-week',
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
                # place holder
            ],
                id='datatable-combined-div',
                style = {
                    'background': 'white',
                    'display': 'block',
                    'width': '100%',
                }
            ),
            html.Div([
                # place holder
            ],
                id='datatable-enrollment-div',
                style = {
                    'background': 'white',
                    'display': 'none',
                    'width': '100%',
                }
            ),
            html.Div([
                # place holder
                html.Ol([
                    html.Li(['Navigate to ',html.A("AHEC Master Calendar", href='https://ems.ahec.edu/mastercalendar/MasterCalendar.aspx', target="_blank")]),
                    html.Li('Unmark all calendars except MSU Finals'),
                    html.Li('Click on "GO" for the "Search for Events" text box'),
                    html.Li('Change the dates to include the Saturday before finals week through the Saturday of finals week.'),
                    html.Li('Select the checkbox for "Use Selected Filters"'),
                    html.Li('Click on "GO" for the "Search for Events" text box'),
                    html.Li('Click on "Export"'),
                ]),
            ],
                id='datatable-finals-div',
                style = {
                    'background': 'white',
                    'display': 'none',
                    'width': '100%',
                }
            ),
            html.Div([
                # place holder
            ],
                id='datatable-rooms-div',
                style = {
                    'background': 'white',
                    'display': 'none',
                    'width': '100%',
                }
            ),
            html.Div([
                dash_table.DataTable(
                    id='datatable-grid',
                    columns=[{'name': n, 'id': i} for n,i in zip([
                        '# of Credits', 'Meetings/Week', 'Class Days',
                        'Class Start', 'Class End', 'Final Day', 'Final Time'
                    ],[ *df_grid.columns ])],
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold',
                    },
                    style_cell={'font-family': 'sans-serif', 'font-size': '1rem'},
                    fixed_rows={'headers': True, 'data': 0},
                    page_size=500,
                    data=df_grid.to_dict('records'),
                    filter_action='native',
                    filter_options={'case': 'insensitive'},
                    sort_action='native',
                    sort_mode='multi',
                    selected_rows=[],
                    style_cell_conditional=[
                        {
                            'if': {'column_id': i},
                            'textAlign': 'center',
                            'minWidth': w, 'width': w, 'maxWidth': w,
                            'whiteSpace': 'normal'
                        }
                        for i,w in zip([*df_grid.columns],
                                       ['14%' for _ in range(7)])
                    ],
                    style_data={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                    },
                )
            ],
                id='datatable-grid-div',
                style = {
                    'background': 'white',
                    'display': 'none',
                    'width': '100%',
                }
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Tabs([generate_weekday_tab(day) for day in days ],
                                    id='weekdays-tabs',
                                    value='tab-mon')
                        ],
                        style={
                            'padding': '10px',
                            'background': 'white',
                        }
                    ),
                    html.Div(
                        [
                            html.Div([
                                generate_tab_fig(day, 'tab-mon', None) for day in days
                            ],
                                id='weekdays-tabs-content',
                                style={
                                    'background': 'white'
                                },
                            ),
                        ]
                    ),
                ],
                style = {
                    'display': 'none',
                },
                id='week-view-div'
            ),
        ],
            id='tab-contents',
            style = {
                'width': '100%',
            },
        ),
    ],
        id='leftContainer',
        style={
            'background': 'white',
            'float': 'left',
            'width': '78%',
            'height': '900px',
            'padding': '5px',
            'border': '1px solid rgba(0, 0, 0, 0.2)',
            'borderRadius': '5px',
            'backgroundColor': '#f9f9f9',
        },
    ),
    html.Div([
        html.Div([
            html.Label('Load:'),
            dcc.Upload(
                id='upload-enrollment',
                children= html.Button(
                    'Enrollment Report',
                    id='load-enrollmentreport-button',
                    n_clicks=0,
                    disabled=False,
                    style={
                        'padding': '0px',
                        'textAlign': 'center',
                        'width': '95%',
                        'fontSize': '1rem',
                    },
                    title='Enrollment report downloaded from Banner (SWRCGSR)',
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
                    disabled=True,
                    style={
                        'padding': '0px',
                        'textAlign': 'center',
                        'width': '95%',
                        'fontSize': '1rem',
                    },
                    title='Export of finals schedule from AHEC master calendar',
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
                style={
                    'padding': '0px',
                    'textAlign': 'center',
                    'width': '95%',
                    'fontSize': '1rem',
                },
                className='button'
            ),
            html.Button(
                'Export for Access',
                id='download-to-access-button',
                n_clicks=0,
                disabled=True,
                style={
                    'padding': '0px',
                    'textAlign': 'center',
                    'width': '95%',
                    'fontSize': '1rem',
                },
                className='button'
            ),
            dcc.Download(id='datatable-to-access-download'),
            html.Button(
                'Export to Excel',
                id='export-all-button',
                n_clicks=0,
                disabled=True,
                style={
                    # 'marginLeft': '5px'
                    'padding': '0px',
                    'textAlign': 'center',
                    'width': '95%',
                    'fontSize': '1rem',
                },
                className='button'
            ),
            dcc.Download(id='datatable-download'),
        ],
            id='buttonContainer',
        ),
    ],
        id='rightContainer',
        style={
            'width': '18%',
            'marginLeft': '1rem',
            'float': 'left',
            'border': '1px solid rgba(0, 0, 0, 0.2)',
            'borderRadius': '5px',
            'backgroundColor': '#f9f9f9',
            'padding': '5px',
        },
    ),
],
    id='mainContainer',
)

@app.callback(
     Output('table-tabs', 'value'),
    [Input('load-enrollmentreport-button', 'n_clicks'),
     Input('load-finalsexport-button', 'n_clicks'),
     Input('update-button', 'n_clicks'),]
)
def display_tab(btn_enroll, btn_finals, btn_update):
    # this function changes the view of the tab content based on
    # which button was clicked
    if DEBUG:
        print("function: update_tab_display")
    ctx = callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if btn_id == 'load-enrollmentreport-button':
            return 'tab-enrollment'
        elif btn_id == 'load-finalsexport-button':
            return 'tab-finals'
        else:
            return 'tab-combined'
    return

@app.callback(
    [Output('datatable-combined-div', 'style'),
     Output('datatable-enrollment-div', 'style'),
     Output('datatable-finals-div', 'style'),
     Output('datatable-rooms-div', 'style'),
     Output('datatable-grid-div', 'style'),
     Output('week-view-div', 'style'),],
    [Input('table-tabs', 'value')],
)
def update_tab_display(tab):
    if DEBUG:
        print("function: update_tab_display")
    ctx = callback_context
    if 'table-tabs' in ctx.triggered[0]['prop_id']:
        styles = []
        for t in ['tab-combined', 'tab-enrollment', 'tab-finals', 'tab-rooms', 'tab-grid', 'tab-week']:
            if t == tab:
                styles.append({'display': 'block'})
            else:
                styles.append({'display': 'none'})
        return styles[:]


@app.callback(
    [Output('datatable-enrollment-div', 'children'),
     Output('datatable-rooms-div', 'children'),
     Output('load-finalsexport-button', 'disabled'),
     Output('load-enrollmentreport-button', 'n_clicks')],
    [Input('upload-enrollment', 'contents'),
     State('upload-enrollment', 'filename'),
     State('load-enrollmentreport-button', 'n_clicks')]
)
def load_enrollment_data(contents, name, n_clicks):
    if DEBUG:
        print('function: load_enrollment')
    if contents is not None and n_clicks > 0:
        df_enrollment = parse_enrollment(contents, name)

        rooms = df_enrollment[(df_enrollment['S']=='A') & (df_enrollment['Time']!='TBA') & (df_enrollment['Campus']=='M')]['Loc'].unique()
        capacities = []
        for room in rooms:
            # capcaity is the max but this may not be the actual room capacity per Banner
            capacities.append(
                df_enrollment[(df_enrollment['Loc']==room)]['Max'].max(),
            )

        df_rooms = DataFrame({'Room': rooms, 'Cap': capacities})

        df_enrollment.drop(['Max'], axis=1, inplace=True)

        enrollment_children = [
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
                                   ['5%', '5.5%', '5.5%', '4.5%', '3.5%', '5.0%', '19.5%',
                                    '6.0%', '4.5%', '5.5%', '8.5%', '7.0%', '9%', '11%'])
                ],
                fixed_rows={'headers': True, 'data': 0},
                page_size=500,
                data=df_enrollment.to_dict('records'),
                filter_action='native',
                filter_options={'case': 'insensitive'},
                sort_action='native',
                sort_mode='multi',
                selected_rows=[],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
            )
        ]


        rooms_children = [
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
                row_deletable=True,
                filter_action='native',
                filter_options={'case': 'insensitive'},
                sort_action='native',
                sort_mode='multi',
            ),
            html.Br(),
            html.Button('Add Row', id='addrow-rooms-button', className='button', n_clicks=0),
            html.Div([
                html.P("Room capacities are taken from 'Max' and may not reflect what is the actual capacity.  Please verify in Banner."),
            ]),
        ]

    else:
        enrollment_children = []
        rooms_children = []
    return enrollment_children, rooms_children, False, 0

@app.callback(
    [Output('datatable-finals-div', 'children'),
     Output('load-finalsexport-button', 'n_clicks')],
    [Input('upload-finals', 'contents'),
     State('upload-finals', 'filename'),
     State('load-finalsexport-button', 'n_clicks'),
     State('datatable-enrollment', 'data')]
)
def load_finals_data(contents, filename, n_clicks, data_enrollment):
    if DEBUG:
        print('function: load_finals')
    if contents is not None and n_clicks > 0:

        # retrieve enrollment table
        df_enrollment = DataFrame(data_enrollment)

        # obtain list of CRNs from enrollment report
        CRNs = df_enrollment['CRN'].unique()

        try:
            if 'csv' in filename:
                df_finals = parse_finals_csv(contents, CRNs)
            elif 'xlsx' in filename:
                df_finals = parse_finals_xlsx(contents, CRNs)
        except Exception as e:
            print(e)
            return html.Div(['There was an error processing this file.'])

        data_children = [
            dash_table.DataTable(
                id='datatable-finals',
                columns=[{'name': n, 'id': i} for n,i in zip([
                    'CRN', 'Class', 'Day', 'Time', 'Loc', 'Date'
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
                    for i,w in zip([ *df_finals.columns ], ['15%', '15%'  '10%',  '20%',  '20%',  '20%'])
                ],
                fixed_rows={'headers': True, 'data': 0},
                page_size=500,
                data=df_finals.to_dict('records'),
                editable=True,
                filter_action='native',
                filter_options={'case': 'insensitive'},
                sort_action='native',
                sort_mode='multi',
                row_deletable=True,
                selected_rows=[],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                page_action='none',
                style_table={'height': '1600px', 'overflowY': 'auto'},
            ),
            html.Br(),
            html.Button('Add Row', id='addrow-finals-button', className='button', n_clicks=0),
        ]

    else:
        data_children = [ ]
    return data_children, 0

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
    [Output('download-to-access-button', 'disabled'),
     Output('export-all-button', 'disabled')],
    Input('update-button', 'n_clicks'),
)
def enable_update_button(n_clicks):
    if DEBUG:
        print('function: enable_disable_button')
    if n_clicks > 0:
        return False, False
    return True, True

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
    Input('addrow-rooms-button', 'n_clicks'),
    State('datatable-rooms', 'data'),
    State('datatable-rooms', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output('datatable-download', 'data'),
    [Input('export-all-button', 'n_clicks'),
     State('datatable-combined', 'data')]
)
def export_all(n_clicks, data):
    if DEBUG:
        print("function: export_all")
    _df = DataFrame(data)
    if n_clicks > 0:
        return {'base64': True, 'content': to_excel(_df), 'filename': 'FinalsSchedule.xlsx', }

@app.callback(
    Output('datatable-to-access-download', 'data'),
    [Input('download-to-access-button', 'n_clicks'),
     State('datatable-combined', 'data')]
)
def export_all(n_clicks, data):
    # download as MS Excel for import in MS Access Database
    if DEBUG:
        print("function: download")
    if n_clicks > 0:

        # retrieve the datatable
        _df = DataFrame(data)

        # create columns for export
        col_dept = []
        col_endtime = []
        for row in _df.index.tolist():
            col_dept.append(
                str(_df.loc[row, 'Subject']) + '-' +
                str(_df.loc[row, 'Number']) + '-' +
                str(_df.loc[row, 'Section']) + ' ' +
                str(_df.loc[row, 'CRN']) + ' ' +
                str(_df.loc[row, 'Title'])
            )
            col_endtime.append(str(_df.loc[row, 'Final_Time'][-5:]))

        # create dictionary of all columns
        d = {
            'DEPT/CID CALL and Title': col_dept,
            'CRN': _df['CRN'],
            'Day': _df['Final_Day'],
            'Final Exam Time': _df['Final_Time'],
            'EndTime': col_endtime,
            'Final Exam Date': _df['Final_Date'],
            'Final Exam Rm': _df['Final_Loc'],
            'ContactName': _df['Instructor'],
            'Error': _df['Error']
        }
        df = DataFrame(d)

        xlsx_io = BytesIO()
        writer = ExcelWriter(
            xlsx_io, engine='xlsxwriter', options={'strings_to_numbers': False}
        )
        df.to_excel(writer, sheet_name='Final Exam Schedule', index=False)

        # Save it
        writer.save()
        xlsx_io.seek(0)
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        data = b64encode(xlsx_io.read()).decode('utf-8')

        return {'base64': True, 'content': data, 'filename': 'Final Exam Schedule.xlsx', }

@app.callback(
    [Output('datatable-combined-div', 'children'),
     Output('weekdays-tabs-content', 'children'),],
    [Input('update-button', 'n_clicks'),
     State('weekdays-tabs', 'value'),
     State('datatable-enrollment', 'data'),
     State('datatable-finals', 'data'),
     State('datatable-rooms', 'data')]
)
def create_combined_table(n_clicks, tab, data_enrollment, data_finals, data_rooms):

    # retrieve enrollment table
    df_enrollment = DataFrame(data_enrollment)

    # retrieve finals table
    df_finals = DataFrame(data_finals)

    # recalculate the day of the final based on the date of the final
    for row in df_finals.index.tolist():
        Date = df_finals.loc[row, 'Date']
        # find the day of week and code it to MTWRFSU
        day_str = datetime.strptime(Date, '%m/%d/%Y').strftime('%A')
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
        df_finals.loc[row, 'Days'] = Days

    # retrieve rooms table
    df_rooms = DataFrame(data_rooms)

    # create dictionary of capacities
    room_capacities = {
        df_rooms.loc[row, 'Room']: int(df_rooms.loc[row, 'Cap']) for row in df_rooms.index.tolist()
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
    df_enrollment['Error'] = ['' for _ in range(len(df_enrollment))]

    # check to see if every course has a final
    _indexFilter = no_final(df_enrollment, df_finals)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '0'

    # check to see if there are multiple finals for a given CRN
    _indexFilter = multiple_finals(df_enrollment[~df_enrollment['Error'].str.contains('0')], df_finals)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '1'

    # fill in finals data
    _indexFilter = df_enrollment[~df_enrollment['Error'].str.contains('0|1')].index.tolist()
    for row in _indexFilter:
        CRN = df_enrollment.loc[row, 'CRN']

        day = df_finals[df_finals['CRN'] == CRN]['Days'].iloc[0]
        date = df_finals[df_finals['CRN'] == CRN]['Date'].iloc[0]
        time = df_finals[df_finals['CRN'] == CRN]['Time'].iloc[0]
        room = df_finals[df_finals['CRN'] == CRN]['Loc'].iloc[0]

        df_enrollment.loc[row, 'Final_Day'] = day
        df_enrollment.loc[row, 'Final_Date'] = date
        df_enrollment.loc[row, 'Final_Time'] = time
        df_enrollment.loc[row, 'Final_Loc'] = room


    # filter out non-existent or multiple finals
    df = df_enrollment[~df_enrollment['Error'].str.contains('0|1')]

    # check to see if final is on one of the class days
    _indexFilter = correct_final_day(df, df_finals)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '2'

    # check for instructor overlap of full time block
    _indexFilter = instructor_overlap(df)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '3'

    # check for instructor overlap of nonconformal time block
    _indexFilter = instructor_nonconformal_overlap(df)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '4'

    # check for instructor back-to-back
    _indexFilter = instructor_back_to_back(df)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '5'

    # check for room overlap
    _indexFilter = room_overlap(df)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '6'

    # check for room overlap of nonconformal time block
    _indexFilter = room_nonconformal_overlap(df)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '7'

    # check for room back-to-back
    _indexFilter = room_back_to_back(df)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '8'

    # check that start time is within one hour of regular class start time
    _indexFilter = within_one_hour(df)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '9'

    # check to see if final room is in room table
    _indexFilter = room_exist(df, df_finals, df_rooms)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += 'A'

    # check final room capacity
    _indexFilter = final_room_capacity(df_enrollment[~df_enrollment['Error'].str.contains('0|1|A')], room_capacities)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += 'B'

    # check if day and time correspond to Finals Grid
    _indexFilter = accord_with_finals_grid(df, df_finals, df_grid)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += 'C'


    # need to check if the only error code is 6 but there may be enough capacity
    # in the room so remove the error
    _indexFilter = df_enrollment[df_enrollment['Error'] == '6'].index.tolist()
    df_tmp = df_enrollment[df_enrollment['Error'] == '6']
    rms = df_enrollment[df_enrollment['Error'] == '6']['Final_Loc'].unique()
    # rms = df_tmp['Final_Loc'].unique()
    for r in rms:
        cap_enrl = df_tmp[df_tmp['Final_Loc'] == r]['Enrolled'].sum()
        cap_rm = int(df_rooms[df_rooms['Room'] == r]['Cap'])
        if cap_enrl <= cap_rm:
            for row in _indexFilter:
                df_enrollment.loc[row, 'Error'] = ''


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
            filter_action='native',
            filter_options={'case': 'insensitive'},
            sort_action='native',
            sort_mode='multi',
            selected_rows=[],
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{Error} > " "',
                    },
                    'backgroundColor': '#FFDD33',
                },
            ],
        ),
        html.Hr(),
        html.P(),
        html.Label('The error codes are'),
        html.Ul([
            html.Li('0 : No final for this CRN'),
            html.Li('1 : Multiple finals for this CRN'),
            html.Li('2 : Day of final incorrect'),
            html.Li('3 : Overlap of time block for instructor'),
            html.Li('4 : Overlap between time blocks for instructor'),
            html.Li('5 : Instructor back-to-back within 15 minutes'),
            html.Li('6 : Overlap of time block in same room'),
            html.Li('7 : Overlap between time blocks in same room'),
            html.Li('8 : Back-to-back in same room'),
            html.Li('9 : Final start time not within one hour of regular start time'),
            html.Li('A : Room does not exist in Rooms Table'),
            html.Li('B : Room capacity may be too low (check in Banner)'),
            html.Li('C : Final day/time does not agree with Finals Grid'),
        ],
            style={'listStyleType': 'none', 'lineHeight': 1.25},
        ),
    ]

    figs = update_grid(df.to_dict())
    tabs_children = [ generate_tab_fig(day, tab, fig) for day, fig in zip(days, figs)]


    return data_children, tabs_children

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
    ctx = callback_context
    if 'weekdays-tabs' in ctx.triggered[0]['prop_id']:
        styles = []
        for t in ['tab-mon', 'tab-tue', 'tab-wed', 'tab-thu', 'tab-fri', 'tab-sat']:
            if t == tab:
                styles.append({'display': 'block'})
            else:
                styles.append({'display': 'none'})
        return styles[:]

# Main
if __name__ == '__main__':
    if mathserver:
        app.run_server(debug=DEBUG)
    else:
        app.run_server(debug=DEBUG, port='8053')
