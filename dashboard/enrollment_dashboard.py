# -*- coding: utf-8 -*-

from utilities import *

# Import required libraries
import dash
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash import dash_table, html, dcc
import numpy as np
import base64
import io
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import datetime

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

app.title = "Enrollment Report Statistics"

app.config.update({
    'suppress_callback_exceptions': True,
})

# specifics for the math.msudenver.edu server
if mathserver:
    app.config.update({
       'url_base_pathname':'/dash/',
       'routes_pathname_prefix':'/dash/',
       'requests_pathname_prefix':'/dash/',
    })


# Helper Functions
def median(nums):
    if len(nums):
        if len(nums) == 1:
            return nums[0]
        nums = sorted(nums)
        middle1 = (len(nums) - 1) // 2
        middle2 = len(nums) // 2
        return (nums[middle1] + nums[middle2]) / 2
    return 0


def multi_mode(lst):

    if len(lst) == 0:
        return [0]

    frequencies = {}

    for num in lst:
        frequencies[num] = frequencies.get(num,0) + 1

    mode = max([value for value in frequencies.values()])

    modes = []

    for key in frequencies.keys():
        if frequencies[key] == mode:
            modes.append(key)

    modes = sorted(modes)
    return modes[:3]


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
        xlsx_io, engine='xlsxwriter', engine_kwargs={'options':{'strings_to_numbers': True}}
    )
    # _df["Sec"] = _df["Sec"].apply(lambda x: '="{x:s}"'.format(x=x))
    _df.to_excel(writer, sheet_name="Schedule", index=False)

    # Save it
    writer.close()
    xlsx_io.seek(0)
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    return data

def to_excel(df, report_term):
    """
    This will export the Number and Sections as formulas to preserve the leading zeros
    To correctly import this back into Python, you will need to open it and save it in
    Excel first, before importing.
    """
    _df = df.copy()

    # only grab needed columns and correct ordering
    cols = ["Subject", "Number", "CRN", "Section", "S", "Campus", "T", "Title",
            "Credit", "Max", "Enrolled", "WCap", "WList", "Days", "Time", "Loc",
            "Rcap", "Full", "Begin/End", "Instructor", "CHP", "Course", "Ratio", "Calc"]
    _df = _df[cols]

    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(
        xlsx_io, engine='xlsxwriter', engine_kwargs={'options':{'strings_to_numbers': True}}
    )

    _df["Section"] = _df["Section"].apply(lambda x: '="{x:s}"'.format(x=str(x)))
    _df["Number"] = _df["Number"].apply(lambda x: '="{x:s}"'.format(x=x))
    _df.to_excel(writer, sheet_name=report_term, index=False)

    workbook = writer.book
    worksheet = writer.sheets[report_term]

    # bold = workbook.add_format({"bold": True})

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
    worksheet.set_column("U:U", 8)

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
    writer.close()
    xlsx_io.seek(0)
    # media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    return data

