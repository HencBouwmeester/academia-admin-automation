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

# Include pretty graph formatting
pio.templates.default = "plotly_white"

# Initialize server
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    prevent_initial_callbacks=True,
)
server = app.server

app.title = "Scheduling Tool"

app.config.update({
    'suppress_callback_exceptions': True,
})

# specifics for the math.msudenver.edu server
"""
app.config.update({
   'url_base_pathname':'/scheduling/',
   'routes_pathname_prefix':'/scheduling/',
   'requests_pathname_prefix':'/scheduling/',
})
"""

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

def updateTitles(df):
    course_titles = [
        ["MTH 1051", "Principles of Math in Chem Lab",],
        ["MTH 1080", "Mathematics for Liberal Arts",],
        ["MTH 1081", "Math. for Lib. Arts with Lab",],
        ["MTH 1082", "Math. for Liberal Arts Lab",],
        ["MTH 1101", "College Algebra for Calc Lab",],
        ["MTH 1108", "College Algebra Stretch Part I",],
        ["MTH 1109", "College Alg. Stretch Part II",],
        ["MTH 1110", "College Algebra for Calculus",],
        ["MTH 1111", "College Alg. for Calc with Lab",],
        ["MTH 1112", "College Algebra thru Modeling",],
        ["MTH 1115", "College Alg thru Mdlng w Lab",],
        ["MTH 1116", "College Alg thru Mdlng Lab",],
        ["MTH 1120", "College Trigonometry",],
        ["MTH 1210", "Introduction to Statistics",],
        ["MTH 1310", "Finite Math - Mgmt & Soc Scncs",],
        ["MTH 1311", "Finite Math-Mgmt -with Lab",],
        ["MTH 1312", "Finite Mathematics Lab",],
        ["MTH 1320", "Calculus - Mgmt & Soc Sciences",],
        ["MTH 1400", "Precalculus Mathematics",],
        ["MTH 1410", "Calculus I",],
        ["MTH 1610", "Integrated Mathematics I",],
        ["MTH 2140", "Computational Matrix Algebra",],
        ["MTH 2410", "Calculus II",],
        ["MTH 2420", "Calculus III",],
        ["MTH 2520", "R Programming",],
        ["MTH 2540", "Scientific Computing",],
        ["MTH 2620", "Integrated Mathematics II",],
        ["MTH 3100", "Intro to Mathematical Proofs",],
        ["MTH 3110", "Abstract Algebra I",],
        ["MTH 3130", "Advd Matrix Mthds Phy Sciences",],
        ["MTH 3140", "Linear Algebra",],
        ["MTH 3170", "Discrete Math for Comp Science",],
        ["MTH 3210", "Probability and Statistics",],
        ["MTH 3220", "Statistical Methods",],
        ["MTH 3240", "Environmental Statistics",],
        ["MTH 3270", "Data Science",],
        ["MTH 3400", "Chaos & Nonlinear Dynamics",],
        ["MTH 3420", "Differential Equations",],
        ["MTH 3430", "Mathematical Modeling",],
        ["MTH 3440", "Partial Differential Equations",],
        ["MTH 3470", "Intro Discrete Math & Modeling",],
        ["MTH 3510", "SAS Programming",],
        ["MTH 3650", "Foundations of Geometry",],
        ["MTH 4110", "Abstract Algebra II",],
        ["MTH 4150", "Elementary Number Theory",],
        ["MTH 4210", "Probability Theory",],
        ["MTH 4230", "Regression/Computational Stats",],
        ["MTH 4250", "Statistical Theory",],
        ["MTH 4290", "Senior Statistics Project",],
        ["MTH 4410", "Real Analysis I",],
        ["MTH 4480", "Numerical Analysis I",],
        ["MTH 4490", "Numerical Analysis II",],
        ["MTH 4640", "History of Mathematics",],
        ["MTH 4660", "Introduction to Topology",],
        ["MTL 3600", "Mathematics of Elementary Curriculum",],
        ["MTL 3620", "Mathematics of Secondary Curriculum",],
        ["MTL 3630", "Teaching Secondary Mathematics",],
        ["MTL 3638", "Secondry Mathematics Field Experience",],
        ["MTL 3750", "Number & Alg in the K-8 Curriculum",],
        ["MTL 3760", "Geom & Stats in the K-8 Curriculum",],
        ["MTL 3850", "STEM Teaching and Learning",],
        ["MTL 3858", "STEM Practicum",],
        ["MTL 4690", "Student Teaching & Seminar: Secondary 7-12",],
        ["MTLM 5020", "Integrated Mathematics II",],
        ["MTLM 5600", "Mathematics of the Elementary Curriculum",],
    ]

    df_titles = pd.DataFrame(course_titles, columns=["Class", "Title"])

    cols = df.columns
    df = df.set_index("Class")
    df.update(df_titles.set_index("Class"))
    df.reset_index(inplace=True)
    df = df[cols]


    return df

