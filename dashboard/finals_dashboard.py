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
       'url_base_pathname':'/finals/',
       'routes_pathname_prefix':'/finals/',
       'requests_pathname_prefix':'/finals/',
    })

def create_time(row):
    return row['Start Time'][:-3].replace(':','').zfill(4) + '-' + row['End Time'][:-3].replace(':','').zfill(4) + row['End Time'][-2:]

def find_day(row):
    try:
        day_str = datetime.datetime.strptime(row['Date'][:-4], '%m/%d/%Y').strftime('%A')
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
        print(row)#['Date'])

    return Days

def correct_date(row):
    return row['Date'][:-4]

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

df_grid = pd.DataFrame({'Credit': finals_grid[::7], 'Meetings': finals_grid[1::7],
                        'Class_Days': finals_grid[2::7], 'Class_Start': finals_grid[3::7],
                        'Class_End': finals_grid[4::7], 'Final_Day': finals_grid[5::7],
                        'Final_Time': finals_grid[6::7]})
df_grid['Class_Start'] = df_grid['Class_Start'].apply(lambda x: convertAMPMtime_grid(x))
df_grid['Class_End'] = df_grid['Class_End'].apply(lambda x: convertAMPMtime_grid(x))

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
    _df.drop(['T', 'WCap', 'WList', 'Rcap', 'Full'], axis=1, inplace=True)

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

def parse_finals_xlsx(contents, CRNs):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded),
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
    df = df[['CRN', 'Days', 'Time', 'Loc', 'Date']]

    df['Time'] = df['Time'].apply(lambda x: convertAMPMtime(x))

    df = pd.merge(pd.DataFrame({'CRN': CRNs}), df, how="left", on="CRN")
    df = df[df['Date'].notna()]

    df.drop_duplicates(inplace=True)
    return df


def parse_finals_csv(contents, CRNs):

    # subjects: list of subjects from enrollment report

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

        fields = [field.replace('"','') for field in line.split(',')]

        # only pick up classes for CRN listed in enrollment report
        try:
            CRN = fields[1].split(' ')[1]
            if CRN in CRNs:
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
        except IndexError:
            pass

    df = pd.DataFrame(rows, columns=['CRN', 'Days', 'Time', 'Loc', 'Date'])
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
        if d.iloc[0, 3] not in r['Room'].tolist():
            indexFilter.append(row)
    return indexFilter

def final_room_capacity(e, f, room_capacities):
    indexFilter = []
    for row in e.index.tolist():
        CRN = e.loc[row, 'CRN']
        room = f[f['CRN'] == CRN]['Loc'].iloc[0]
        if e.loc[row, 'Enrolled'] > int(room_capacities[room]):
            indexFilter.append(row)
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
        ],
            id='tab-contents',
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
                'Download',
                id='download-button',
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
    ctx = dash.callback_context
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
     Output('datatable-grid-div', 'style'),],
    [Input('table-tabs', 'value')],
)
def update_tab_display(tab):
    if DEBUG:
        print("function: update_tab_display")
    ctx = dash.callback_context
    if 'table-tabs' in ctx.triggered[0]['prop_id']:
        styles = []
        for t in ['tab-combined', 'tab-enrollment', 'tab-finals', 'tab-rooms', 'tab-grid']:
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
            # capcaity is the largest of max or enrolled
            capacities.append(max(
                df_enrollment[(df_enrollment['Loc']==room)]['Max'].max(),
                df_enrollment[(df_enrollment['Loc']==room)]['Enrolled'].max()
            )
            )

        df_rooms = pd.DataFrame({'Room': rooms, 'Cap': capacities})

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
        df_enrollment = pd.DataFrame(data_enrollment)

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
    Input('addrow-rooms-button', 'n_clicks'),
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
    # download as MS Excel for import in MS Access Database
    if DEBUG:
        print("function: download")
    if n_clicks > 0:

        # retrieve the datatable
        _df = pd.DataFrame(data)

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
        df = pd.DataFrame(d)

        xlsx_io = io.BytesIO()
        writer = pd.ExcelWriter(
            xlsx_io, engine='xlsxwriter', options={'strings_to_numbers': False}
        )
        df.to_excel(writer, sheet_name='Final Exam Schedule', index=False)

        # Save it
        writer.save()
        xlsx_io.seek(0)
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        data = base64.b64encode(xlsx_io.read()).decode('utf-8')

        return {'base64': True, 'content': data, 'filename': 'Final Exam Schedule.xlsx', }