def to_excel_dean(df, report_term):
    _df = df.copy()

    # only grab needed columns and correct ordering
    cols = ["Subject", "Number", "CRN", "Section", "S", "Campus", "T", "Title",
            "Credit", "Max", "Enrolled", "WCap", "WList", "Days", "Time", "Loc",
            "Rcap", "Full", "Begin/End", "Instructor", "CHP", "Course", "Ratio", "Calc"]
    _df = _df[cols]

    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(
        xlsx_io, engine='xlsxwriter', engine_kwargs={'options':{'strings_to_numbers': True}}
    )
    _df["Section"] = _df["Section"].apply(lambda x: '="{x:s}"'.format(x=x))
    _df["Number"] = _df["Number"].apply(lambda x: '="{x:s}"'.format(x=x))
    _df.to_excel(writer, sheet_name=report_term, index=False)

    workbook = writer.book
    worksheet = writer.sheets[report_term]

    # bold = workbook.add_format({"bold": True})

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
    worksheet.set_column("U:U", 8)

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

    # 1000 level classes that have fewer than 20 students
    worksheet.conditional_format(
        1,  # row 2
        10,  # column K
        rowCount,  # last row
        10,  # column K
        {"type": "formula", "criteria": "=_xlfn.AND($K2<20,_xlfn.NUMBERVALUE($B2)<2000)", "value": "TRUE", "format": format1},
    )

    # 2000 level classes that have fewer than 18 students
    worksheet.conditional_format(
        1,  # row 2
        10,  # column K
        rowCount,  # last row
        10,  # column K
        {"type": "formula", "criteria": "=_xlfn.AND($K2<18,_xlfn.NUMBERVALUE($B2)>1999,_xlfn.NUMBERVALUE($B2)<3000)", "value": "TRUE", "format": format1},
    )

    # 3000 level classes that have fewer than 15 students
    worksheet.conditional_format(
        1,  # row 2
        10,  # column K
        rowCount,  # last row
        10,  # column K
        {"type": "formula", "criteria": "=_xlfn.AND($K2<15,_xlfn.NUMBERVALUE($B2)>2999,_xlfn.NUMBERVALUE($B2)<4000)", "value": "TRUE", "format": format1},
    )

    # 4000 level classes that have fewer than 10 students
    worksheet.conditional_format(
        1,  # row 2
        10,  # column K
        rowCount,  # last row
        10,  # column K
        {"type": "formula", "criteria": "=_xlfn.AND($K2<10,_xlfn.NUMBERVALUE($B2)>3999)", "value": "TRUE", "format": format1},
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
    writer.close()
    xlsx_io.seek(0)
    # media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    return data

def parse_contents(contents, filename): #, date):
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

    _, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)

    df = pd.DataFrame()
    term_code = ''
    data_date = ''

    # try:
    if "txt" in filename:
        # Assume that the user uploaded a banner fixed width file with .txt extension
        df, term_code, data_date = tidy_txt(io.StringIO(decoded.decode("utf-8")))
        df["Time"] = df["Time"].apply(lambda x: convertAMPMtime(x))
    elif "csv" in filename:
        # Assume the user uploaded a banner Shift-F1 export quasi-csv file with .csv extension
        df, term_code, data_date = tidy_csv(io.StringIO(decoded.decode("utf-8")))
        df["Time"] = df["Time"].apply(lambda x: convertAMPMtime(x))
    elif "xlsx" in filename:
        df, term_code, data_date = tidy_xlsx(io.BytesIO(decoded))
    # except Exception as e:
    #     print(e)
    else:
        return html.Div(["There was an error processing this file."])


    # fill Nan with zeros
    df["Enrolled"] = df["Enrolled"].astype(float).fillna(0)
    df["Rcap"] = df["Rcap"].astype(float).fillna(0)
    df["Full"] = df["Full"].astype(float).fillna(0)

    # Helper columns
    df.loc[:, "CHP"] = df["Credit"] * df["Enrolled"]
    df.loc[:, "Course"] = df["Subject"] + df["Number"]

    # protect for division by zero
    for row in df.index.to_list():
        if df.loc[row, "Max"] != 0:
            df.loc[row, "Ratio"] = 100 * df.loc[row, "Enrolled"] / df.loc[row, "Max"]

    if term_code[-2:] == "30":
        report_term = "Spring " + term_code[0:4]
    elif term_code[-2:] == "40":
        report_term = "Summer " + term_code[0:4]
    elif term_code[-2:] == "50":
        report_term = "Fall " + term_code[0:4]
    else:
        report_term = "Unknown " + term_code[0:4]

    return df, report_term, term_code, data_date

def create_datatable(df):
    return [
        dash_table.DataTable(
            id="datatable",
            data=df.to_dict("records"),
            # export_format="csv",
            columns = [
                {'name': 'Subj', 'id': 'Subject'},
                {'name': 'Nmbr', 'id': 'Number'},
                {'name': 'CRN', 'id': 'CRN'},
                {'name': 'Sec', 'id': 'Section'},
                {'name': 'S', 'id': 'S'},
                {'name': 'Cam', 'id': 'Campus'},
                {'name': 'Title', 'id': 'Title'},
                {'name': 'Credit', 'id': 'Credit'},
                {'name': 'Max', 'id': 'Max'},
                {'name': 'Enrl', 'id': 'Enrolled'},
                {'name': 'WCap', 'id': 'WCap'},
                {'name': 'WLst', 'id': 'WList'},
                {'name': 'Days', 'id': 'Days'},
                {'name': 'Time', 'id': 'Time'},
                {'name': 'Loc', 'id': 'Loc'},
                {'name': 'RCap', 'id': 'Rcap'},
                {'name': '%Ful', 'id': 'Full'},
                {'name': 'Begin/End', 'id': 'Begin/End'},
                {'name': 'Instructor', 'id': 'Instructor'},
                {'name': 'Calc', 'id': 'Calc', 'editable': True},
            ],
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
                for i,w in zip([*df.columns[:6],*df.columns[7:-14], *df.columns[[-4]]],
                               ['3.5%', '4%', '4%', '3%', '3%', '3%',
                                '18%', '4%', '3%', '4%', '4%', '4%', '4%',
                                '7.5%', '5%', '3.5%', '3.5%', '6.5%', '9.5%', '3%'])
            ],
            sort_action="native",
            editable=False,
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
                # 1000 level min of 20; 2000 level min of 18, 3000 level min of 15; 4000 level min of 10
                {
                    'if': {
                        'filter_query': '{S} contains A && {Credit} > 0 && ({Subject} contains MTH || {Subject} contains MTL) && ({Number} != "1082" && {Number} != "1101" && {Number} != "1116" && {Number} != "1312") && ({Enrolled} < 20 && {Number} < 2000) || ({Enrolled} < 18 && ({Number} >= 2000 && {Number} < 3000)) || ({Enrolled} < 15 && ({Number} >= 3000 && {Number} < 4000)) || ({Enrolled} < 10 && {Number} >= 4000)',
                        'column_id': 'Enrolled'
                    },
                    'backgroundColor': '#FFC7CE',
                    'color': '#9C0006'
                },
                # {
                #     'if': {
                #         'filter_query': '({Enrolled} < 10 && {Max} >= 20 && {S} contains A) || ({Enrolled} < 6 && {S} contains A)',
                #         'column_id': 'Enrolled'
                #     },
                #     'backgroundColor': '#FFC7CE',
                #     'color': '#9C0006'
                # },
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
    ]

