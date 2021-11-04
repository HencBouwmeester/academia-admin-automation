# -*- coding: utf-8 -*-

# Import required libraries
import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import dash_table
import numpy as np
import base64
import io
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# Include pretty graph formatting
pio.templates.default = "plotly_white"

# Initialize server
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    prevent_initial_callbacks=True,
)
server = app.server

app.title = "Scheduling Tools"

app.config.update({
    'suppress_callback_exceptions': True,
})

# specifics for the math.msudenver.edu server
"""
app.config.update({
   'url_base_pathname':'/dash/',
   'routes_pathname_prefix':'/dash/',
   'requests_pathname_prefix':'/dash/',
})
"""

# Create app layout
app.layout = html.Div([
    dcc.Store(id="aggregate_data"),
    # empty Div to trigger javascript file for graph resizing
    html.Div(id="output-clientside"),
    html.Div([
        html.Div([
            html.Img(
                id="msudenver-logo",
                src=app.get_asset_url('msudenver-logo.png'),

            ),
        ],
            className="three offset-right columns",
        ),
        html.Div([
            html.Div([
                html.H3(
                    "Scheduling Tools",
                    id="title-report-semester",
                    style={"marginBottom": "0px"},
                ),
            ],
                id="main_title",
            )
        ],
            className="six offset-left offset-right columns",
            id="title",
        ),
        html.Div([
            dcc.Upload(
                id="upload-data",
                children=html.Div(
                    ["Drag and Drop or ", html.A("Select Files")]
                ),
                multiple=False,
                accept=".txt, .csv, .xlsx",
            ),
        ],
            className="three offset-left columns",
            id="button",
        ),
    ],
        id="header",
        className="row flex-display",
        style={"marginBottom": "25px"},
    ),
    html.Div(id="output-data-upload"),
],
id="mainContainer",
style={"display": "flex", "flexDirection": "column"},
)

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

    # read the data date from the file
    for i in range(5):
        line = file_contents.readline()
        if i == 4:
            d = line.split()[-1]
            break
    data_date = datetime.datetime.strptime(d, "%d-%b-%Y")

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
    # _df.drop(["T", "Enrolled", "WCap", "WList", "Rcap", "Full", "Class"], axis=1, inplace=True)

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

    term_code = "190000"
    d = "02-FEB-1900"
    data_date = datetime.datetime.strptime(d, "%d-%b-%Y")
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
                        })

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

    # _df.drop(["Class"], axis=1, inplace=True)

    # there might be CRNs that are unknown (blank), so fill sequentially starting
    # from 99999 and go down
    i = 1
    for row in _df[_df["CRN"].isna()].index.tolist():
        _df.loc[row, "CRN"] = str(100000 - i)
        i += 1

    return _df, term_code, data_date