@app.callback(
    Output('datatable-combined-div', 'children'),
    [Input('update-button', 'n_clicks'),
     State('datatable-enrollment', 'data'),
     State('datatable-finals', 'data'),
     State('datatable-rooms', 'data')]
)
def create_combined_table(n_clicks, data_enrollment, data_finals, data_rooms):

    # retrieve enrollment table
    df_enrollment = pd.DataFrame(data_enrollment)

    # retrieve finals table
    df_finals = pd.DataFrame(data_finals)

    # recalculate the day of the final based on the date of the final
    for row in df_finals.index.tolist():
        Date = df_finals.loc[row, 'Date']
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
        df_finals.loc[row, 'Days'] = Days

    # retrieve rooms table
    df_rooms = pd.DataFrame(data_rooms)

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

    indexFilter = df_enrollment.index.tolist()

    # '''
    # check to see if every course has a final
    _indexFilter = no_final(df_enrollment, df_finals)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '0'

    # check to see if there are multiple finals for a given CRN
    _indexFilter = multiple_finals(df_enrollment[~df_enrollment['Error'].str.contains('0')], df_finals)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '1'

    # check to see if final is on one of the class days
    _indexFilter = correct_final_day(df_enrollment[~df_enrollment['Error'].str.contains('0|1')], df_finals)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += '2'

    # check to see if final room is in room table
    _indexFilter = room_exist(df_enrollment[~df_enrollment['Error'].str.contains('0|1')], df_finals, df_rooms)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += 'B'

    # check final room capacity
    _indexFilter = final_room_capacity(df_enrollment[~df_enrollment['Error'].str.contains('0|1|B')], df_finals, room_capacities)
    if _indexFilter:
        df_enrollment.loc[_indexFilter, 'Error'] += 'A'

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


    # check that start time is within one hour of regular class start time
    for row in indexFilter:
        class_start = datetime.datetime.strptime(df_enrollment.loc[row, 'Time'][:5], "%H:%M")
        plusone = class_start + datetime.timedelta(hours=1)
        minusone = class_start + datetime.timedelta(hours=-1)
        try:
            final_start = datetime.datetime.strptime(df_enrollment.loc[row, 'Final_Time'][:5], "%H:%M")
            final_day = df_enrollment.loc[row, 'Final_Day']
            if (final_start < minusone or final_start > plusone) and (final_day != "S"):
                # ERROR 9: Final start time not within one hour of regular start time
                if '9' not in df_enrollment.loc[row, 'Error']:
                    df_enrollment.loc[row, 'Error']+='9'

        except: # no final time provided
            pass

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
                    if '3' not in df_enrollment.loc[row, 'Error']:
                        df_enrollment.loc[row, 'Error']+='3'

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
                                if '4' not in df_enrollment.loc[row, 'Error']:
                                    df_enrollment.loc[row, 'Error']+='4'

                # check for instructor back-to-back (different rooms) within 15 minutes
                end_times = [datetime.datetime.strptime(time[-5:], "%H:%M")+datetime.timedelta(minutes=15) for time in times]
                for k in range(n):
                    s = ([x > start_times[k] for x in end_times])
                    e = ([x < end_times[k] for x in start_times])
                    if sum([x*y for x,y in zip(s,e)]) > 1:
                        for row in df.index.tolist():
                            if df.loc[row, 'Final_Time'] == times[k]:
                                # ERROR 5: Instructor back-to-back within 15 minutes
                                if '5' not in df_enrollment.loc[row, 'Error']:
                                    df_enrollment.loc[row, 'Error']+='5'



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
                    if '6' not in df_enrollment.loc[row, 'Error']:
                        df_enrollment.loc[row, 'Error']+='6'

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
                                if '7' not in df_enrollment.loc[row, 'Error']:
                                    df_enrollment.loc[row, 'Error']+='7'
                # check for back-to-back in same room
                for k in range(n):
                    s = ([x == start_times[k] for x in end_times[:-1]])
                    e = ([x == end_times[k] for x in start_times[1:]])
                    if sum(s+e) > 0:
                        for row in df.index.tolist():
                            if df.loc[row, 'Final_Time'] == times[k]:
                                # ERROR 8: Back-to-back in same room
                                if '8' not in df_enrollment.loc[row, 'Error']:
                                    df_enrollment.loc[row, 'Error']+='8'

    # check enrollment by instructor, if room large enough, remove error
    rows = df_enrollment[df_enrollment['Error'].str.contains('3')].index.tolist()
    # now add up all the enrollments and compare against room capacity
    df = df_enrollment[df_enrollment.index.isin(rows)]
    for row in rows:
        CRN = df_enrollment.loc[row, 'CRN']
        enrl = df[(df['Instructor'] == df.loc[row, 'Instructor']) & (df['Final_Time'] == df.loc[row, 'Final_Time']) & (df['Final_Day'] == df.loc[row, 'Final_Day'])]['Enrolled'].sum()
        try: # only can be done if the room exists in the room_capacity dictionary
            if (enrl < int(room_capacities[df.loc[row, 'Final_Loc']])): # and (df[(df['Instructor'] == df.loc[row, 'Instructor']) & (df['Time'] == df.loc[row, 'Time'])].shape[0] == 1):
                df_enrollment.loc[row, 'Error'] = df_enrollment.loc[row, 'Error'].replace('3','')
            else:
                if df.loc[row , 'Loc'] == df_finals[df_finals['CRN'] == CRN]['Loc'].iloc[0]:
                    # ERROR A: Room capacity too low
                    if 'A' not in df_enrollment.loc[row, 'Error']:
                        df_enrollment.loc[row, 'Error']+='A'

        except KeyError:
            # ERROR B: Room does not exist in Rooms Table
            if 'B' not in df_enrollment.loc[row, 'Error']:
                df_enrollment.loc[row, 'Error']+='B'

    # check enrollment by room, if room large enough, remove error
    rows = df_enrollment[df_enrollment['Error'].str.contains('6')].index.tolist()
    # now add up all the enrollments and compare against room capacity
    df = df_enrollment[df_enrollment.index.isin(rows)]
    for row in rows:
        enrl = df[(df['Final_Loc'] == df.loc[row, 'Final_Loc']) & (df['Final_Time'] == df.loc[row, 'Final_Time']) & (df['Final_Day'] == df.loc[row, 'Final_Day'])]['Enrolled'].sum()
        try: # only can be done if the room exists in the room_capacity dictionary
            if enrl < int(room_capacities[df.loc[row, 'Final_Loc']]):
                df_enrollment.loc[row, 'Error'] = df_enrollment.loc[row, 'Error'].replace('6','')
        except KeyError:
            # ERROR B: Room does not exist in Rooms Table
            if 'B' not in df_enrollment.loc[row, 'Error']:
                df_enrollment.loc[row, 'Error']+='B'

    # check if day and time correspond to Finals Grid
    rows = df_enrollment[~df_enrollment['Error'].str.contains('0|1')].index.tolist()
    df = df_enrollment[df_enrollment.index.isin(rows)]
    for row in rows:
        CRN = df_enrollment.loc[row, 'CRN']

        # convert everything to string to compare to datatable
        credit = str(int(df_enrollment.loc[row, 'Credit']))
        start_time = df_enrollment.loc[row, 'Time'][:5]
        meetings = str(len(days) - days.count(" ")) # do not count spaces
        days = df_enrollment.loc[row, 'Days']

        _df = df_grid[(df_grid['Credit']==credit) & (df_grid['Class_Start']==start_time) & (df_grid['Meetings']==meetings) & (df_grid['Class_Days']==days)]
        try:
            final_day = df_finals[df_finals['CRN']==CRN]['Days'].iloc[0]
            final_time = df_finals[df_finals['CRN']==CRN]['Time'].iloc[0]
            grid_day = _df['Final_Day'].iloc[0]
            grid_time = _df['Final_Time'].iloc[0]
            if (grid_day != final_day) or (grid_time != final_time):
                if (df_enrollment.loc[row, 'Number'] in ['1109', '1110', '1111']) and (final_day == "S"):
                    pass
                else:
                    # ERROR C : Final day/time does not agree with Finals Grid
                    df_enrollment.loc[row, 'Error']+='C'
        except IndexError:
            pass # could not find day/time in finals grid

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
            html.Li('A : Room capacity may be too low (check in Banner)'),
            html.Li('B : Room does not exist in Rooms Table'),
            html.Li('C : Final day/time does not agree with Finals Grid'),
        ],
            style={'listStyleType': 'none', 'lineHeight': 1.25},
        ),
    ]
    return data_children

# Main
if __name__ == '__main__':
    if mathserver:
        app.run_server(debug=DEBUG)
    else:
        app.run_server(debug=True, host='10.0.2.15', port='8053')