def freq_dist_graph(data, m):

    if len(data):

        freq_dist = pd.DataFrame({'Enrolled': data, 'Value': data}).groupby('Enrolled').count()

        X=freq_dist.index.to_list()
        Y=freq_dist['Value'].to_list()

    else:
        X = [0, m]
        Y = [0, 0]

    fig = make_subplots(rows=1, cols=1,)
    fig.add_trace(
        go.Bar(
            x=X,
            y=Y,
            width=1,
            customdata=pd.DataFrame({'x': X, 'y': Y}),
            hovertemplate='<br>'.join([
                'Enrl: %{customdata[0]}',
                'Freq: %{customdata[1]}'])+'<extra></extra>',
            marker_color='#00447c',
        ),
        row=1,col=1,
    )
    fig.update_layout(
        showlegend=False,
        xaxis_range=[-0.5, m+0.5],
        xaxis={
            'showgrid': False,
            'showticklabels': False,
            'zeroline': False,
        },
        yaxis={
            'showgrid': False,
            'showticklabels': False,
            'zerolinecolor': '#00447c',
            'zerolinewidth': 1,
        },
        margin=dict(l=10, r=10, b=10, t=10),
        height=50,
        paper_bgcolor='#f9f9f9',
        plot_bgcolor='#f9f9f9',
    )

    return fig

