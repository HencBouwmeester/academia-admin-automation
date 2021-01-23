# -*- coding: utf-8 -*-

# Import required libraries
import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
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
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

app.title = "Enrollment Report Statistics"

app.config.update({
    'suppress_callback_exceptions': True,
})

# specifics for the math.msudenver.edu server
# """
app.config.update({
   'url_base_pathname':'/dash/',
   'routes_pathname_prefix':'/dash/',
   'requests_pathname_prefix':'/dash/',
})
# """

df = pd.DataFrame()

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
            className="two columns",
        ),
        html.Div([
            html.Div([
                html.H3(
                    "SWRCGSR Enrollment",
                    id="title-report-semester",
                    style={"margin-bottom": "0px"},
                ),
                html.H5(
                    "Statistics and Graphs",
                    style={"margin-top": "0px"}
                ),
            ],
                id="main_title",
            )
        ],
            className="seven columns",
            id="title",
        ),
        html.Div([
            dcc.Upload(
                id="upload-data",
                children=html.Div(
                    ["Drag and Drop or ", html.A("Select Files")]
                ),
                multiple=False,
                accept=".txt, .csv",
            )
        ],
            className="three columns",
            id="button",
        ),
    ],
        id="header",
        className="row flex-display",
        style={"margin-bottom": "25px"},
    ),
    html.Div(id="output-data-upload"),
],
id="mainContainer",
style={"display": "flex", "flex-direction": "column"},
)