def convertAMPMtime(timeslot):
    """Convert time format from 12hr to 24hr and account for TBA times.

    Args:
        timeslot: dataframe cell contents.

    Returns:
        reformmated dataframe cell contents."""

    try:
        starthour = int(timeslot[0:2])
        endhour = int(timeslot[5:7])
        if timeslot[-2:] == "PM":
            endhour = endhour + 12 if endhour < 12 else endhour
            starthour = starthour + 12 if starthour + 12 <= endhour else starthour
        timeslot = "{:s}:{:s}-{:s}:{:s}".format(
            str(starthour).zfill(2), timeslot[2:4], str(endhour).zfill(2), timeslot[7:9]
        )
    except ValueError:  # catch the TBA times
        pass

    return timeslot

def tidy_txt(file_contents):
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
    file_contents.seek(0)

    _df = pd.read_fwf(file_contents, colspecs=_LINE_PATTERN)

    # read the report Term and Year from file
    term_code = str(_df.iloc[5][1])[3:] + str(_df.iloc[5][2])[:-2]

    _df.columns = _df.iloc[7]

    # manual filtering of erroneous data which preserves data for MTH 1108/1109
    _df = _df.dropna(how='all')
    _df = _df[~_df["Subj"].str.contains("Subj", na=False)]
    _df = _df[~_df["Subj"].str.contains("---", na=False)]
    _df = _df[~_df["Subj"].str.contains("SWRC", na=False)]
    _df = _df[~_df["Subj"].str.contains("Ter", na=False)]
    _df = _df[~_df["Instructor"].str.contains("Page", na=False)]
    _df = _df.drop(_df.index[_df["Loc"].str.startswith("BA", na=False)].tolist())
    _df = _df[_df["Begin/End"].notna()]

    # reset index and remove old index column
    _df = _df.reset_index()
    _df = _df.drop([_df.columns[0]], axis=1)

    # correct report to also include missing data for MTH 1109
    for row in _df[_df["Subj"].str.contains("MTH") & _df["Nmbr"].str.contains("1109") & _df["S"].str.contains("A")].index.tolist():
        for col in ["Subj", "Nmbr", "CRN", "Sec", "S", "Cam", "T", "Title", "Max", "Enrl", "WCap", "WLst", "Instructor"]:
            _df.loc[row + 1, col] = _df.loc[row, col]
        _df.loc[row + 1, "Credit"] = 0

    # correct report to also include missing data for MTH 1108
    for row in _df[_df["Subj"].str.contains("MTH") & _df["Nmbr"].str.contains("1108") & _df["S"].str.contains("A")].index.tolist():
        for col in ["Subj", "Nmbr", "CRN", "Sec", "S", "Cam", "T", "Title", "Max", "Enrl", "WCap", "WLst", "Instructor"]:
            _df.loc[row + 1, col] = _df.loc[row, col]
        _df.loc[row + 1, "Credit"] = 0
        row_dict = _df.loc[row].to_dict()
        row_dict["Instructor"] = ","
        row_dict["Credit"] = 0
        _df = _df.append(row_dict, ignore_index=True)

    # update all titles to show full name
    _df.insert(len(_df.columns), "Class", " ")
    _df["Class"] = _df["Subj"] + " " + _df["Nmbr"]
    _df = updateTitles(_df)

    # remove all rows with irrelevant data
    _df = _df[_df["CRN"].notna()]
    _df = _df[_df.CRN.apply(lambda x: x.isnumeric())]
    _df.rename(
        columns={
            "Subj": "Subject",
            "Nmbr": "Number",
            "Sec": "Section",
            "Cam": "Campus",
            "Enrl": "Enrolled",
            "WLst": "WList",
            "%Ful": "Full",
        },
        inplace=True,
    )
    _df[["Credit", "Max", "Enrolled", "WCap", "WList"]] = _df[
        ["Credit", "Max", "Enrolled", "WCap", "WList"]
    ].apply(pd.to_numeric, errors="coerce")

    _df = _df.sort_values(by=["Subject", "Number", "Section"])
    _df.drop(["T", "Enrolled", "WCap", "WList", "Rcap", "Full"], axis=1, inplace=True)

    return _df