def summary_stats(df, category, m):

    sections = 0
    courses = 0
    waitlist = 0
    enrolled = 0
    min_enrl = 0
    avg_enrl = 0
    med_enrl = 0
    mod_enrl = [0]
    fig=freq_dist_graph([0], 0)

    if not df.empty:

        # only use active courses
        df = df[df['S'] == 'A']

        if category == 'Lab':
            df = df[df['Calc'] == 'L']

            sections = df["CRN"].nunique()
            courses = df["Class"].nunique()
            waitlist = df['WList'].sum()
            enrolled = df['Enrolled'].sum()
            min_enrl = df["Enrolled"].min()
            avg_enrl = df["Enrolled"].mean()
            if np.isnan(avg_enrl):
                avg_enrl = 0
            med_enrl = df["Enrolled"].median()
            if np.isnan(med_enrl):
                med_enrl = 0
            mod_enrl = multi_mode(df['Enrolled'].to_list())
            fig=freq_dist_graph(df['Enrolled'].to_list(), m)


        elif category == 'Total':
            df_labs = df[df['Calc']=='L']
            lab_sections = df_labs["CRN"].nunique()
            lab_courses = df_labs["Class"].nunique()

            # only courses that we want included in calculations
            df_N = df[(df['Calc'] == 'N') & (df['Credit'] > 0)]
            df = df[df['Calc'] == 'Y']

            # face-to-face courses
            df_M = df[(df["Campus"]=="M")]

            # online courses
            df_I = df[(df["Campus"]=="I")]

            # include all courses marked 'Y' and subtract labs and 5000 level courses
            sections = df["CRN"].nunique() - lab_sections - df[df['Number'].str.startswith('5')]["CRN"].nunique()
            if sections > 0:
                courses = df["Class"].nunique() - lab_courses
                waitlist = df['WList'].sum()

                # add in the independent studies and omnibus courses
                # enrolled = df['Enrolled'].sum() + df_N['Enrolled'].sum()

                # calculate enrollments for each day/time/loc block
                enrl = df_M[['Enrolled', 'DaysTimeLoc']].groupby(['DaysTimeLoc']).sum()['Enrolled'].tolist()
                # add in the online sections
                enrl += df_I['Enrolled'].tolist()
                # add in the F2F without day/time/loc (such as independent studies)
                enrl += df_M[df_M['DaysTimeLoc'].isna()]['Enrolled'].to_list()

                # courses marked with a 'N' are not included in minimum, median, mode or sections
                sections = len(enrl)

                min_enrl = np.min(enrl)
                med_enrl = median(enrl)
                mod_enrl = multi_mode(enrl)
                fig=freq_dist_graph(enrl, m)

                # no add in the students in those sections that we ommited
                enrl += df_N['Enrolled'].to_list()

                enrolled = sum(enrl)

                avg_enrl = enrolled / sections
                # avg_enrl = np.mean(enrl)
            else:
                sections = 0

        else:
            df_labs = df[df['Calc']=='L']
            lab_sections = df_labs["CRN"].nunique()
            lab_courses = df_labs["Class"].nunique()

            # only courses that we want included in calculations
            df = df[df['Calc'] == 'Y']

            # face-to-face courses
            df_M = df[(df["Campus"]=="M")]

            # online courses
            df_I = df[(df["Campus"]=="I")]

            # print(df_labs["CRN"])
            # print(df["CRN"])
            sections = df["CRN"].nunique() - lab_sections
            if sections > 0:
                courses = df["Class"].nunique() - lab_courses
                waitlist = df['WList'].sum()
                enrolled = df['Enrolled'].sum()

                # calculate enrollments for each day/time/loc block
                enrl = df_M[['Enrolled', 'DaysTimeLoc']].groupby(['DaysTimeLoc']).sum()['Enrolled'].tolist()
                # add in the online sections
                enrl += df_I['Enrolled'].tolist()
                # add in the F2F without day/time/loc (such as independent studies)
                enrl += df_M[df_M['DaysTimeLoc'].isna()]['Enrolled'].to_list()

                min_enrl = np.min(enrl)
                avg_enrl = np.mean(enrl)
                med_enrl = median(enrl)
                mod_enrl = multi_mode(enrl)
                fig=freq_dist_graph(enrl, m)
            else:
                sections = 0


    children=[
        html.H6(category + " Enrollment"),
        html.Table([
            html.Tr([
                html.Td(["Sections: "]),
                html.Td([
                    "{:,.0f}".format(sections)
                ],
                    style={'textAlign':'right'},
                ),
            ]),
            html.Tr([
                html.Td(["Courses: "]),
                html.Td([
                    "{:,.0f}".format(courses)
                ],
                    style={'textAlign':'right'},
                ),
            ]),
            html.Tr([
                html.Td(["Waitlist: "]),
                html.Td([
                    '{:,.0f}'.format(waitlist)
                ],
                    style={'textAlign':'right'},
                ),
            ]),
            html.Tr([
                html.Td(["Total: "]),
                html.Td([
                    '{:,.0f}'.format(enrolled)
                ],
                    style={'textAlign':'right'},
                ),
            ]),
            html.Tr([
                html.Td(["Min: "]),
                html.Td([
                    "{:,.0f}".format(min_enrl)
                ],
                    style={'textAlign':'right'},
                ),
            ]),
            html.Tr([
                html.Td(["Mean: "]),
                html.Td([
                    "{:,.2f}".format(avg_enrl)
                ],
                    style={'textAlign':'right'},
                ),
            ]),
            html.Tr([
                html.Td(["Median: "]),
                html.Td([
                    '{:,.1f}'.format(med_enrl)
                ],
                    style={'textAlign':'right'},
                ),
            ]),
            html.Tr([
                html.Td(["Mode: "]),
                html.Td([
                    ', '.join(['{:,.0f}'.format(_x) for _x in mod_enrl]),
                ],
                    style={'textAlign':'right'},
                ),
            ]),
        ],
            style={'width':'100%'},
        ),
        html.Div([
            dcc.Graph(
                figure=fig,
                config={
                    'displaylogo': False,
                    'displayModeBar': False,
                    'showAxisDragHandles': False,
                },
            )
        ],
            style={'width': '95%'},
        ),
    ]
    return children

