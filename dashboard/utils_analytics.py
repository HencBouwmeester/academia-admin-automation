# Import required libraries
import dash
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash import dash_table, html, dcc
import plotly.graph_objects as go
import numpy as np
import base64
import io
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import datetime

import re

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
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
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
        df = df[df['S'] == 'A'].copy()
        df.loc[:,'DaysTimeLoc'] = df['Days'] +  df['Time'] + df['Loc']

        if category == 'Lab':
            df = df[df['Calc'] == 'L']

            sections = df["CRN"].nunique()
            courses = df["Course"].nunique()
            waitlist = df['WLst'].sum()
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
            lab_courses = df_labs["Course"].nunique()

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
                courses = df["Course"].nunique() - lab_courses
                waitlist = df['WLst'].sum()

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
            lab_courses = df_labs["Course"].nunique()

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
                courses = df["Course"].nunique() - lab_courses
                waitlist = df['WLst'].sum()
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
                    df.loc[row_p, 'WLst'] += df.loc[row_l, 'WLst']

                    # recalculate the CHP and Ratio
                    df.loc[row_p, 'CHP'] = df.loc[row_p, 'Credit'] * df.loc[row_p, 'Enrolled']
                    df.loc[row_p, 'Ratio'] = 100 * df.loc[row_p, 'Enrolled'] / df.loc[row_p, 'Max']

    # remove the lab sections from the data
    for lab in parent_lab.values():
        mask = df[df['Number'] != lab].index.to_list()
        df = df.loc[mask]
        # df.drop(df[df['Number'] == lab].index, inplace=True)

    return df

