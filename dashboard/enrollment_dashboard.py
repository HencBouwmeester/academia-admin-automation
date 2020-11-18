# -*- coding: utf-8 -*-

# Import required libraries
import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.io as pio
import dash_table
import dash_table.FormatTemplate as FormatTemplate
import numpy as np
import base64
import io
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Include pretty graph formatting
pio.templates.default = "plotly_white"
# expects 'assets' folder with styling CSS and resizing js
# CSS from: https://github.com/plotly/dash-sample-apps/tree/master/apps/dashr-oil-and-gas/assets

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


# Helper Functions
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

    _df = pd.read_fwf(file_contents, colspecs=_LINE_PATTERN)

    # read the report Term and Year from file
    term_code = str(_df.iloc[5][1])[3:] + str(_df.iloc[5][2])[:-2]

    _df.columns = _df.iloc[7]
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

    return _df, term_code

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

# Data wrapper class
class EnrollmentData:
    """ Encapsulate a dataframe with helpful accessors for summary statistics and graphs """

    def __init__(self, df, term_code):

        if not df.empty:
            # convert time from 12hr to 24hr
            df["Time"] = df["Time"].apply(lambda x: convertAMPMtime(x))

            # fill Nan with zeros
            df["Enrolled"] = df["Enrolled"].fillna(0)
            df["Rcap"] = df["Rcap"].fillna(0)
            df["Full"] = df["Full"].fillna(0)

            # Helper columns
            df.loc[:, "CHP"] = df["Credit"] * df["Enrolled"]
            df.loc[:, "Course"] = df["Subject"] + df["Number"]
            df.loc[:, "Ratio"] = df["Enrolled"] / df["Max"]

            self.df_raw = df
            self.df = df[df["S"] == "A"]  # keep only active classes

            self.term_code = term_code
            if term_code[-2:] == "30":
                self.report_term = "Spring " + term_code[0:4]
            elif term_code[-2:] == "40":
                self.report_term = "Summer " + term_code[0:4]
            elif term_code[-2:] == "50":
                self.report_term = "Fall " + term_code[0:4]

    # Calculate Stats and Graphs
    def total_sections(self):
        try:
            return self.df["CRN"].nunique()
        except AttributeError:
            return 0

    def avg_enrollment(self):
        try:
            return round(self.df["Enrolled"].mean(), 2)
        except AttributeError:
            return 0.00

    def total_CHP(self):
        try:
            return self.df["CHP"].sum()
        except AttributeError:
            return 0.00

    def enrollment_by_instructor(self):
        try:
            _df = (
                self.df.groupby("Instructor")
                .agg(enrl_sum=("Enrolled", "sum"), enrl_avg=("Enrolled", "mean"))
                .rename(columns={"enrl_sum":"Total", "enrl_avg":"Avg"})
                .sort_values(("Instructor"), ascending=True)
                .reset_index()
            )
            _df["Avg"] = _df["Avg"].round(2)
            return _df
        except AttributeError:
            return pd.DataFrame()

    def credits_by_instructor(self):
        try:
            return (
                self.df.groupby("Instructor")
                .agg({"Credit": "sum"})
                .sort_values(("Credit"), ascending=False)
                .reset_index()
            )
        except AttributeError:
            return pd.DataFrame()

    def chp_by_course(self):
        try:
            return (
                self.df.groupby("Course")
                .agg({"CHP": "sum", "Enrolled": "sum", "Max": "sum"})
                .sort_values(("Course"), ascending=True)
                .reset_index()
            )
        except AttributeError:
            return pd.DataFrame()

    def avg_fill_rate(self):
        try:
            return round(self.df["Ratio"].mean(), 2)
        except AttributeError:
            return 0.00

    def courses_over_85_percent(self):
        try:
            return self.df[self.df["Ratio"] >= 0.85].loc[
                :, ["Course", "Enrolled", "Max", "Days", "Time", "Instructor"]
            ]
        except AttributeError:
            return pd.DataFrame()

    def courses_under_40_percent(self):
        try:
            return self.df[self.df["Ratio"] <= 0.40].loc[
                :, ["Course", "Enrolled", "Max", "Days", "Time", "Instructor"]
            ]
        except AttributeError:
            return pd.DataFrame()

    def courses_under_13_enrolled(self):
        try:
            return self.df[self.df["Enrolled"] < 13].loc[
                :, ["Course", "Enrolled", "Max", "Days", "Time", "Instructor"]
            ]
        except AttributeError:
            return pd.DataFrame()

    def courses_with_waitlists(self):
        try:
            return self.df[self.df["WList"] > 0].loc[
                :, ["Course", "Enrolled", "WList", "Max", "Days", "Time", "Instructor"]
            ]
        except AttributeError:
            return pd.DataFrame()

    def average_waitlist(self):
        try:
            return round(self.df["WList"].mean(), 2)
        except AttributeError:
            return 0.00

    def avg_enrollment_by_instructor(self):
        try:
            return round(
                self.df.groupby("Instructor").agg({"Enrolled": "sum"}).values.mean(), 2
            )
        except AttributeError:
            return 0.00

    # Face to Face vs Online
    def f2f_df(self):
        _df = self.df.groupby("Loc").sum()
        _df.reset_index(inplace=True)
        _df2 = _df[
            (_df["Loc"] != "SYNC  T")
            & (_df["Loc"] != "ASYN  T")
            & (_df["Loc"] != "ONLI  T")
        ]
        _df3 = pd.DataFrame(_df2.sum(axis=0)).T
        _df3.iloc[0, 0] = "F2F"
        f2f_df = pd.concat(
            [
                _df[_df["Loc"] == "ASYN  T"],
                _df[_df["Loc"] == "SYNC  T"],
                _df[_df["Loc"] == "ONLI  T"],
                _df3,
            ]
        )
        f2f_df.reset_index(drop=True)
        return f2f_df

    def f2f_df2(self):
        _df = self.df.groupby("Loc").sum()
        _df.reset_index(inplace=True)
        _df2 = _df[
            (_df["Loc"] != "SYNC  T")
            & (_df["Loc"] != "ASYN  T")
            & (_df["Loc"] != "ONLI  T")
        ]
        _df3 = pd.DataFrame(_df2.sum(axis=0)).T
        _df3.iloc[0, 0] = "F2F"
        _df4 = _df[
            (_df["Loc"] == "SYNC  T")
            | (_df["Loc"] == "ASYN  T")
            | (_df["Loc"] != "ONLI  T")
        ]
        _df5 = pd.DataFrame(_df4.sum(axis=0)).T
        _df5.iloc[0, 0] = "Online"
        f2f_df2 = pd.concat([_df3, _df5])
        f2f_df2.reset_index(drop=True)
        return f2f_df2

    def percent_f2f(self):
        try:
            _a = self.f2f_df2()[self.f2f_df2()["Loc"] == "F2F"].CHP.values[0]
            _b = self.f2f_df2()[self.f2f_df2()["Loc"] == "Online"].CHP.values[0]
            d = _a + _b
            if d != 0:
                return round(_a / (_a + _b), 2)
            else:
                return 0.00
        except AttributeError:
            return 0.00

    def full_f2f_df(self):
        full_f2f_df = self.df.groupby("Loc").sum()
        full_f2f_df.reset_index(inplace=True)
        full_f2f_df
        full_f2f_df["Online"] = np.where(
            full_f2f_df["Loc"].isin(["ASYN  T", "SYNC  T", "ONLI  T"]), "Online", "F2F"
        )
        return full_f2f_df

    def enrolled_vs_max(self):
        return self.df.loc[
            :, ["Course", "Ratio", "Enrolled", "Max", "Days", "Time", "Instructor"]
        ].sort_values(by=["Max", "Enrolled", "Ratio"], axis=0, ascending=False)


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

    # Prepare graphs
    def graph_enrollment_by_instructor(self):
        try:
            return (
                px.bar(
                    self.df,
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
        except AttributeError:
            return self.blankFigure

    def graph_chp_by_course(self):
        try:
            return (
                px.bar(
                    self.df,
                    x="Course",
                    y="CHP",
                    title="Credit Hour Production by Course",
                    color="Ratio",
                    color_continuous_scale=px.colors.sequential.RdBu,
                )
                .update_xaxes(categoryorder="category descending")
                .update_layout(showlegend=False)
            )
        except AttributeError:
            return self.blankFigure

    def graph_chp_by_course_treemap(self):
        return px.treemap(
            self.df,
            path=["Subject", "Course", "CRN"],
            values="CHP",
            color="Ratio",
            title="Credit Hour Production",
        )

    def graph_f2f(self, toggle):
        try:
            _df = self.df[["Loc", toggle]]
            _df = _df.groupby("Loc", as_index=False).sum()
            t = _df[toggle].sum()
            o = _df[_df["Loc"].isin(["ASYN  T", "SYNC  T", "ONLI  T"])][toggle].sum()
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
        except AttributeError:
            return self.blankFigure

    def graph_ratio_course(self):
        try:
            _df = (
                self.df.groupby("Course")
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
        except AttributeError:
            return self.blankFigure

    def graph_ratio_crn(self):
        try:
            return (
                px.bar(
                    self.df,
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
        except AttributeError:
            return self.blankFigure

    # Output Excel files
    def to_excel(self):
        _df = self.df.copy()
        xlsx_io = io.BytesIO()
        writer = pd.ExcelWriter(
            xlsx_io, engine="xlsxwriter", options={"strings_to_numbers": True}
        )
        _df["Section"] = _df["Section"].apply(lambda x: '="{x:s}"'.format(x=x))
        _df["Number"] = _df["Number"].apply(lambda x: '="{x:s}"'.format(x=x))
        _df.to_excel(writer, sheet_name="Enrollment", index=False)

        workbook = writer.book
        worksheet = writer.sheets["Enrollment"]

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

        # New sheets
        worksheet2 = workbook.add_worksheet("Statistics")
        worksheet3 = workbook.add_worksheet("Data")

        # Add stats
        worksheet2.set_column("A:A", 25)

        worksheet2.write(0, 0, "Summary Statistics", bold)
        worksheet2.write(1, 0, "Average Fill Rate")
        try:
            worksheet2.write(1, 1, round(_df["Ratio"].mean(), 2))
        except (KeyError, TypeError):
            worksheet2.write(1, 1, 0.0)

        worksheet2.write(3, 0, "Total Sections")
        worksheet2.write(3, 1, _df["CRN"].nunique())

        worksheet2.write(5, 0, "Average Enrollment per Section")
        try:
            worksheet2.write(5, 1, round(_df["Enrolled"].mean(), 2))
        except (KeyError, TypeError):
            worksheet2.write(5, 1, 0.0)

        worksheet2.write(7, 0, "Credit Hour Production")
        worksheet2.write(7, 1, _df["CHP"].sum())

        worksheet2.write(9, 0, "Percent F2F Classes")
        try:
            worksheet2.write(9, 1, self.percent_f2f())
        except (KeyError, TypeError):
            worksheet2.write(9, 1, 0.0)

        # Enrollment Chart
        chart = workbook.add_chart({"type": "column", "subtype": "stacked"})

        chart_data = (
            _df.groupby("Course")
            .agg({"Enrolled": "sum", "Max": "sum"})
            .sort_values("Course", ascending=True)
        )

        data = chart_data.reset_index().T.values.tolist()

        worksheet3.write_column("A1", data[0])
        worksheet3.write_column("B1", data[1])
        worksheet3.write_column("C1", data[2])

        chart.add_series(
            {
                "categories": ["Data", 0, 0, len(data[0]), 0],
                "values": ["Data", 0, 2, len(data[0]), 2],
                "fill": {"color": "blue", "transparency": 50},
            }
        )
        chart.add_series(
            {
                "categories": ["Data", 0, 0, len(data[0]), 0],
                "values": ["Data", 0, 1, len(data[0]), 1],
                "y2_axis": 1,
                "fill": {"color": "red", "transparency": 50},
            }
        )

        chart.set_size({"x_scale": 2, "y_scale": 1.5})

        chart.set_title({"name": "Enrollment by Course"})
        chart.set_legend({"none": True})
        chart.set_y_axis(
            {"name": "Students", "min": 0, "max": chart_data.max().max() + 50}
        )

        chart.set_y2_axis(
            {"visible": False, "min": 0, "max": chart_data.max().max() + 50}
        )

        worksheet2.insert_chart("D2", chart)

        # Online vs F2F chart
        chart2 = workbook.add_chart({"type": "column", "subtype": "stacked"})

        _one = (
            self.full_f2f_df()[["Loc", "Online", "CHP"]]
            .pivot(index="Loc", columns="Online", values="CHP")
            .reset_index()
        )
        _two = pd.DataFrame(_one.columns.to_numpy())
        _three = _two.T.rename(columns={0: "Loc", 1: "F2F", 2: "Online"})
        data2 = pd.concat([_three, _one]).fillna(0).T.values.tolist()

        worksheet3.write_column("D1", data2[0])
        worksheet3.write_column("E1", data2[1])

        try:
            worksheet3.write_column("F1", data2[2])
        except (KeyError, TypeError):
            data2.append(["Online", *(len(data2[1]) - 1) * [0]])
            worksheet3.write_column("F1", data2[2])

        for i in range(len(data2[0]) - 1):
            chart2.add_series(
                {
                    "name": ["Data", i, 3],
                    "categories": ["Data", 0, 4, 0, 5],
                    "values": ["Data", i + 1, 4, i + 1, 5],
                }
            )

        chart2.set_size({"x_scale": 2, "y_scale": 1.5})

        chart2.set_title({"name": "Online vs F2F"})
        # chart.set_legend({'none': True})
        chart2.set_y_axis({"name": "CHP"})

        worksheet2.insert_chart("D25", chart2)

        # Save it
        writer.save()
        xlsx_io.seek(0)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        data = base64.b64encode(xlsx_io.read()).decode("utf-8")
        return f"data:{media_type};base64,{data}"


# Create app layout
app.layout = html.Div(  # div-lvl-1
    [
        dcc.Store(id="aggregate_data"),  # div-lvl-2
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),  # div-lvl-2
        html.Div(  # div-lvl-2
            [
                html.Div(  # div-lvl-2
                    [
                        # Blank padding
                    ],
                    className="one-third column",
                ),
                html.Div(  # div-lvl-2
                    [
                        html.Div(  # div-lvl-3
                            [
                                html.H3(
                                    "SWRCGSR Enrollment",
                                    id="report-semester",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Statistics and Graphs", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(  # div-lvl-2
                    [
                        dcc.Upload(  # div-lvl-3
                            id="upload-data",
                            children=html.Div(
                                ["Drag and Drop or ", html.A("Select Files")]
                            ),
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px",
                            },
                            multiple=True,
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(id="output-data-upload"),  # div-lvl-2, where data gets inserted
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


def parse_contents(contents, filename, date):
    """Assess filetype of uploaded file and pass to appropriate processing functions,
    then return html of enrollment statistics.

    Args:
        contents: the encoded file contents
        filename: the filename
        date: the timestamp

    Returns:
        html Div element containing statistics and dash graphs."""

    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "txt" in filename:
            # Assume that the user uploaded a banner fixed width file with .txt extension
            # Load data
            df, term_code = tidy_txt(io.StringIO(decoded.decode("utf-8")))
        elif "csv" in filename:
            # Assume the user uploaded a banner Shift-F1 export quasi-csv file with .csv extension
            df, term_code = tidy_csv(io.StringIO(decoded.decode("utf-8")))
        # TODO: elif "xls" in filename:
        #     # Assume that the user uploaded a pre-processed excel file from this program
        #     df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    data = EnrollmentData(df, term_code)

    return html.Div(  # div-lvl-3 is outermost of return
        [
            html.Div(  # div-lvl-4, first row: download link
                [
                    html.Div(  # div-lvl-5
                        [
                            # Blank padding
                        ],
                        className="one-third column",
                    ),
                    html.Div(  # div-lvl-5
                        [
                            html.Div(  # div-lvl-6
                                [
                                    html.H5(
                                        "Excel Formatted Output for {0}".format(
                                        data.report_term
                                        ),
                                        style={
                                            "margin-bottom": "0px",
                                            "text-align": "center",
                                        },
                                    ),
                                    html.A(
                                        "Download Excel Data",
                                        id="excel-download",
                                        download="SWRCGSR_{0}.xlsx".format(
                                            data.term_code
                                        ),
                                        href=data.to_excel(),
                                        target="_blank",
                                    ),
                                ],
                                style={"text-align": "center"},
                            )
                        ],
                        className="one-half column",
                        id="download",
                    ),
                    html.Div(  # div-lvl-5
                        [
                            # Blank padding
                        ],
                        className="one-third column",
                    ),
                ],
                id="header",
                className="row flex-display",
                style={"margin-bottom": "25px"},
            ),
            html.Div(  # div-lvl-4, second row: statistics
                [
                    html.Div(  # div-lvl-5
                        [
                            html.H6(
                                f"{data.total_sections()}", id="total_sections_text"
                            ),
                            html.P("Total Sections"),
                        ],
                        id="sections",
                        className="mini_container",
                    ),
                    html.Div(  # div-lvl-5
                        [
                            html.H6(
                                f"{data.avg_enrollment()}", id="avg_enrollment_text"
                            ),
                            html.P("Average Enrollment by Section"),
                        ],
                        id="avg_enrollment",
                        className="mini_container",
                    ),
                    html.Div(  # div-lvl-5
                        [
                            html.H6(f"{data.total_CHP()}", id="total_CHP_text"),
                            html.P("Total Credit Hour Production"),
                        ],
                        id="total_CHP",
                        className="mini_container",
                    ),
                    html.Div(  # div-lvl-5
                        [
                            html.H6(f"{data.avg_fill_rate()}", id="avg_fill_rate_text"),
                            html.P("Average Fill Rate"),
                        ],
                        id="avg_fill_rate",
                        className="mini_container",
                    ),
                    html.Div(  # div-lvl-5
                        [
                            html.H6(
                                f"{data.avg_enrollment_by_instructor()}",
                                id="avg_enrollment_by_instructor_text",
                            ),
                            html.P("Average Enrollment per Instructor"),
                        ],
                        id="avg_enrollment_by_instructor",
                        className="mini_container",
                    ),
                    html.Div(  # div-lvl-5
                        [
                            html.H6(
                                f"{data.average_waitlist()}", id="avg_waitlist_text"
                            ),
                            html.P("Average Waitlist"),
                        ],
                        id="avg_waitlist",
                        className="mini_container",
                    ),
                    html.Div(  # div-lvl-5
                        [
                            html.H6(f"{data.percent_f2f()}", id="percent_f2f_text"),
                            html.P("Percent F2F Classes"),
                        ],
                        id="percent_f2f",
                        className="mini_container",
                    ),
                ],
                className="row container-display",
            ),
            html.Div(  # div-lvl-4, third row: graphs
                [
                    html.Div(  # div-lvl-5
                        [
                            dcc.Graph(
                                figure=data.graph_ratio_crn(),
                                id="main_graph"
                            )
                        ],
                             id = "main_graph_div",
                             className="pretty_container six columns",
                    ),
                    html.Div(  # div-lvl-5
                        [
                            dcc.Graph(
                              figure=data.graph_ratio_course(),
                              id="main_graph_2"
                            )
                        ],
                        className="pretty_container six columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(  # div-lvl-4, fourth row: lists and graphs
                [
                    html.Div(  # div-lvl-5
                        [
                            html.H6(
                                "Enrollment by Instructor",
                                id="enrollment_by_instructor_id",
                            ),
                            dash_table.DataTable(  # div-lvl-6
                                id="enrollment_data_table",
                                columns=[
                                    {"name": i, "id": i}
                                    for i in data.enrollment_by_instructor().columns
                                ],
                                data=data.enrollment_by_instructor().to_dict("records"),
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
                                        'minWidth': '140px', 'width': '140px', 'maxWidth': '140px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Total'},
                                        'minWidth': '60px', 'width': '60px', 'maxWidth': '60px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Avg'},
                                        'minWidth': '60px', 'width': '60px', 'maxWidth': '60px',
                                        'whiteSpace': 'normal'
                                    },
                                ]
                            ),
                        ],
                        className="pretty_container one-third column",
                    ),
                    html.Div(  # div-lvl-5
                        [
                            html.H6("Course CHP and Enrollment", id="chp_by_course_id"),
                            dash_table.DataTable(  # div-lvl-6
                                id="chp_by_course_data_table",
                                columns=[
                                    {"name": i, "id": i}
                                    for i in data.chp_by_course().columns
                                ],
                                data=data.chp_by_course().to_dict("records"),
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
                                        'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'CHP'},
                                        'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Enrolled'},
                                        'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Max'},
                                        'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
                                        'whiteSpace': 'normal'
                                    },
                                ]
                            ),
                        ],
                        className="pretty_container one-third column",
                    ),
                    html.Div(  # div-lvl-5
                             [
                                 dcc.Graph(figure=data.graph_f2f("Max"), id="graph_f2f"),
                                 html.B("Enrollment:"),
                                 dcc.RadioItems(
                                     id='enrollment-max-actual',
                                     options=[
                                         {'label': 'Max', 'value': 'Max'},
                                         {'label': 'Actual', 'value': 'Enrolled'}
                                     ],
                                     labelStyle={'display': 'inline-block'},
                                     value='Max'
                                 ),
                             ],
                        className="pretty_container one-third column",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(  # div-lvl-4, sixth row: graphs
                [
                    html.Div(  # div-lvl-5
                        [
                            dcc.Graph(  # div-lvl-6
                                figure=data.graph_enrollment_by_instructor(),
                                id="individual_graph",
                            )
                        ],
                        className="pretty_container six columns",
                    ),
                    html.Div(  # div-lvl-5
                        [
                            dcc.Graph(  # div-lvl-6
                                figure=data.graph_chp_by_course(),
                                id="individual_graph_2",
                            )
                        ],
                        className="pretty_container six columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(  # div-lvl-4, seventh row: datatable
                [
                    html.Div(  # div-lvl-5
                        [
                            dcc.RadioItems(
                                id='filter-query-read-write',
                                options=[
                                    {'label': 'Read filter_query', 'value': 'read'},
                                    {'label': 'Write to filter_query', 'value': 'write'}
                                ],
                                value='read'
                            ),

                            html.Br(),

                            dcc.Input(id='filter-query-input', placeholder='Enter filter query'),

                            html.Div(id='filter-query-output'),

                            html.Hr(),

                            dash_table.DataTable(  # div-lvl-6
                                id="datatable-filtering",
                                columns=[
                                    {"name": "CRN", "id": "CRN", "type": "numeric"},
                                    {"name": "Course", "id": "Course", "type": "text"},
                                    { "name": "Section", "id": "Section", "type": "text", },
                                    {"name": "Title", "id": "Title", "type": "text"},
                                    {"name": "Credit", "id": "Credit", "type": "text"},
                                    {"name": "Status", "id": "S", "type": "text"},
                                    {"name": "Days", "id": "Days", "type": "text"},
                                    {"name": "Time", "id": "Time", "type": "text"},
                                    {"name": "Loc", "id": "Loc", "type": "text"},
                                    {"name": "Campus", "id": "Campus", "type": "text"},
                                    {"name": "Max", "id": "Max", "type": "numeric"},
                                    {"name": "Enrld", "id": "Enrolled", "type": "numeric", },
                                    {"name": "CHP", "id": "CHP", "type": "numeric"},
                                    {
                                        "name": "Ratio",
                                        "id": "Ratio",
                                        "type": "numeric",
                                        "format": FormatTemplate.percentage(1),
                                    },
                                    { "name": "Instructor", "id": "Instructor", "type": "text", },
                                ],
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': 'CRN'},
                                        'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Course'},
                                        'textAlign': 'right',
                                        'minWidth': '90px', 'width': '90px', 'maxWidth': '90px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Section'},
                                        'textAlign': 'left',
                                        'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Title'},
                                        'textAlign': 'left',
                                        'minWidth': '140px', 'width': '140px', 'maxWidth': '140px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Credit'},
                                        'minWidth': '70px', 'width': '70px', 'maxWidth': '70px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'S'},
                                        'textAlign': 'center',
                                        'minWidth': '70px', 'width': '70px', 'maxWidth': '70px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Days'},
                                        'minWidth': '60px', 'width': '60px', 'maxWidth': '60px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Time'},
                                        'textAlign': 'center',
                                        'minWidth': '120px', 'width': '120px', 'maxWidth': '120px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Loc'},
                                        'textAlign': 'center',
                                        'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Campus'},
                                        'textAlign': 'center',
                                        'minWidth': '75px', 'width': '75px', 'maxWidth': '75px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Max'},
                                        'minWidth': '55px', 'width': '55px', 'maxWidth': '55px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Enrolled'},
                                        'minWidth': '60px', 'width': '60px', 'maxWidth': '60px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Ratio'},
                                        'minWidth': '65px', 'width': '65px', 'maxWidth': '65px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'CHP'},
                                        'minWidth': '55px', 'width': '55px', 'maxWidth': '55px',
                                        'whiteSpace': 'normal'
                                    },
                                    {
                                        'if': {'column_id': 'Instructor'},
                                        'textAlign': 'left',
                                        'minWidth': '140px', 'width': '140px', 'maxWidth': '140px',
                                        'whiteSpace': 'normal'
                                    },
                                ],
                                data=data.df.to_dict("records"),
                                # data=data.df_raw.to_dict("records"),
                                # editable=True,
                                page_action="native",
                                sort_action="native",
                                filter_action="native",
                                fixed_rows={"headers": True, "data": 0},
                                style_table={
                                    "overflowX": "scroll",
                                    "maxHeight": "600px",
                                },
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
                                style_cell={"font-family": "sans-serif"},
                            ),
                            html.Hr(),
                            html.Div(id='datatable-query-structure', style={'whitespace': 'pre'})
                        ],
                        className="pretty_container twelve columns",
                    )
                ],
                className="row flex-display",
            ),
        ],
        id = "outer_most",
    )