def create_calc_row_layout(df, df_all):

    max_enrl = 0
    if not df.empty:
        # max_enrl = df['Enrolled'].max()
        _df = labs_combined(df_all)
        max_enrl = _df['Enrolled'].max()

    mask_1000 = df[df['Number'].str.startswith('1')].index.to_list()
    mask_2000 = df[df['Number'].str.startswith('2')].index.to_list()
    mask_3000 = df[df['Number'].str.startswith('3')].index.to_list()
    mask_4000 = df[df['Number'].str.startswith('4')].index.to_list()

    children=[
        html.Div([
            html.Div([
                html.Div(
                    summary_stats(df, 'Lab', max_enrl),
                    id="lab_enrollment",
                    className="mini_container",
                    style={'width': '17.5%'},
                ),
                html.Div(
                    summary_stats(df.loc[mask_1000], '1000', max_enrl),
                    id="1000_enrollment",
                    className="mini_container",
                    style={'width': '17.5%'},
                ),
                html.Div(
                    summary_stats(df.loc[mask_2000], '2000', max_enrl),
                    id="2000_enrollment",
                    className="mini_container",
                    style={'width': '17.5%'},
                ),
                html.Div(
                    summary_stats(df.loc[mask_3000], '3000', max_enrl),
                    id="3000_enrollment",
                    className="mini_container",
                    style={'width': '17.5%'},
                ),
                html.Div(
                    summary_stats(df.loc[mask_4000], '4000', max_enrl),
                    id="4000_enrollment",
                    className="mini_container",
                    style={'width': '17.5%'},
                ),
                html.Div(
                    summary_stats(df, 'Total', max_enrl),
                    id="calc_total_enrollment",
                    className="mini_container",
                    style={'width': '17.5%'},
                ),
                # html.Div([
                    # html.H6("Notes:"),
                    # html.Ul([
                    # html.Li([
                        # "Lab enrollments, marked with an 'L' in the datatable,  \
                        # are not included in Total, Lower, or Upper Division \
                        # calculations."]),
                    # html.Li([
                        # "Rows marked with an 'N' in the datatable are not \
                        # included in Total, Lower, or Upper Division \
                        # calculations."]),
                    # ]),
                # ],
                    # id="notes_enrollment",
                    # className="mini_container",
                    # style={'width': '30%'},
                # ),
            ],
                style={'display': 'flex'},
            ),
        ],
            className="pretty_container twelve columns",
        ),
    ]

    return children

def labs_combined(df):
    # Combine Max, Enrollments, and WaitLists for Co-Requisite Labs with their parents

    # only use the active courses
    df = df[df["S"]=="A"]

    parent_lab = {"1080": "1081", "1110": "1111", "1112": "1115", "1310": "1311"}
    # filter for parent sections
    for parent in parent_lab.keys():
        mask_parents = (df['Number'] == parent)

        #filter for lab sections
        mask_labs = (df['Number'] == parent_lab[parent])
        for row_p in df[mask_parents].index.tolist():
            for row_l in df[mask_labs].index.tolist():
                if (df.loc[row_p, 'Days'] == df.loc[row_l, 'Days']) and (df.loc[row_p, 'Time'] == df.loc[row_l, 'Time']) and (df.loc[row_p, 'Loc'] == df.loc[row_l, 'Loc']):
                    df.loc[row_p, 'Max'] += df.loc[row_l, 'Max']
                    df.loc[row_p, 'Enrolled'] += df.loc[row_l, 'Enrolled']
                    df.loc[row_p, 'WList'] += df.loc[row_l, 'WList']

                    # recalculate the CHP and Ratio
                    df.loc[row_p, 'CHP'] = df.loc[row_p, 'Credit'] * df.loc[row_p, 'Enrolled']
                    df.loc[row_p, 'Ratio'] = 100 * df.loc[row_p, 'Enrolled'] / df.loc[row_p, 'Max']

    # remove the lab sections from the data
    for lab in parent_lab.values():
        mask = df[df['Number'] != lab].index.to_list()
        df = df.loc[mask]
        # df.drop(df[df['Number'] == lab].index, inplace=True)

    return df