def tidy_csv(file_contents):
    """ Converts the CSV format to the TXT format from Banner

    Args:
        file_contents:
            input decoded filestream of SWRCGSR output from an uploaded textfile.

    Returns:
        Dataframe.
    """

    _file = file_contents.read()
    _file = _file.replace("\r","")

    _list = []
    line = ""
    for char in _file:
        if char == '\n':
            line = line.replace('"','')
            _list.append(line[:-1])
            line = ""
        else:
            line += char

    return tidy_txt(io.StringIO("\n".join(_list)))

def tidy_xlsx(file_contents):
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
        _df.insert(len(_df.columns), "S", "A")
    if not 'Begin/End' in _df.columns:
        _df.insert(len(_df.columns), "Begin/End", "01/01-01/01")
    if not 'Max' in _df.columns:
        _df.insert(len(_df.columns), "Max", 1)
    if not 'Credit' in _df.columns:
        _df.insert(len(_df.columns), "Credit", 3)

    _df.rename(
        columns={
            "Subj": "Subject",
            "Nmbr": "Number",
            "Sec": "Section",
            "Cam": "Campus",
            "Enrl": "Enrolled",
            "WLst": "WList",
            "%Ful": "Full",
        },
        inplace=True,
    )

    _df = _df[["Subject", "Number", "CRN", "Section", "S", "Campus", "Title",
              "Credit", "Max", "Days", "Time", "Loc", "Begin/End", "Instructor"]]

    _df.insert(len(_df.columns), "Class", " ")
    _df["Class"] = _df["Subject"] + " " + _df["Number"]
    _df = updateTitles(_df)

    # there might be CRNs that are unknown (blank), so fill sequentially starting
    # from 99999 and go down
    i = 1
    for row in _df[_df["CRN"].isna()].index.tolist():
        _df.loc[row, "CRN"] = str(100000 - i)
        i += 1

    return _df