@app.callback(
    Output("output-data-upload", "children"),
    [Input("upload-data", "contents")],
    [State("upload-data", "filename"), State("upload-data", "last_modified")],
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    """When files are selected, call parse-contents and return the new html elements."""

    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d)
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]
        return children

@app.callback(
    [
        Output('main_graph', "figure"),
        Output('total_sections_text', "children"),
        Output('avg_enrollment_text', "children"),
        Output('total_CHP_text', "children"),
        Output('avg_fill_rate_text', "children"),
        Output('avg_enrollment_by_instructor_text', "children"),
        Output('avg_waitlist_text', "children"),
        Output('percent_f2f_text', "children"),
        Output('individual_graph', "figure"),
        Output('enrollment_data_table', "data"),
        Output('chp_by_course_data_table', "data"),
        Output('graph_f2f', "figure"),
        Output('main_graph_2', "figure"),
        Output('individual_graph_2', "figure"),
    ],
    [
        Input('datatable-filtering', "derived_viewport_data"),
        Input('excel-download', 'download'),
        Input('enrollment-max-actual', 'value'),
    ],
    [
        State('main_graph', "figure"),
        State('total_sections_text', "children"),
        State('avg_enrollment_text', "children"),
        State('total_CHP_text', "children"),
        State('avg_fill_rate_text', "children"),
        State('avg_enrollment_by_instructor_text', "children"),
        State('avg_waitlist_text', "children"),
        State('percent_f2f_text', "children"),
        State('individual_graph', "figure"),
        State('enrollment_data_table', "data"),
        State('chp_by_course_data_table', "data"),
        State('graph_f2f', "figure"),
        State('main_graph_2', "figure"),
        State('individual_graph_2', "figure"),
    ],
)
def update_after_filter(filtered_data, term_code, toggle,
                main_graph_fig,
                total_sections_text,
                avg_enrollment_text,
                total_CHP_text,
                avg_fill_rate_text,
                avg_enrollment_by_instructor_text,
                avg_waitlist_text,
                percent_f2f_text,
                individual_graph_fig,
                enrollment_data_table,
                chp_by_course_data_table,
                graph_f2f_fig,
                main_graph_2_fig,
                individual_graph_2_fig,
               ):
    if filtered_data is not None:
        df = pd.DataFrame(filtered_data)
        data = EnrollmentData(df, term_code[8:14])
        main_graph_fig = data.graph_ratio_crn()
        individual_graph_fig = data.graph_enrollment_by_instructor()

        graph_f2f_fig = data.graph_f2f(toggle)
        main_graph_2_fig = data.graph_ratio_course()
        individual_graph_2_fig = data.graph_chp_by_course()

        return [
            main_graph_fig,
            f"{data.total_sections()}",
            f"{data.avg_enrollment()}",
            f"{data.total_CHP()}",
            f"{data.avg_fill_rate()}",
            f"{data.avg_enrollment_by_instructor()}",
            f"{data.average_waitlist()}",
            f"{data.percent_f2f()}",
            individual_graph_fig,
            data.enrollment_by_instructor().to_dict("records"),
            data.chp_by_course().to_dict("records"),
            graph_f2f_fig,
            main_graph_2_fig,
            individual_graph_2_fig,
        ]
    else:
        return [
            main_graph_fig,
            total_sections_text,
            avg_enrollment_text,
            total_CHP_text,
            avg_fill_rate_text,
            avg_enrollment_by_instructor_text,
            avg_waitlist_text,
            percent_f2f_text,
            individual_graph_fig,
            enrollment_data_table,
            chp_by_course_data_table,
            graph_f2f_fig,
            main_graph_2_fig,
            individual_graph_2_fig,
        ]

@app.callback(
    [Output('filter-query-input', 'style'),
     Output('filter-query-output', 'style')],
    [Input('filter-query-read-write', 'value')]
)
def query_input_output(val):
    input_style = {'width': '100%'}
    output_style = {}
    if val == 'read':
        input_style.update(display='none')
        output_style.update(display='inline-block')
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
    return dcc.Markdown('`filter_query = "{}"`'.format(query))


# Main
if __name__ == "__main__":
    # app.run_server(debug=True, host='172.16.0.153')
    app.run_server(debug=True)