# Create app layout
app.layout = html.Div([
    html.Div([
        html.Img(id='msudenver-logo',
                 src=app.get_asset_url('msudenver-logo.png')),
        html.Div([
                html.H3(
                    "Enrollment Report",
                    id="title-report-semester",
                    style={"marginBottom": "0px"},
                ),
                html.H5(
                    "",
                    id='stats-graph-title',
                    style={"marginTop": "0px"}
                ),
        ],
            style={'textAlign': 'center'},
        ),
        dcc.Upload(id='upload-data',
                   children=html.Button(['Upload file'],
                                        id='upload-data-button',
                                        n_clicks=0,
                                        style={'height': '38px'},
                                        className='button'
                                        ),
                   multiple=False,
                   accept='.txt, .csv, .xlsx'),
    ],
        id='header',
        style={'display': 'flex',
               'justifyContent': 'space-between',
               'alignItems': 'center',
              },
    ),
    html.Div([
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
                style={'display': 'flex'},
                    # className="row container-display",
                ),
            ],
                className="pretty_container twelve columns",
            ),
        ],
            className="row flex-display",
        ),
    html.Div([
        html.Div([
            html.Div([
                html.Div(
                    summary_stats(pd.DataFrame(), '', 0),
                    id="lab_enrollment",
                    className="mini_container two columns",
                ),
                html.Div(
                    summary_stats(pd.DataFrame(), '', 0),
                    id="1000_enrollment",
                    className="mini_container two columns",
                ),
                html.Div(
                    summary_stats(pd.DataFrame(), '', 0),
                    id="2000_enrollment",
                    className="mini_container two columns",
                ),
                html.Div(
                    summary_stats(pd.DataFrame(), '', 0),
                    id="3000_enrollment",
                    className="mini_container two columns",
                ),
                html.Div(
                    summary_stats(pd.DataFrame(), '', 0),
                    id="4000_enrollment",
                    className="mini_container two columns",
                ),
                html.Div(
                    summary_stats(pd.DataFrame(), '', 0),
                    id="calc_total_enrollment",
                    className="mini_container two columns",
                ),
                # html.Div([
                    # html.H6("Notes:"),
                    # html.Ul([
                    # html.Li([
                        # "Lab enrollments are not included in Total, Lower, \
                        # or Upper Division calculations."]),
                    # html.Li([
                        # "Rows marked with an 'N' in the datatable are not \
                        # included in Total, Lower, or Upper Division \
                        # calculations."]),
                    # ]),
                # ],
                    # id="notes_enrollment",
                    # className="mini_container four columns",
                # ),
            ],
            style={'display': 'flex'},
            ),
        ],
            className="pretty_container twelve columns",
        ),
        ],
            className="row flex-display",
            id="calc_row",
        ),

                html.Div([
                    html.H6("Notes:"),
                    html.Ul([
                    html.Li([
                        "Lab enrollments, marked with an 'L' in the datatable, \
                        are not included in Total, Lower, \
                        or Upper Division calculations."]),
                    # html.Li([
                    #     "Rows marked with an 'N' in the datatable are not \
                    #     included in any of the calculations."]),
                    html.Li([
                        "5000 level courses are only included in the Total \
                        calculations."]),
                    ]),
                ],
                    id="notes_enrollment",
                    # className="mini_container four columns",
                ),
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=blankFigure(),
                    id="max_v_enrl_by_crn_graph"
                )
            ],
                className="pretty_container six offset-right columns",
            ),
            html.Div([
                dcc.Graph(
                    figure=blankFigure(),
                    id="max_v_enrl_by_course_graph"
                )
            ],
                className="pretty_container six offset-left columns",
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
                className="pretty_container four offset-right columns",
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
                className="pretty_container four offset-left offset-right columns",
            ),
            html.Div([
                dcc.Graph(
                    figure=blankFigure(),
                    id="graph_f2f"
                ),
                html.Label([
                    "Enrollment:",
                    dcc.RadioItems(
                        id='enrollment-max-actual',
                        options=[
                            {'label': 'Max', 'value': 'Max'},
                            {'label': 'Actual', 'value': 'Enrolled'},
                            {'label': 'Sections', 'value': 'Section'},
                        ],
                        labelStyle={'display': 'inline-block'},
                        className="dcc_control",
                        value='Max'
                    ),
                ]),
            ],
                className="pretty_container four offset-left columns",
            ),
        ],
            className="row flex-display",
        ),
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=blankFigure(),
                    id="enrl_by_instructor_graph",
                )
            ],
                className="pretty_container six offset-right columns",
            ),
            html.Div([
                dcc.Graph(
                    figure=blankFigure(),
                    id="chp_by_course_graph",
                )
            ],
                className="pretty_container six offset-left columns",
            ),
        ],
            className="row flex-display",
        ),
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='filter-query-dropdown',
                    options=[
                        {'label': 'Custom...', 'value': 'custom'},
                        {'label': 'Active Classes', 'value': '{S} contains A'},
                        {'label': 'Canceled CRNs', 'value': '{S} contains C'},
                        {'label': 'Lower Division', 'value': '{Number} < 3000 && {S} contains A'},
                        {'label': 'Upper Division', 'value': '{Number} >= 3000 && {S} contains A'},
                        {'label': "Dean's minimums", 'value': '(({Number} < 2000 && {Number} !="1080" && {Number} !="1081" && {Number} !="1082" && {Number} !="1101" && {Number} !="1110" && {Number} !="1111"  && {Number} !="1112" && {Number} !="1115" && {Number} !="1116" && {Number} !="1310" && {Number} !="1311" && {Number} !="1312") && {Credit} > 0 && {Enrolled} < 20) || ({Number} <3000 && {Number} >= 2000 && {Enrolled} < 18) || ({Number} <4000 && {Number} >= 3000 && {Enrolled} < 15) || ({Number} >= 3000 && {Enrolled} < 10)'},
                        {'label': "Provost's minimums", 'value': '(({Number} < 2000 && {Number} !="1080" && {Number} !="1081" && {Number} !="1082" && {Number} !="1101" && {Number} !="1110" && {Number} !="1111"  && {Number} !="1112" && {Number} !="1115" && {Number} !="1116" && {Number} !="1310" && {Number} !="1311" && {Number} !="1312") && {Credit} > 0 && {Enrolled} < 15) || ({Number} <3000 && {Number} >= 2000 && {Enrolled} < 15) || ({Number} <4000 && {Number} >= 3000 && {Enrolled} < 10) || ({Number} >= 3000 && {Enrolled} < 10)'},
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
        html.Div([
                html.Hr(),
                html.Div([
                    html.Button('Export All', id='export-all-button', n_clicks=0,
                                style={'marginLeft': '5px'},className='button'),
                    dcc.Download(id='datatable-download'),
                    html.Button('Export Filtered', id='export-filtered-button',n_clicks=0,
                                style={'marginLeft': '5px'},className='button'),
                    dcc.Download(id='datatable-filtered-download'),
                    html.Button('Export to Access', id='export-access-button', n_clicks=0,
                                style={'marginLeft': '5px'},className='button'),
                    dcc.Download(id='datatable-access-download'),
                    html.Button("Export Dean's Rpt", id='export-dean-button', n_clicks=0,
                                style={'marginLeft': '5px'},className='button'),
                    dcc.Download(id='datatable-dean-download'),
                ]),
        ],
            style={'width': '100%'}
        ),
        html.Div([
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
        ]),
    ],
        id='output-data-upload',
        style={'display': 'none'}),