def generate_weekday_tab(day):
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

    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "txt" in filename:
            # Assume that the user uploaded a banner fixed width file with .txt extension
            df = tidy_txt(io.StringIO(decoded.decode("utf-8")))
            df["Time"] = df["Time"].apply(lambda x: convertAMPMtime(x))
        elif "csv" in filename:
            # Assume the user uploaded a banner Shift-F1 export quasi-csv file with .csv extension
            df = tidy_csv(io.StringIO(decoded.decode("utf-8")))
            df["Time"] = df["Time"].apply(lambda x: convertAMPMtime(x))
        elif "xlsx" in filename:
            df = tidy_xlsx(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return df

def update_grid(toggle, data, filtered_data, slctd_row_indices):
    _dfLoc = pd.DataFrame(data)
    _df = pd.DataFrame(filtered_data)

    # set the color pallete
    colorLight = ['#fbb4ae', '#b3cde3', '#ccebc5', '#decbe4', '#fed9a6',
                  '#ffffcc', '#e5d8bd', '#fddaec', '#f2f2f2']

    # add columns for rectangle dimensions and annotation
    if not 'xRec' in _df.columns:
        _df.insert(len(_df.columns), "xRec", 0)
    if not 'yRec' in _df.columns:
        _df.insert(len(_df.columns), "yRec", 0)
    if not 'wRec' in _df.columns:
        _df.insert(len(_df.columns), "wRec", 0)
    if not 'hRec' in _df.columns:
        _df.insert(len(_df.columns), "hRec", 0)
    if not 'textRec' in _df.columns:
        _df.insert(len(_df.columns), "textRec", 0)
    if not 'colorRec' in _df.columns:
        _df.insert(len(_df.columns), "colorRec", 0)

    colors = [colorLight[4] if k in slctd_row_indices else colorLight[1]
              for k in range(len(_df))]
    _df["colorRec"] = colors

    # remove classes without rooms
    _dfLoc = _dfLoc[_dfLoc["Campus"] != "I"]
    _dfLoc = _dfLoc[_dfLoc["Loc"] != "TBA"]
    _dfLoc = _dfLoc[_dfLoc["Loc"] != "OFFC  T"]
    _dfLoc = _dfLoc[_dfLoc["S"] != "C"]
    _df = _df[_df["Campus"] != "I"]
    _df = _df[_df["Loc"] != "TBA"]

    # remove canceled classes
    _df = _df[_df["Loc"] != "OFFC  T"]
    _df = _df[_df["S"] != "C"]

    # create figures for all tabs
    figs = []
    for d in ['M', 'T', 'W', 'R', 'F', 'S']:

        # create mask for particular tab
        mask = _df["Days"].str.contains(d, case=True, na=False)

        # apply the mask and use a copy of the dataframe
        df = _df[mask].copy()

        # unique rooms and total number of unique rooms
        if toggle:
            rooms = _dfLoc["Loc"].unique()
        else:
            rooms = df["Loc"].unique()
        Loc = dict(zip(sorted(rooms), range(len(rooms))))
        nLoc = len(list(Loc.keys()))

        # compute dimensions based on class time
        for row in df.index.tolist():
            strTime = df.loc[row, "Time"]
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
                df.loc[row, "xRec"] = Loc[df.loc[row, "Loc"]]
            except:
                df.loc[row, "xRec"] = 0

            df.loc[row, "yRec"] = yRec
            df.loc[row, "wRec"] = 1
            df.loc[row, "hRec"] = hRec
            try:
                df.loc[row, "textRec"] = df.loc[row, "Subject"] + " " + df.loc[row, "Number"] + "-" + df.loc[row, "Section"]
            except TypeError:
                df.loc[row, "textRec"] = ""

        fig = go.Figure()

        # alternating vertical shading for rooms
        for k in range(nLoc):
            if k%2:
                fig.add_vrect(
                    xref="x", yref="y",
                    x0 = k, x1 = k+1,
                    fillcolor=colorLight[8],
                    layer="below", line_width=0,
                )
            else:
                fig.add_vrect(
                    xref="x", yref="y",
                    x0 = k, x1 = k+1,
                    fillcolor="white",
                    layer="below", line_width=0,
                )

        # create list of dictionaries of rectangle for each course this will allow
        # me to find overlaps later
        recAnnotations = []
        recDimensions = []
        for row in df.index.tolist():
            xRec = df.loc[row, "xRec"]
            yRec = df.loc[row, "yRec"]
            wRec = df.loc[row, "wRec"]
            hRec = df.loc[row, "hRec"]
            textRec = df.loc[row, "textRec"]
            colorRec = df.loc[row, "colorRec"]

            recAnnotations.append(
                dict(
                    xref="x", yref="y",
                    x = xRec + wRec/2,
                    y = -(yRec + hRec/2),
                    text = textRec,
                    showarrow = False,
                    font = dict(size=min(int(16/nLoc*8),14)),
                )
            )

            recDimensions.append(
                dict(
                    type="rect",
                    xref="x", yref="y",
                    x0 = xRec, y0 = -yRec,
                    x1 = xRec + wRec, y1 = -(yRec + hRec),
                    line=dict(
                        color="LightGray",
                        width=1,
                    ),
                    fillcolor=colorRec,
                    opacity=0.5,
                )
            )

        # draw the rectangles and annotations
        for ann,rec in zip(recAnnotations, recDimensions):
            fig.add_annotation(
                ann
            )
            fig.add_shape(
                rec
            )

        # setup the axes and tick marks
        fig.update_layout(
            xaxis = dict(
                range=[0,nLoc],
                tickvals=[k+.5 for k in range(nLoc)],
                ticktext=list(Loc.keys()),
                side='top',
                showgrid=False,
                linecolor='#CCC',
                mirror=True,
            ),
            yaxis = dict(
                range=[-168, 0],
                tickvals=[-k*12 for k in range(15)],
                ticktext=[("0{:d}:00".format(k))[-5:] for k in range(8,23)],
                showgrid=True,
                gridwidth=1,
                gridcolor='#DDD',
                linecolor='#CCC',
                mirror=True,
            )
        )
        figs.append(fig)

    return figs

def to_excel(df):
    _df = df.copy()

    # only grab needed columns and correct ordering
    cols = ["Subject", "Number", "CRN", "Section", "S", "Campus", "Title",
            "Credit", "Max", "Days", "Time", "Loc", "Begin/End", "Instructor"]
    _df = _df[cols]

    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(
        xlsx_io, engine="xlsxwriter", options={"strings_to_numbers": False}
    )
    _df.to_excel(writer, sheet_name='Schedule', index=False)

    # Save it
    writer.save()
    xlsx_io.seek(0)
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")

    return data

def generate_tab_fig(day, tab, fig):

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

    if fig is None:
        fig = blankFigure

    modeBarButtonsToRemove = ['zoom2d', 'pan2d', 'lasso2d', 'zoomIn2d',
                              'zoomOut2d', 'autoScale2d', 'resetScale2d']

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
app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(
                id='msudenver-logo',
                src=app.get_asset_url('msudenver-logo.png'),
                alt='MSU Denver',
            )],
            className='three offset-right columns',
            id='logo-container',
        ),
        html.Div([
            html.Div([
                html.H3(
                    'Scheduling',
                    id='title-report-semester',
                    style={'marginBottom': '0px'},
                )],
                id='main_title',
            )],
            className='six offset-left offset-right columns',
            id='title',
        ),
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Upload file']),
                multiple=False,
                accept='.txt, .csv, .xlsx',
                style={'display': 'inline-block'},
            )],
            className='three offset-left columns',
            id='button',
        )],
        id='header',
        className='row flex-display',
        style={'marginBottom': '25px'},
    ),
    html.Div(id='output-data-upload',
             children = [
                 html.Div([
                     html.Div([
                         dcc.Tabs(id='weekdays-tabs',
                                  value='tab-mon',
                                  children=[ generate_weekday_tab(day) for day in days ]
                                 )
                     ]),
                     html.Div([
                         html.Div(
                             id='weekdays-tabs-content',
                             children = [generate_tab_fig(day, 'tab-mon', None) for day in days],
                             style={
                                 'width': '100%',
                                 'display': 'block',
                                 'marginLeft': 'auto',
                                 'marginRight': 'auto',
                             }
                         ),
                     html.Div([
                         html.Div([
                             html.Label("All rooms:",
                                        style={'display': 'none'},
                                        id='all-rooms-label'),
                         ],
                             style={'vertical-align': 'middle', 'width': '59%', 'display': 'inline-block'},
                         ),
                         html.Div([
                             daq.BooleanSwitch(
                                 id='toggle-rooms',
                                 on=True,
                                 disabled=True,
                                 color='#e6e6e6',
                                 style={'display': 'none'},
                             ),
                         ],
                             style={'vertical-align': 'middle', 'width': '39%', 'display': 'inline-block'},
                         ),
                     ],
                         style={'float': 'right','marginRight': '5px'}),
                     ]),
                 ]),
                html.Div([
                    html.Div([
                        html.Label([
                            "Predefined Queries:",
                            dcc.Dropdown(
                                id='filter-query-dropdown',
                                options=[
                                    {'label': 'Only Math Classes', 'value': '{Subject} contains M'},
                                    {'label': 'Active Classes', 'value': '{S} contains A'},
                                    {'label': 'Active Math Classes', 'value': '{Subject} contains M && {S} contains A'},
                                    {'label': 'Active MTL Classes', 'value': '({Subject} contains MTL || {Number} contains 1610 || {Number} contains 2620) && {S} contains A'},
                                    {'label': 'Active Math without MTL', 'value': '{Subject} > M && {Subject} < MTL && ({Number} <1610 || {Number} >1610) && ({Number} <2620 || {Number} >2620) && {S} contains A'},
                                    {'label': 'Active Math w/o Labs', 'value': '{Subject} contains M && {S} contains A && ({Number} < 1082 || {Number} > 1082) && ({Number} < 1101 || {Number} > 1101) && ({Number} < 1116 || {Number} > 1116) && ({Number} < 1312 || {Number} > 1312)'},
                                    {'label': 'Active Math Labs', 'value': '{Subject} contains M && {S} contains A && ({Number} = 1082 || {Number} = 1101 || {Number} = 1116 || {Number} = 1312)'},
                                    {'label': 'Active Math Labs with Parents', 'value': '{Subject} contains M && {S} contains A && ({Number} = 1081 || {Number} = 1111 || {Number} = 1115 || {Number} = 1311 || {Number} = 1082 || {Number} = 1101 || {Number} = 1116 || {Number} = 1312)'},
                                    {'label': 'Active Unassigned Math w/o Labs', 'value': '{Subject} contains M && {S} contains A && ({Number} < 1082 || {Number} > 1082) && ({Number} < 1101 || {Number} > 1101) && ({Number} < 1116 || {Number} > 1116) && ({Number} < 1312 || {Number} > 1312) && {Instructor} Is Blank'},
                                    {'label': 'Active Unassigned Math Labs', 'value': '{Subject} contains M && {S} contains A && ({Number} = 1082 || {Number} = 1101 || {Number} = 1116 || {Number} = 1312) && {Instructor} Is Blank'},
                                    {'label': 'Active Math Lower Division', 'value': '{Subject} contains M && {Number} < 3000 && {S} contains A'},
                                    {'label': 'Active Math Upper Division', 'value': '{Subject} contains M && {Number} >= 3000 && {S} contains A'},
                                    {'label': 'Active Math Lower Division (except MTL)', 'value': '{Subject} > M && {Subject} < MTL && ({Number} <1610 || {Number} >1610) && ({Number} <2620 || {Number} >2620) && {Number} <3000 && {S} contains A'},
                                    {'label': 'Active Math Upper Division (except MTL)', 'value': '({Subject} > M && {Subject} < MTL) && {Number} >=3000 && {S} contains A'},
                                    {'label': 'Active Asynchronous', 'value': '{Loc} contains O && {S} contains A'},
                                    {'label': 'Active Face-To-Face', 'value': '{Campus} contains M && {S} contains A'},
                                    {'label': 'Active Synchronous', 'value': '{Loc} contains SY && {S} contains A'},
                                    {'label': 'Active Math Asynchronous', 'value': '{Subject} contains M && {Loc} contains O && {S} contains A'},
                                    {'label': 'Active Math Face-To-Face', 'value': '{Subject} contains M && {Campus} contains M && {S} contains A'},
                                    {'label': 'Active Math Synchronous', 'value': '{Subject} contains M && {Loc} contains SY && {S} contains A'},
                                    {'label': 'Canceled CRNs', 'value': '{S} contains C'},
                                ],
                                placeholder='Select a query',
                                value='',
                            ),
                        ]),
                    ], style={'marginTop': '7px', 'marginLeft': '5px',}),

                    html.Br(),

                    html.Div([
                        html.Label([
                            "Custom Queries:",
                            dcc.RadioItems(
                                id='filter-query-read-write',
                                options=[
                                    {'label': 'Read filter_query', 'value': 'read'},
                                    {'label': 'Write to filter_query', 'value': 'write'}
                                ],
                                className="dcc_control",
                                value='read'
                            ),
                        ]),
                    ], style={'marginLeft': '5px',}),
                html.Div([
                    html.Div([
                        dcc.Input(
                            id='filter-query-input',
                            placeholder='Enter filter query',
                            className="dcc_control",
                            style={'width': '98.5%'},
                        ),
                    ],
                        id='filter-query-input-container',
                        style={'marginLeft': '5px', 'width': '100%', 'display': 'none'}
                    ),
                    html.Div(id='filter-query-output', style={'display': 'inline-block', 'marginLeft': '15px'}),
                ], style={'height': '35px', 'width': '100%'}),
                html.Hr(),
                html.Div([
                    html.Button('Update Grid', id='update-grid-button', n_clicks=0,
                                style={'marginLeft': '5px'},className='button'),
                    html.Button('Select All', id='select-all-button', n_clicks=0,
                                style={'marginLeft': '5px'},className='button'),
                    html.Button('Deselect All', id='deselect-all-button', n_clicks=0,
                                style={'marginLeft': '5px'},className='button'),
                    html.Button('Export All', id='export-all-button', n_clicks=0,
                                style={'marginLeft': '5px'},className='button'),
                    dcc.Download(id='datatable-download'),
                    html.Button('Export Filtered', id='export-filtered-button',n_clicks=0,
                                style={'marginLeft': '5px'},className='button'),
                    dcc.Download(id='datatable-filtered-download'),
                    html.Button('Add Row', id='add-row-button', n_clicks=0,
                                style={'marginLeft': '5px'}, className='button'),
                    html.Button('Delete Row(s)', id='delete-row-button', n_clicks=0,
                                style={'marginLeft': '5px'}, className='button'),
                ]),
                ]),
                dcc.Loading(id='loading-icon-upload', children=[
                html.Div([],
                         style={
                             'width': '100%',
                             'display': 'block',
                             'marginLeft': 'auto',
                             'marginRight': 'auto',
                         },
                         id='datatable-interactivity-container',
                        ),], type='circle', fullscreen=True, color='#064779'),
                ],
                style={'display': 'none'}
                )],
                id="mainContainer",
    style={"display": "flex", "flexDirection": "column"},
)