def parse_contents(contents, filename, date):
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
            df, term_code, data_date = tidy_xlsx(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    tab_style = {
        'height': '30px',
        'padding': '2px',
    }
    selected_tab_style = {
        'height': '30px',
        'padding': '2px',
    }
    html_layout = [
        html.Div([
            dcc.Tabs(id='tabs-weekdays', value='tab-mon', children=[
                dcc.Tab(label='Monday',
                        value='tab-mon',
                        style=tab_style,
                        selected_style=selected_tab_style,
                       ),
                dcc.Tab(label='Tuesday',
                        value='tab-tue',
                        style=tab_style,
                        selected_style=selected_tab_style,
                       ),
                dcc.Tab(label='Wednesday',
                        value='tab-wed',
                        style=tab_style,
                        selected_style=selected_tab_style,
                       ),
                dcc.Tab(label='Thursday',
                        value='tab-thu',
                        style=tab_style,
                        selected_style=selected_tab_style,
                       ),
                dcc.Tab(label='Friday',
                        value='tab-fri',
                        style=tab_style,
                        selected_style=selected_tab_style,
                       ),
                dcc.Tab(label='Saturday',
                        value='tab-sat',
                        style=tab_style,
                        selected_style=selected_tab_style,
                       ),
            ]),
            html.Div(id='tabs-weekdays-content',
                     style={
                         'width': '100%',
                         'display': 'block',
                         'marginLeft': 'auto',
                         'marginRight': 'auto',
                     }
                    )
        ],
        ),
        html.Div([
            dash_table.DataTable(
                id='datatable-interactivity',
                export_format="xlsx",
                columns=[{'name': n, 'id': i} for n,i in zip([
                    "Subj", "Nmbr", "CRN", "Sec", "S", "Cam", "Title",
                    "Credit", "Max", "Days", "Time", "Loc", "Begin/End", "Instructor"
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
            )
            ],
            style={
                'width': '100%',
                'display': 'block',
                'marginLeft': 'auto',
                'marginRight': 'auto',
            }
            )
    ]
    return html_layout, df

@app.callback(
    [Output("output-data-upload", "children")],
    [Input("upload-data", "contents")],
    [State("upload-data", "filename"), State("upload-data", "last_modified")],
)
def update_output(contents, name, date):
    """When files are selected, call parse-contents and return the new html elements."""

    if contents is not None:
        data_children, df = parse_contents(contents, name, date)
    else:
        data_children = []
    return [data_children]

@app.callback(
    Output('tabs-weekdays-content', 'children'),
    [Input('tabs-weekdays', 'value'),
     Input('datatable-interactivity', 'data'),
     Input('datatable-interactivity', 'derived_viewport_data'),
     Input('datatable-interactivity', 'derived_virtual_selected_rows')],
)
def render_content(tab, data, filtered_data, slctd_row_indices):
    _dfLoc = pd.DataFrame(data)
    _df = pd.DataFrame(filtered_data)

    # set the color pallete
    colorDark = px.colors.qualitative.Set1
    colorLight = px.colors.qualitative.Pastel1

    # add columns for rectangle dimensions and annotation
    _df.insert(len(_df.columns), "xRec", 0)
    _df.insert(len(_df.columns), "yRec", 0)
    _df.insert(len(_df.columns), "wRec", 0)
    _df.insert(len(_df.columns), "hRec", 0)
    _df.insert(len(_df.columns), "textRec", 0)
    _df.insert(len(_df.columns), "colorRec", 0)

    colors = [colorLight[4] if k in slctd_row_indices else colorLight[1]
              for k in range(len(_df))]
    _df["colorRec"] = colors

    # remove classes without rooms
    _df = _df[_df["Campus"] != "I"]
    _df = _df[_df["Loc"] != "TBA"]
    _dfLoc = _dfLoc[_dfLoc["Campus"] != "I"]
    _dfLoc = _dfLoc[_dfLoc["Loc"] != "TBA"]

    # unique rooms and total number of unique rooms
    rooms = _dfLoc["Loc"].unique()
    Loc = dict(zip(sorted(rooms), range(len(rooms))))
    nLoc = len(list(Loc.keys()))

    # compute dimensions based on class time
    for row in _df.index.tolist():
        strTime = _df.loc[row, "Time"]
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
        _df.loc[row, "xRec"] = Loc[_df.loc[row, "Loc"]]
        _df.loc[row, "yRec"] = yRec
        _df.loc[row, "wRec"] = 1
        _df.loc[row, "hRec"] = hRec
        _df.loc[row, "textRec"] = _df.loc[row, "Class"] + "-" + _df.loc[row, "Section"]

    # create mask for each tab based on day of week
    if tab == 'tab-mon':
        mask = _df["Days"].str.contains('M', case=True, na=False)
    elif tab == 'tab-tue':
        mask = _df["Days"].str.contains('T', case=True, na=False)
    elif tab == 'tab-wed':
        mask = _df["Days"].str.contains('W', case=True, na=False)
    elif tab == 'tab-thu':
        mask = _df["Days"].str.contains('R', case=True, na=False)
    elif tab == 'tab-fri':
        mask = _df["Days"].str.contains('F', case=True, na=False)
    elif tab == 'tab-sat':
        mask = _df["Days"].str.contains('S', case=True, na=False)

    # apply mask to tab
    _df = _df[mask]

    fig = go.Figure()

    # alternating vertical shading for rooms
    for k in range(nLoc):
        if k%2:
            fig.add_shape(
                type="rect",
                xref="x", yref="y",
                x0 = k, y0 = 0,
                x1 = k+1, y1 = -170,
                line=dict(
                    color="white",
                    width=1,
                ),
                fillcolor=colorLight[8],
            )
        else:
            fig.add_shape(
                type="rect",
                xref="x", yref="y",
                x0 = k, y0 = 0,
                x1 = k+1, y1 = -170,
                line=dict(
                    color="white",
                    width=1,
                ),
                fillcolor="white",
            )

    # horizontal lines for hours
    for k in range(170):
        if not k%12:
            fig.add_shape(
                type="line",
                xref="x", yref="y",
                x0 = 0, y0 = -k,
                x1 = nLoc, y1 = -k,
                line=dict(
                    color="LightGray",
                    dash="dot",
                    width=1,
                ),
            )


    # create list of dictionaries of rectangle for each course this will allow
    # me to find overlaps later
    recAnnotations = []
    recDimensions = []
    for row in _df.index.tolist():
        xRec = _df.loc[row, "xRec"]
        yRec = _df.loc[row, "yRec"]
        wRec = _df.loc[row, "wRec"]
        hRec = _df.loc[row, "hRec"]
        textRec = _df.loc[row, "textRec"]
        colorRec = _df.loc[row, "colorRec"]

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
        autosize = False,
        width = 1283,
        height = 600,
        xaxis = dict(
            range=[0,nLoc],
            tickvals=[k+.5 for k in range(nLoc)],
            ticktext=list(Loc.keys()),
        ),
        yaxis = dict(
            range=[-170, 0],
            tickvals=[-k*12 for k in range(15)],
            ticktext=[("0{:d}:00".format(k))[-5:] for k in range(8,23)],
        )
    )

    return html.Div([
        dcc.Graph(
            figure=fig,
            config={
                'displayModeBar': False,
                'staticPlot': True,
            },
        )
    ])

# Main
if __name__ == "__main__":
    app.run_server(debug=True, host='10.0.2.15')
    # app.run_server(debug=True)


"""
TODO:
    add functionality to add rows

"""