html.Div([dcc.Input(id='report-term', placeholder='', style={'display': 'none'})]),
html.Div([dcc.Input(id='term-code', placeholder='', style={'display': 'none'})])
],
)

@app.callback(
     [Output('datatable-container', 'children'),
     Output('title-report-semester', 'children'),
     Output('stats-graph-title', 'children'),
     Output('upload-data-button', 'n_clicks'),
     Output('report-term', 'value'),
     Output('term-code', 'value')],
    Input('upload-data', 'contents'),
    [State('upload-data-button', 'n_clicks'),
     State('upload-data', 'filename')],
     # State('upload-data', 'last_modified')],
)
def initial_data_loading(contents, n_clicks, filename):#, date):
    if contents is not None and n_clicks > 0:
        df, report_term, term_code, data_date = parse_contents(contents, filename) #, date)

        # these are courses that should not be included in the calculations
        lab_courses = ('MTH 1082','MTH 1101', 'MTH 1116', 'MTH 1312')

        excluded_courses = ( 'MTL 3850', 'MTL 3858', 'MTL 4690')

        for row in df.index.to_list():
            # canceled courses
            if df.loc[row, 'S'] == 'C':
                   df.loc[row, 'Calc'] = 'N'
            # zero credit courses
            if df.loc[row, 'Credit'] == 0:
                   df.loc[row, 'Calc'] = 'N'
            # lab courses
            for course in lab_courses:
                if df.loc[row, 'Class'] == course:
                       df.loc[row, 'Calc'] = 'L'
                       break
            # omnibus or independent study courses
            if any(c.isalpha() for c in df.loc[row, 'Number']):
                df.loc[row, 'Calc'] = 'N'

            # excluded courses
            for course in excluded_courses:
                if df.loc[row, 'Class'] == course:
                       df.loc[row, 'Calc'] = 'N'
                       break

        data_children = create_datatable(df)
        title_report_semester = "Enrollment Report for " + report_term
        stats_graph_title = "Date of report: " + datetime.datetime.strftime(data_date, "%d-%b-%Y").upper()
        n_clicks = 1
    else:
        data_children = []
        report_term = ''
        term_code = ''
        stats_graph_title = ""
        n_clicks = 0
        title_report_semester = "Enrollment Report"

    datatable_container_children = [
        html.Div(
            data_children,
            style={
                'width': '100%',
                'display': 'block',
                'marginLeft': 'auto',
                'marginRight': 'auto',
            },
            id='datatable-container',
        )
    ]

    return datatable_container_children, title_report_semester, stats_graph_title, n_clicks, report_term, term_code

@app.callback(
    Output('datatable-download', 'data'),
    [Input('export-all-button', 'n_clicks'),
     Input('export-access-button', 'n_clicks'),
     Input('export-dean-button', 'n_clicks'),
     State('datatable', 'data'),
     State('report-term', 'value'),
     State('term-code', 'value')],
)
def export_all(all_n_clicks, access_n_clicks, dean_n_clicks, data, report_term, term_code):
    if DEBUG:
        print("function: export_all")
    ctx = dash.callback_context
    trigger = ''
    if ctx.triggered:
        trigger = (ctx.triggered[0]['prop_id'].split('.')[0])
    _df = pd.DataFrame(data)
    if 'export-all-button' == trigger and all_n_clicks > 0:
        return {'base64': True,
                'content': to_excel(_df, report_term),
                'filename': "SWRCGSR_{0}.xlsx".format(term_code)}
    elif 'export-access-button' == trigger and access_n_clicks > 0:
        return {'base64': True,
                'content': to_access(_df, report_term),
                'filename': "SWRCGSR_{0}.xlsx".format(term_code)}
    elif 'export-dean-button' == trigger and dean_n_clicks > 0:
        _df = labs_combined(_df)
        return {'base64': True,
                'content': to_excel_dean(_df, report_term),
                'filename': "SWRCGSR_{0}.xlsx".format(term_code)}