@app.callback(
    Output('output-data-upload', 'style'),
    Input('upload-data', 'contents')
)
def func(contents):
    if contents is not None:
        return {'display': 'block'}

@app.callback(
    [Output('loading-icon-upload', 'children'),
     Output('weekdays-tabs-content', 'children')],
    [Input('upload-data', 'contents'),
     State('weekdays-tabs', 'value'),
     State('upload-data', 'filename')],
)
def func(contents, tab, name):
    if contents is not None:
        df = parse_contents(contents, name)
        data_children = [ dash_table.DataTable(
            id='datatable-interactivity',
            columns=[{'name': n, 'id': i} for n,i in zip([
                "Subj", "Nmbr", "CRN", "Sec", "S", "Cam", "Title", "Credit",
                "Max", "Days", "Time", "Loc", "Begin/End", "Instructor"
            ],[ *df.columns ])],
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold",
            },
            style_cell={"font-family": "sans-serif", "font-size": "1rem"},
            style_cell_conditional=[
                {
                    'if': {'column_id': i},
                    'textAlign': 'left',
                    'minWidth': w, 'width': w, 'maxWidth': w,
                    'whiteSpace': 'normal'
                }
                for i,w in zip([ *df.columns ],
                               ['5%', '5.5%', '5.5%', '4.5%', '3.5%', '4.5%', '19.5%',
                                '5.5%', '4.5%', '5.5%', '9%', '7.5%', '9%', '11%'])
            ],
            fixed_rows={"headers": True, "data": 0},
            page_size=500,
            data=df.to_dict('records'),
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            row_deletable=True,
            selected_rows=[],
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
        )]
        figs = update_grid(True, df.to_dict(), df.to_dict(), [])
        tabs_children = [ generate_tab_fig(day, tab, fig) for day, fig in zip(days, figs)]

    else:
        data_children = []
        tabs_children = [ generate_tab_fig(day, tab, None) for day in days]

    loading_children = [
        html.Div(data_children,
                 style={
                     'width': '100%',
                     'display': 'block',
                     'marginLeft': 'auto',
                     'marginRight': 'auto',
                 },
                 id='datatable-interactivity-container',
                )]

    return loading_children, tabs_children