# Helper Functions
def data_bars(column_data, column_apply):
    n_bins = 100
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    ranges = [100 * i for i in bounds]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        max_bound_percentage = bounds[i] * 100
        styles.append({
            'if': {
                'filter_query': (
                    '{{{column}}} >= {min_bound}' +
                    (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column_data, min_bound=min_bound, max_bound=max_bound),
                'column_id': column_apply
            },
            'background': (
                """
                    linear-gradient(90deg,
                    #CACACA 0%,
                    #CACACA {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(max_bound_percentage=max_bound_percentage)
            ),
            'paddingBottom': 2,
            'paddingTop': 2
        })

    return styles

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
        ["MTL 3600", "Mathematics of Elem Curriculum",],
        ["MTL 3620", "Mathematics of Secondary Curr",],
        ["MTL 3630", "Teaching Secondary Mathematics",],
        ["MTL 3638", "Secondry Mathematics Field Exp",],
        ["MTL 3750", "Number & Alg in the K-8 Curric",],
        ["MTL 3760", "Geom & Stats in the K-8 Curric",],
        ["MTL 3850", "STEM Teaching and Learning",],
        ["MTL 3858", "STEM Practicum",],
        ["MTL 4690", "Stdnt Teach & Sem:Secndry 7-12",],
        ["MTLM 5020", "Integrated Math II",],
        ["MTLM 5600", "Math of the Elem Curriculum",],
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

    # add columns for Access Table
    _df.insert(len(_df.columns), "PTCR", 0)
    _df["PTCR"] = _df["Credit"]
    _df.insert(len(_df.columns), "Final", "Y")
    _df.insert(len(_df.columns), "OrigRoom", " ")
    _df["OrigRoom"] = _df["Loc"]
    _df.insert(len(_df.columns), "Bldg", " ")
    _df.insert(len(_df.columns), "Room", " ")
    _df["Bldg"] = _df["Loc"].str.split(" ").str[0]
    _df["Room"] = _df["Loc"].str.split(" ").str[1]
    _df.insert(len(_df.columns), "Dates", " ")
    _df["Dates"] = _df["Begin/End"] + "/" + str(term_code[2:4])
    _df.insert(len(_df.columns), "Class Start Date", " ")
    _df.insert(len(_df.columns), "Class End Date", " ")
    _df["Class Start Date"] = _df["Begin/End"].str[0:5] +  "/" + str(term_code[2:4])
    _df["Class End Date"] = _df["Begin/End"].str[-5:] +  "/" + str(term_code[2:4])

    # reset index and remove old index column
    _df = _df.reset_index()
    _df = _df.drop([_df.columns[0]], axis=1)

    # change all online final flags to N since they do not need a room
    for row in _df[_df["Cam"].str.startswith("I", na=False)].index.tolist():
        _df.loc[row, "Final"] = "N"

    # correct report to also include missing data for MTH 1109
    for row in _df[_df["Subj"].str.contains("MTH") & _df["Nmbr"].str.contains("1109")].index.tolist():
        for col in ["Subj", "Nmbr", "CRN", "Sec", "S", "Cam", "T", "Title", "Max", "Enrl", "WCap", "WLst", "Instructor"]:
            _df.loc[row + 1, col] = _df.loc[row, col]
        _df.loc[row + 1, "Credit"] = 0
        _df.loc[row + 1, "PTCR"] = 0

    # correct report to also include missing data for MTH 1108
    for row in _df[_df["Subj"].str.contains("MTH") & _df["Nmbr"].str.contains("1108")].index.tolist():
        for col in ["Subj", "Nmbr", "CRN", "Sec", "S", "Cam", "T", "Title", "Max", "Enrl", "WCap", "WLst", "Instructor"]:
            _df.loc[row + 1, col] = _df.loc[row, col]
        _df.loc[row + 1, "Credit"] = 0
        _df.loc[row + 1, "PTCR"] = 0
        row_dict = _df.loc[row].to_dict()
        row_dict["Instructor"] = ","
        row_dict["Credit"] = 0
        row_dict["PTCR"] = 1
        _df = _df.append(row_dict, ignore_index=True)

    # add columns for Access Table
    _df.insert(len(_df.columns), "Class", " ")
    _df["Class"] = _df["Subj"] + " " + _df["Nmbr"]

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

    return _df, term_code, data_date

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

def to_access(df, report_term):
    _df = df.copy()

    # only use the active courses
    _df = _df[_df["S"]=="A"]

    # update all titles to show full name
    _df = updateTitles(_df)

    # rename columns to match Access
    _df.rename(
        columns={
            "Subject" :"Subj",
            "Number"  :"Nmbr",
            "Section" :"Sec",
            "Credit"  :"CR",
            "Enrolled":"Enrl",
            "WList"   :"WLst",
            "Full"    :"%Ful",
        },
        inplace=True,
    )

    # only grab needed columns and correct ordering
    cols = ["CRN", "Class", "Sec", "S", "Title", "CR", "PTCR", "Final",
            "Days", "Time", "Instructor", "OrigRoom", "Bldg",
            "Room", "Dates", "Class Start Date", "Class End Date", "Campus"]
    _df = _df[cols]

    # setup the IO stream
    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(
        xlsx_io, engine="xlsxwriter", options={"strings_to_numbers": True}
    )
    # _df["Sec"] = _df["Sec"].apply(lambda x: '="{x:s}"'.format(x=x))
    _df.to_excel(writer, sheet_name="Schedule", index=False)

    # Save it
    writer.save()
    xlsx_io.seek(0)
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    return f"data:{media_type};base64,{data}"

def to_excel(df, report_term):
    _df = df.copy()

    # only grab needed columns and correct ordering
    cols = ["Subject", "Number", "CRN", "Section", "S", "Campus", "T", "Title",
            "Credit", "Max", "Enrolled", "WCap", "WList", "Days", "Time", "Loc",
            "Rcap", "Full", "Begin/End", "Instructor", "CHP", "Course", "Ratio"]
    _df = _df[cols]

    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(
        xlsx_io, engine="xlsxwriter", options={"strings_to_numbers": True}
    )
    _df["Section"] = _df["Section"].apply(lambda x: '="{x:s}"'.format(x=x))
    _df["Number"] = _df["Number"].apply(lambda x: '="{x:s}"'.format(x=x))
    _df.to_excel(writer, sheet_name=report_term, index=False)

    workbook = writer.book
    worksheet = writer.sheets[report_term]

    bold = workbook.add_format({"bold": True})

    rowCount = len(_df.index)

    worksheet.freeze_panes(1, 0)
    worksheet.set_column("A:A", 6.5)
    worksheet.set_column("B:B", 7)
    worksheet.set_column("C:C", 5.5)
    worksheet.set_column("D:D", 6.5)
    worksheet.set_column("E:E", 2)
    worksheet.set_column("F:F", 6.5)
    worksheet.set_column("G:G", 2)
    worksheet.set_column("H:H", 13.2)
    worksheet.set_column("I:I", 5.5)
    worksheet.set_column("J:J", 4)
    worksheet.set_column("K:K", 7)
    worksheet.set_column("L:L", 5)
    worksheet.set_column("M:M", 5)
    worksheet.set_column("N:N", 5.5)
    worksheet.set_column("O:O", 12)
    worksheet.set_column("P:P", 7)
    worksheet.set_column("Q:Q", 4)
    worksheet.set_column("R:R", 3.5)
    worksheet.set_column("S:S", 10.5)
    worksheet.set_column("T:T", 14)

    # Common cell formatting
    # Light red fill with dark red text
    format1 = workbook.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})
    # Light yellow fill with dark yellow text
    format2 = workbook.add_format({"bg_color": "#FFEB9C", "font_color": "#9C6500"})
    # Green fill with dark green text.
    format3 = workbook.add_format({"bg_color": "#C6EFCE", "font_color": "#006100"})
    # Darker green fill with black text.
    format4 = workbook.add_format({"bg_color": "#008000", "font_color": "#000000"})

    # Add enrollment evaluation conditions

    # classes that have enrollment above 94% of capacity
    worksheet.conditional_format(
        1,  # row 2
        10,  # column K
        rowCount,  # last row
        10,  # column K
        {"type": "formula", "criteria": "=$K2>0.94*$J2", "format": format4},
    )

    # classes that have enrollment above 80% of capacity
    worksheet.conditional_format(
        1,  # row 2
        10,  # column K
        rowCount,  # last row
        10,  # column K
        {"type": "formula", "criteria": "=$K2>0.8*$J2", "format": format3},
    )

    # classes that have enrollment below 10 students
    worksheet.conditional_format(
        1,  # row 2
        10,  # column K
        rowCount,  # last row
        10,  # column K
        {"type": "formula", "criteria": "=$K2<10", "format": format1},
    )

    # classes that have students on the waitlist
    worksheet.conditional_format(
        1,  # row 2
        12,  # column M
        rowCount,  # last row
        12,  # column M
        {"type": "cell", "criteria": ">", "value": 0, "format": format2},
    )

    # Save it
    writer.save()
    xlsx_io.seek(0)
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    return f"data:{media_type};base64,{data}"

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
            df, term_code, data_date = tidy_txt(io.StringIO(decoded.decode("utf-8")))
        elif "csv" in filename:
            # Assume the user uploaded a banner Shift-F1 export quasi-csv file with .csv extension
            df, term_code, data_date = tidy_csv(io.StringIO(decoded.decode("utf-8")))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    df["Time"] = df["Time"].apply(lambda x: convertAMPMtime(x))

    # fill Nan with zeros
    df["Enrolled"] = df["Enrolled"].fillna(0)
    df["Rcap"] = df["Rcap"].fillna(0)
    df["Full"] = df["Full"].fillna(0)

    # Helper columns
    df.loc[:, "CHP"] = df["Credit"] * df["Enrolled"]
    df.loc[:, "Course"] = df["Subject"] + df["Number"]
    df.loc[:, "Ratio"] = 100 * df["Enrolled"] / df["Max"]

    if term_code[-2:] == "30":
        report_term = "Spring " + term_code[0:4]
    elif term_code[-2:] == "40":
        report_term = "Summer " + term_code[0:4]
    elif term_code[-2:] == "50":
        report_term = "Fall " + term_code[0:4]

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

    html_layout = [
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H6(
                            "0",
                            id="total_sections_text"
                        ),
                        html.P("Total Sections"),
                    ],
                        id="sections",
                        className="mini_container",
                    ),
                    html.Div([
                        html.H6(
                            "0",
                            id="total_courses_text"
                        ),
                        html.P("Total Courses"),
                    ],
                        id="total_courses",
                        className="mini_container",
                    ),
                    html.Div([
                        html.H6(
                            "0",
                            id="total_CHP_text"),
                        html.P("Total Credit Hour Production"),
                    ],
                        id="total_CHP",
                        className="mini_container",
                    ),
                    html.Div([
                        html.H6(
                            "0.0",
                            id="avg_enrollment_text"
                        ),
                        html.P("Average Enrollment by CRN"),
                    ],
                        id="avg_enrollment",
                        className="mini_container",
                    ),
                    html.Div([
                        html.H6(
                            "0.00",
                            id="avg_enrollment_by_instructor_text",
                        ),
                        html.P("Average Enrollment per Instructor"),
                    ],
                        id="avg_enrollment_by_instructor",
                        className="mini_container",
                    ),
                    html.Div([
                        html.H6(
                            "0.00%",
                            id="avg_fill_rate_text"),
                        html.P("Average Fill Rate"),
                    ],
                        id="avg_fill_rate",
                        className="mini_container",
                    ),
                    html.Div([
                        html.H6(
                            "0.00",
                            id="avg_waitlist_text"
                        ),
                        html.P("Average Waitlist"),
                    ],
                        id="avg_waitlist",
                        className="mini_container",
                    ),
                ],
                    className="row container-display",
                ),
            ],
                className="twelve columns",
            ),
        ],
            className="row flex-display",
        ),
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=blankFigure,
                    id="max_v_enrl_by_crn_graph"
                )
            ],
                className="pretty_container six columns",
            ),
            html.Div([
                dcc.Graph(
                    figure=blankFigure,
                    id="max_v_enrl_by_course_graph"
                )
            ],
                className="pretty_container six columns",
            ),
        ],
            className="row flex-display",
        ),
        html.Div([
            html.Div([
                html.Div([
                    # place holder
                ],
                    id="enrl_by_instructor",
                    style={
                        'width': '96%',
                        'display': 'block',
                        'marginLeft': 'auto',
                        'marginRight': 'auto',
                    }
                ),
            ],
                className="pretty_container four columns",
            ),
            html.Div([
                html.Div([
                    # place holder
                ],
                    id="chp_by_course",
                    style={
                        'width': '96%',
                        'display': 'block',
                        'marginLeft': 'auto',
                        'marginRight': 'auto',
                    }
                ),
            ],
                className="pretty_container four columns",
            ),
            html.Div([
                dcc.Graph(
                    figure=blankFigure,
                    id="graph_f2f"
                ),
                html.Label([
                    "Enrollment:",
                    dcc.RadioItems(
                        id='enrollment-max-actual',
                        options=[
                            {'label': 'Max', 'value': 'Max'},
                            {'label': 'Actual', 'value': 'Enrolled'}
                        ],
                        labelStyle={'display': 'inline-block'},
                        className="dcc_control",
                        value='Max'
                    ),
                ]),
            ],
                className="pretty_container four columns",
            ),
        ],
            className="row flex-display",
        ),
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=blankFigure,
                    id="enrl_by_instructor_graph",
                )
            ],
                className="pretty_container six columns",
            ),
            html.Div([
                dcc.Graph(
                    figure=blankFigure,
                    id="chp_by_course_graph",
                )
            ],
                className="pretty_container six columns",
            ),
        ],
            className="row flex-display",
        ),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Label([
                            "Predefined Queries:",
                            dcc.Dropdown(
                                id='filter-query-dropdown',
                                options=[
                                    {'label': 'Active Classes', 'value': '{S} contains A'},
                                    {'label': 'Active CS Classes', 'value': '{Subject} contains C && {S} contains A'},
                                    {'label': 'Active Math Classes', 'value': '{Subject} contains M && {S} contains A'},
                                    {'label': 'Active MTL Classes', 'value': '({Subject} contains MTL || {Number} contains 1610 || {Number} contains 2620) && {S} contains A'},
                                    {'label': 'Active Math without MTL', 'value': '{Subject} > M && {Subject} < MTL && ({Number} <1610 || {Number} >1610) && ({Number} <2620 || {Number} >2620) && {S} contains A'},
                                    {'label': 'Active CS Lower Division', 'value': '{Subject} contains C && {Number} < 3000 && {S} contains A'},
                                    {'label': 'Active CS Upper Division', 'value': '{Subject} contains C && {Number} >= 3000 && {S} contains A'},
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
                    ], style={'margin-left': '5px',}),

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
                    ], style={'margin-left': '5px',}),

                    html.Br(),

                    html.Div([
                        dcc.Input(
                            id='filter-query-input',
                            placeholder='Enter filter query',
                            className="dcc_control",
                        ),
                    ], style={'margin-left': '5px',}),
                    html.Br(),
                    html.Div(id='filter-query-output'),

                    html.Hr(),
                    ]),
                    html.Div([
                        dash_table.DataTable(
                            id="datatable-filtering",
                            data=df.to_dict("records"),
                            columns=[{'name': n, 'id': i} for n,i in zip([
                                "Subj", "Nmbr", "CRN", "Sec", "S", "Cam", "Title",
                                "Credit", "Max", "Enrl", "WCap", "WLst", "Days", "Time",
                                "Loc", "Rcap", "%Ful", "Begin/End", "Instructor"
                            ],[*df.columns[:6],*df.columns[7:-3]])],
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
                                for i,w in zip([*df.columns[:6],*df.columns[7:-3]],
                                               ['3.5%', '5%', '4%', '4%', '2%', '4%',
                                                '10%', '5%', '4%', '4%', '5%', '5%', '5%',
                                                '7.5%', '6%', '4.5%', '4.5%', '7.5%', '9.5%'])
                            ],
                            sort_action="native",
                            filter_action="native",
                            fixed_rows={"headers": True, "data": 0},
                            page_size=5000,
                            style_data_conditional=[
                                *data_bars('Ratio', 'Max'),
                                {
                                    "if": {"row_index": "odd"},
                                    "backgroundColor": "rgb(248, 248, 248)",
                                },
                                {
                                    'if': {
                                        'filter_query': '{WList} > 0',
                                        'column_id': 'WList'
                                    },
                                    'backgroundColor': '#FFEB9C',
                                    'color': '#9C6500'
                                },
                                {
                                    'if': {
                                        'filter_query': '({Enrolled} < 10 && {Max} >= 20 && {S} contains A) || ({Enrolled} < 6 && {S} contains A)',
                                        'column_id': 'Enrolled'
                                    },
                                    'backgroundColor': '#FFC7CE',
                                    'color': '#9C0006'
                                },
                                {
                                    'if': {
                                        'filter_query': '{Ratio} > 80',
                                        'column_id': 'Enrolled'
                                    },
                                    'backgroundColor': '#C6EFCE',
                                    'color': '#006100'
                                },
                                {
                                    'if': {
                                        'filter_query': '{Ratio} > 94',
                                        'column_id': 'Enrolled'
                                    },
                                    'backgroundColor': '#008000',
                                    'color': 'white'
                                },
                                {
                                    'if': {
                                        'filter_query': '{S} contains C',
                                    },
                                    'backgroundColor': '#FF4136',
                                },
                            ],
                    )
                ],
                    style={
                        'width': '98%',
                        'display': 'block',
                        'marginLeft': 'auto',
                        'marginRight': 'auto',
                    }
                ),
            ],
                className="pretty_container full-width column",
            ),
        ],
            className="row flex-display",
        ),
    ]
    return html_layout, df, term_code, report_term, data_date

@app.callback(
    [Output("output-data-upload", "children"),
     Output("main_title", "children")],
    [Input("upload-data", "contents")],
    [State("upload-data", "filename"), State("upload-data", "last_modified")],
)
def update_output(contents, name, date):
    """When files are selected, call parse-contents and return the new html elements."""

    if contents is not None:
        data_children, df, term_code, report_term, data_date = parse_contents(contents, name, date)
        title_children = [
            html.H3(
                "SWRCGSR Enrollment for " + report_term,
                id="title-report-semester",
                style={"margin-bottom": "0px"},
            ),
            html.H5(
                "Statistics and Graphs: " + datetime.datetime.strftime(data_date, "%d-%b-%Y").upper(),
                style={"margin-top": "0px"}
            ),
            html.Div([
            html.A(
                "Download Excel Data",
                id="excel-download",
                download="SWRCGSR_{0}.xlsx".format(
                    term_code
                ),
                href=to_excel(df, report_term),
                target="_blank",
            ),
            ]),
            html.Div([
            html.A(
                "Download Access Table",
                id="access-download",
                download="Schedule_{0}.xlsx".format(
                    term_code
                ),
                href=to_access(df, report_term),
                target="_blank",
            ),
            ]),
        ]
    else:
        data_children = []
        title_children = [
            html.H3(
                "SWRCGSR Enrollment",
                id="title-report-semester",
                style={"margin-bottom": "0px"},
            ),
            html.H5(
                "Statistics and Graphs",
                style={"margin-top": "0px"}
            ),
        ]
    return [data_children, title_children]

@app.callback(
    [Output("total_sections_text", "children"),
     Output("total_courses_text", "children"),
     Output("total_CHP_text", "children"),
     Output("avg_enrollment_text", "children"),
     Output("avg_fill_rate_text", "children"),
     Output("avg_enrollment_by_instructor_text", "children"),
     Output("avg_waitlist_text", "children"),
    ],
    Input('datatable-filtering', 'derived_viewport_data'),
)
def update_stats(data):
    if data:
        df = pd.DataFrame(data)
        return [
            "{:,.0f}".format(df["CRN"].nunique()),
            "{:,.0f}".format(df["Course"].nunique()),
            "{:,.0f}".format(df["CHP"].sum()),
            round(df["Enrolled"].mean(), 2),
            "{}%".format(round(df["Ratio"].mean(), 2)),
            round(df.groupby("Instructor").agg({"Enrolled": "sum"}).values.mean(), 2),
            round(df["WList"].mean(), 2),
        ]
    else:
        return ["0", "0", "0", "0.00", "0.00", "0.00", "0.00"]

@app.callback(
    [Output('filter-query-input', 'style'),
     Output('filter-query-output', 'style')],
    [Input('filter-query-read-write', 'value')]
)
def query_input_output(val):
    input_style = {'width': '100%', 'height': '35px'}
    output_style = {'height': '35px'}
    if val == 'read':
        input_style.update(display='none')
        output_style.update(display='inline-block', marginLeft='15px')
    else:
        input_style.update(display='inline-block')
        output_style.update(display='none')
    return input_style, output_style

@app.callback(
    Output('datatable-filtering', 'filter_query'),
    [Input('filter-query-input', 'value')]
)
def write_query(query):
    if query is None:
        return ''
    return query

@app.callback(
    Output('filter-query-output', 'children'),
    [Input('datatable-filtering', 'filter_query')]
)
def read_query(query):
    if query is None:
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
    Output('max_v_enrl_by_crn_graph', 'figure'),
    Input('datatable-filtering', 'derived_viewport_data'),
    State('max_v_enrl_by_crn_graph', 'figure'),
)
def max_v_enrl_by_crn(data, fig):
    if data:
        df = pd.DataFrame(data)
        return (
            px.bar(
                df,
                x="CRN",
                y=["Max", "Enrolled"],
                title="Enrollment per Section",
                hover_name="CRN",
                hover_data={
                    "Course": True,
                    "CRN": False,
                    "Instructor": True,
                    "Ratio": True,
                    "variable": False,
                    "WList": True,
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
    else:
        return fig

@app.callback(
    Output('max_v_enrl_by_course_graph', 'figure'),
    Input('datatable-filtering', 'derived_viewport_data'),
    State('max_v_enrl_by_course_graph', 'figure'),
)
def max_v_enrl_by_course(data, fig):
    if data:
        df = pd.DataFrame(data)
        _df = (
            df.groupby("Course")
            .agg(
                {
                    "Instructor": "size",
                    "Credit": "sum",
                    "Enrolled": "sum",
                    "Max": "sum",
                    "WList": "sum",
                    "CHP": "sum",
                    "Ratio": "mean",
                }
            )
            .sort_values("Course", ascending=False)
        )
        return (
            px.bar(
                _df,
                y=["Max", "Enrolled"],
                title="Enrollment per Course",
                hover_data={"Ratio": True, "WList": True},
            )
            .update_layout(
                showlegend=False,
                xaxis_type="category",
                yaxis_title="Enrolled",
                barmode="overlay",
            )
        )
    else:
        return fig

@app.callback(
    Output('graph_f2f', 'figure'),
    [Input('datatable-filtering', 'derived_viewport_data'),
     Input('enrollment-max-actual', 'value'),],
    State('graph_f2f', 'figure'),
)
def graph_f2f(data, toggle, fig):
    if data:
        df = pd.DataFrame(data)
        _df = df[["Loc", toggle]]
        _df = _df.groupby("Loc", as_index=False).sum()
        t = _df[toggle].sum()
        o = _df[_df["Loc"].isin(["ASYN  T", "SYNC  T", "ONLI  T", "MOST  T"])][toggle].sum()
        s = _df[_df["Loc"].isin(["SYNC  T"])][toggle].sum()

        fig = make_subplots(rows=2,
                            cols=1,
                            specs=[[{'type':'domain'}], [{'type':'domain'}]],
                            vertical_spacing=0.15,
                           )
        fig.add_trace(go.Pie(labels=["Async", "Sync"],
                             values=[o-s, s],
                             name="Async vs Sync"),
                      1, 1)
        fig.add_trace(go.Pie(labels=["F2F", "Online"],
                             values=[t-o, o],
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
    else:
        return fig

@app.callback(
    Output('enrl_by_instructor_graph', 'figure'),
    Input('datatable-filtering', 'derived_viewport_data'),
    State('enrl_by_instructor_graph', 'figure'),
)
def graph_enrollment_by_instructor(data, fig):
    if data:
        df = pd.DataFrame(data)
        return (
            px.bar(
                df,
                x="Instructor",
                y="Enrolled",
                color="Ratio",
                title="Enrollment by Instructor",
                color_continuous_scale=px.colors.sequential.RdBu,
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
    else:
        return fig

@app.callback(
    Output('chp_by_course_graph', 'figure'),
    Input('datatable-filtering', 'derived_viewport_data'),
    State('chp_by_course_graph', 'figure'),
)
def chp_by_course(data, fig):
    if data:
        df = pd.DataFrame(data)
        return (
            px.bar(
                df,
                x="Course",
                y="CHP",
                title="Credit Hour Production by Course",
                color="Ratio",
                color_continuous_scale=px.colors.sequential.RdBu,
            )
            .update_xaxes(categoryorder="category descending")
            .update_layout(showlegend=False)
        )
    else:
        return fig

@app.callback(
    Output('enrl_by_instructor', 'children'),
    Input('datatable-filtering', 'derived_viewport_data'),
)
def enrl_by_instructor(data):
    if data:
        df = pd.DataFrame(data)
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
    Input('datatable-filtering', 'derived_viewport_data'),
)
def chp_by_course(data):
    if data:
        df = pd.DataFrame(data)
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

# Main
if __name__ == "__main__":
    # app.run_server(debug=True, host='172.16.0.153')
    app.run_server(debug=True)