@app.callback(
    Output('datatable-filtered-download', 'data'),
    [Input('export-filtered-button', 'n_clicks'),
     State('datatable', 'derived_virtual_data'),
     State('report-term', 'value'),
     State('term-code', 'value')]
)
def export_filtered(n_clicks, data, report_term, term_code):
    if DEBUG:
        print("function: export_filtered")
    _df = pd.DataFrame(data)
    print(_df)
    if n_clicks > 0:
        return {'base64': True,
                'content': to_excel(_df, report_term),
                'filename': "SWRCGSR_{0}.xlsx".format(term_code)}

@app.callback(
    Output('output-data-upload', 'style'),
    Input('upload-data-button', 'n_clicks')
)
def show_contents(n_clicks):
    if n_clicks > 0:
        return {'display': 'block'}
    return {'display': 'none'}

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
    # return input_style, output_style , html.P('filter_query = "{}"'.format(val)),

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
    # if n_clicks > 0 or n_submit > 0:
    if n_clicks or n_submit:
        if dropdown_value == 'custom':
            return [input_value]
        else:
            if dropdown_value is None:
                return ['']
            return [dropdown_value]


@app.callback(
    Output('max_v_enrl_by_crn_graph', 'figure'),
    Input('datatable', 'derived_viewport_data'),
    State('max_v_enrl_by_crn_graph', 'figure'),
)
def max_v_enrl_by_crn(data, fig):
    if data:
        df = pd.DataFrame(data).copy()
        df = df[df["Credit"] != 0]

        return (
            px.bar(
                df,
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
    Output('calc_row', 'children'),
    Input('datatable', 'derived_viewport_data'),
    Input('datatable', 'data'),
    State('calc_row', 'children'),
)
def calc_row(derived_data, data, children):
    if derived_data:
        df = pd.DataFrame(derived_data)
        df_all = pd.DataFrame(data)
        return create_calc_row_layout(df, df_all)
    else:
        return children

@app.callback(
    Output('max_v_enrl_by_course_graph', 'figure'),
    Input('datatable', 'derived_viewport_data'),
    State('max_v_enrl_by_course_graph', 'figure'),
)
def max_v_enrl_by_course(data, fig):
    if data:
        df = pd.DataFrame(data).copy()
        df = df[df["Credit"] != 0]
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
                color_discrete_map = {"Max": '#00447c', "Enrolled": '#d11242'},
                title="Enrollment per Course",
                hover_data={"Ratio": ':0.1f', "WList": True},
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
    [Input('datatable', 'derived_viewport_data'),
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

@app.callback(
    Output('enrl_by_instructor_graph', 'figure'),
    Input('datatable', 'derived_viewport_data'),
    State('enrl_by_instructor_graph', 'figure'),
)
def graph_enrollment_by_instructor(data, fig):
    if data:
        df = pd.DataFrame(data).copy()
        df = df[df["Credit"] != 0]
        return (
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
    else:
        return fig

@app.callback(
    Output('chp_by_course_graph', 'figure'),
    Input('datatable', 'derived_viewport_data'),
    State('chp_by_course_graph', 'figure'),
)
def chp_by_course_callback(data, fig):
    if data:
        df = pd.DataFrame(data).copy()
        df = df[df["Credit"] != 0]
        return (
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
    else:
        return fig

@app.callback(
    Output('enrl_by_instructor', 'children'),
    Input('datatable', 'derived_viewport_data'),
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
    Input('datatable', 'derived_viewport_data'),
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
    [Output("total_sections_text", "children"),
     Output("total_courses_text", "children"),
     Output("total_CHP_text", "children"),
     Output("avg_enrollment_text", "children"),
     Output("avg_fill_rate_text", "children"),
     Output("avg_enrollment_by_instructor_text", "children"),
     Output("avg_waitlist_text", "children"),
    ],
    Input('datatable', 'derived_viewport_data'),
)
def update_stats(data):
    if data:
        df = pd.DataFrame(data).copy()
        df = df[df["Credit"] != 0]

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



# Main
if __name__ == "__main__":
    if mathserver:
        app.run_server(debug=DEBUG)
    else:
        # app.run_server(debug=True, host='10.0.2.15', port='8050')
        app.run_server(debug=DEBUG, port='8050')