@app.callback(
    [Output("loading-icon-mon", "children"),
     Output("loading-icon-tue", "children"),
     Output("loading-icon-wed", "children"),
     Output("loading-icon-thu", "children"),
     Output("loading-icon-fri", "children"),
     Output("loading-icon-sat", "children"),
     Output('toggle-rooms', 'color'),
     Output('toggle-rooms', 'disabled'),
     Output('toggle-rooms', 'style'),
     Output('all-rooms-label', 'style'),
     Output('msudenver-logo', 'alt')],
    [Input('update-grid-button', 'n_clicks'),
     Input('toggle-rooms', 'on'),
     State('weekdays-tabs', 'value'),
     State('datatable-interactivity', 'data'),
     State('datatable-interactivity', 'derived_virtual_data'),
     State('datatable-interactivity', 'derived_virtual_selected_rows')],
)
def render_content(n_clicks, toggle, tab, data, filtered_data, slctd_row_indices):
    if n_clicks > 0:
        figs = update_grid(toggle, data, filtered_data, slctd_row_indices)

        modeBarButtonsToRemove = ['zoom2d', 'pan2d', 'lasso2d', 'zoomIn2d',
                                  'zoomOut2d', 'autoScale2d', 'resetScale2d']
        children = []
        for day,fig in zip(days, figs):
            day_abbrv = day.lower()[:3]
            child = dcc.Graph(
                figure=fig,
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': modeBarButtonsToRemove,
                    'showAxisDragHandles': True,
                    'toImageButtonOptions': {'filename': day_abbrv},
                },
                id='schedule_'+day_abbrv,
            )
            children.append(child)

        bool_switch_disabled = False
        bool_switch_style = {'display': 'inline-block'}
        all_rooms_label_style = {'display': 'inline-block'}
        return *children, '#064779', bool_switch_disabled, bool_switch_style, all_rooms_label_style, "MSU Denver"


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
    if 'weekdays-tabs' in ctx.triggered[0]['prop_id']:
        styles = []
        for t in ['tab-mon', 'tab-tue', 'tab-wed', 'tab-thu', 'tab-fri', 'tab-sat']:
            if t == tab:
                styles.append({'display': 'block'})
            else:
                styles.append({'display': 'none'})
        return styles[:]


@app.callback(
    Output('datatable-interactivity', 'selected_rows'),
    [Input('select-all-button', 'n_clicks'),
     Input('deselect-all-button', 'n_clicks')],
    State('datatable-interactivity', 'derived_virtual_indices'),
)
def select_deselect(selbtn, deselbtn, selected_rows):
    ctx = dash.callback_context
    if ctx.triggered:
        trigger = (ctx.triggered[0]['prop_id'].split('.')[0])
    if trigger == 'select-all-button':
        if selected_rows is None:
            return []
        else:
            return selected_rows
    else:
        return []

@app.callback(
    Output('datatable-interactivity', 'data'),
    Input('add-row-button', 'n_clicks'),
    State('datatable-interactivity', 'data'),
    State('datatable-interactivity', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append(
            {'Subject': '', 'Number':'', 'CRN': '', 'Section': '', 'S': 'A',
             'Campus': '', 'Title': '', 'Credit': '', 'Max': '', 'Days': '',
             'Time': '', 'Loc': 'TBA', 'Being/End': '', 'Instructor': ','}
        )
    return rows

@app.callback(
    [Output('filter-query-input-container', 'style'),
     Output('filter-query-output', 'style')],
    [Input('filter-query-read-write', 'value')]
)
def query_input_output(val):
    if val == 'read':
        input_style = {'display': 'none'}
        output_style = {'display': 'inline-block', 'marginLeft': '15px'}
    else:
        input_style = {'marginLeft': '5px', 'width': '100%', 'display': 'inline-block'}
        output_style = {'display': 'none'}
    return input_style, output_style

@app.callback(
    Output('datatable-interactivity', 'filter_query'),
    [Input('filter-query-input', 'value')]
)
def write_query(query):
    if query is None:
        return ''
    return query

@app.callback(
    Output('filter-query-output', 'children'),
    [Input('datatable-interactivity', 'filter_query')]
)
def read_query(query):
    if query is None or query=="":
        return "No filter query"
    return html.P('filter_query = "{}"'.format(query)),

@app.callback(
    Output('filter-query-input', 'value'),
    Input('filter-query-dropdown', 'value')
)
def read_query_dropdown(query):
    if query is not None:
        return query

@app.callback(
    Output('datatable-download', 'data'),
    [Input('export-all-button', 'n_clicks'),
     State('datatable-interactivity', 'data')]
)
def func(n_clicks, data):
    _df = pd.DataFrame(data)
    if n_clicks > 0:
        return {"base64": True, "content": to_excel(_df), "filename": "Schedule.xlsx", }

@app.callback(
    Output('datatable-filtered-download', 'data'),
    [Input('export-filtered-button', 'n_clicks'),
     State('datatable-interactivity', 'derived_virtual_data')]
)
def func(n_clicks, data):
    _df = pd.DataFrame(data)
    if n_clicks > 0:
        return {"base64": True, "content": to_excel(_df), "filename": "Schedule.xlsx", }

# Main
if __name__ == "__main__":
    app.run_server(debug=True, host='10.0.2.15', port='8050')
    # app.run_server(debug=True)
