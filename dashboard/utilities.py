from os import times
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import io
import datetime

def blankFigure():
# blank figure when no data is present
    return {
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
        ["MTH 3130", "Applied Methods in Linear Algebra",],
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
        ["MTH 3450", "Complex Variables",],
        ["MTH 3470", "Intro Discrete Math & Modeling",],
        ["MTH 3510", "SAS Programming",],
        ["MTH 3640", "History of Mathematics",],
        ["MTH 3650", "Foundations of Geometry",],
        ["MTH 4110", "Abstract Algebra II",],
        ["MTH 4150", "Elementary Number Theory",],
        ["MTH 4210", "Probability Theory",],
        ["MTH 4230", "Regression/Computational Stats",],
        ["MTH 4250", "Statistical Theory",],
        ["MTH 4290", "Senior Statistics Project",],
        ["MTH 4410", "Real Analysis I",],
        ["MTH 4420", "Real Analysis II",],
        ["MTH 4440", "Partial Differential Equations",],
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
        ["MTL 4630", "Teaching Secondary Mathematics",],
        ["MTL 4690", "Student Teaching & Seminar: Secondary 7-12",],
        ["MTLM 5020", "Integrated Mathematics II",],
        ["MTLM 5600", "Mathematics of the Elementary Curriculum",],
        ["MTLM 5610", "Elementary Mathematics from an Advanced Perspective"],
    ]

    df_titles = pd.DataFrame(course_titles, columns=["Class", "Title"])

    cols = df.columns
    df = df.set_index("Class")
    df.update(df_titles.set_index("Class"))
    df.reset_index(inplace=True)
    df = df[cols]

    return df


def convertAMPMtime(timeslot):

    if pd.isna(timeslot):
        return

    try:
        if ("AM" in timeslot) or ("PM" in timeslot):
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

    # delete information in first line to match txt file type
    _list = _list[1:]
    _list.insert(0,'')

    return tidy_txt(io.StringIO("\n".join(_list)))


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
    d = ''
    for i in range(5):
        line = file_contents.readline()
        if i == 4:
            d = line.split()[-1]
            break

    data_date = datetime.datetime.strptime(d, "%d-%b-%Y")

    # read into a dataframe based on specified column spacing
    _df = pd.read_fwf(file_contents, colspecs=_LINE_PATTERN)

    # read the report Term and Year from file
    dd = _df.iloc[0]
    term_code = str(dd.iloc[1][3:])+str(dd.iloc[2][:-2])
    # term_code = str(_df.iloc[0][1])[3:] + str(_df.iloc[0][2])[:-2]

    # rename the columns
    # make allowances for newer version of pandas
    if pd.__version__ >= '1.4.1':
        k = 1
    else:
        k = 2
    _df.columns = _df.iloc[k]


    # manual filtering of erroneous data which preserves data for MTH 1108/1109
    _df = _df.dropna(how='all')
    _df = _df[~_df["Subj"].str.contains("Subj", na=False)]
    _df = _df[~_df["Subj"].str.contains("---", na=False)]
    _df = _df[~_df["Subj"].str.contains("SWRC", na=False)]
    _df = _df[~_df["Subj"].str.contains("Ter", na=False)]
    _df = _df[~_df["Instructor"].str.contains("Page", na=False)]

    _df.reset_index(drop=True, inplace=True)
    # pick up all rows where the "Begin/End" does not contain data
    nan_rows_indexes=list(_df.loc[pd.isna(_df["Begin/End"]), :].index.values)
    # append the "Loc" and "Instructor" to the previous row
    mask = []
    for row in _df.index.to_list():
        if row in nan_rows_indexes:
            for column in ["Loc", "Instructor"]:
                # only do this when the data is not null and is a string
                if not pd.isnull(_df.iloc[row][column]) and isinstance(_df.iloc[row-1][column],str):
                    _df.loc[row-1,column] = _df.iloc[row-1][column] + _df.iloc[row][column]
                    # keep track of those rows and remove them later
                    mask.append(row)

    # remove those rows whose data was appended to the previous row
    _df = _df.drop(mask)

    _df = _df.drop(_df.index[_df["Loc"].str.startswith("BA", na=False)].tolist())
    # _df = _df[_df["Time"].notna()]
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

    # _df = _df[_df["Instructor"].str.contains(',', na=False)]
    # reset index and remove old index column
    _df = _df.reset_index()
    _df = _df.drop([_df.columns[0]], axis=1)

    # for row in _df.index.to_list():
        # if pd.isnull(_df.loc[row, 'Subj']):
            # _df.loc[row, 'Subj'] = _df.loc[row-1, 'Subj']
        # if pd.isnull(_df.loc[row, 'Nmbr']):
            # _df.loc[row, 'Nmbr'] = _df.loc[row-1, 'Nmbr']
        # if pd.isnull(_df.loc[row, 'CRN']):
            # _df.loc[row, 'CRN'] = _df.loc[row-1, 'CRN']
        # if pd.isnull(_df.loc[row, 'Sec']):
            # _df.loc[row, 'Sec'] = _df.loc[row-1, 'Sec']
        # if pd.isnull(_df.loc[row, 'S']):
            # _df.loc[row, 'S'] = _df.loc[row-1, 'S']
        # if pd.isnull(_df.loc[row, 'Cam']):
            # _df.loc[row, 'Cam'] = _df.loc[row-1, 'Cam']
        # if pd.isnull(_df.loc[row, 'Title']):
            # _df.loc[row, 'Title'] = _df.loc[row-1, 'Title']
        # if pd.isnull(_df.loc[row, 'PTCR']):
            # _df.loc[row, 'PTCR'] = _df.loc[row-1, 'PTCR']
        # if pd.isnull(_df.loc[row, 'T']):
            # _df.loc[row, 'T'] = _df.loc[row-1, 'T']
        # if pd.isnull(_df.loc[row, 'Credit']):
            # _df.loc[row, 'Credit'] = _df.loc[row-1, 'Credit']
        # if pd.isnull(_df.loc[row, 'Max']):
            # _df.loc[row, 'Max'] = _df.loc[row-1, 'Max']
        # if pd.isnull(_df.loc[row, 'Enrl']):
            # _df.loc[row, 'Enrl'] = _df.loc[row-1, 'Enrl']
        # if pd.isnull(_df.loc[row, 'WCap']):
            # _df.loc[row, 'WCap'] = _df.loc[row-1, 'WCap']
        # if pd.isnull(_df.loc[row, 'WLst']):
            # _df.loc[row, 'WLst'] = _df.loc[row-1, 'WLst']

    # This is a hack to include all rows of days into one for those classes
    # that have different modes of teaching on different days.  For example,
    # if MTLM 5610 is MT R, but the M is online and T R are in person.

    # print()
    # print(_df.to_string())

    # for row in _df.index.to_list():
        # if pd.isnull(_df.loc[row, 'Subj']) and (_df.loc[row-1, 'Nmbr'] not in ['1108', '1109']):
            # weekdays = {'M':0, 'T':1, 'W':2, 'R':3, 'F':4, 'S':5}
            # days = '      '
            # _days = _df.loc[row, 'Days'] + _df.loc[row-1, 'Days']
            # for day in weekdays.keys():
                # if day in _days:
                    # index = weekdays[day]
                    # days = days[:index] + day + days[ index + 1:]
            # _df.loc[row-1, 'Days'] = days.rstrip()
            # _df.loc[row, 'Subj'] = _df.loc[row-1, 'Subj']
            # _df.loc[row, 'Nmbr'] = _df.loc[row-1, 'Nmbr']

    # only remove the extra rows from above that we no longer need but preserve
    # the extra rows for 1108 and 1109
    _df = _df[(~_df["CRN"].isnull()) | (~_df["Nmbr"].isin(['1108','1109']))]
    _df = _df.reset_index()
    _df = _df.drop([_df.columns[0]], axis=1)

    # print()
    # print(_df.to_string())

    # change PTCR for 1081s, 1311s, 1111s, and 1115s to 0
    for nmbr in ["1081", "1111", "1115", "1311"]:
        for row in _df[_df["Subj"].str.contains("MTH") & _df["Nmbr"].str.contains(nmbr) & _df["S"].str.contains("A")].index.tolist():
            _df.loc[row, "PTCR"] = 0

    # change all online final flags to N since they do not need a room
    for row in _df[_df["Cam"].str.startswith("I", na=False)].index.tolist():
        _df.loc[row, "Final"] = "N"

    # correct report to also include missing data for MTH 1108 and MTH 1109
    for stretch_course in ['1108', '1109']:
        for row in _df[_df["Subj"].str.contains("MTH") & _df["Nmbr"].str.contains(stretch_course) & _df["S"].str.contains("A")].index.tolist():

            # copy all but days, time and location to next row
            for col in ["Subj", "Nmbr", "CRN", "Sec", "S", "Cam", "T", "Title", "Max", "Enrl", "WCap", "WLst", "Instructor"]:
                _df.loc[row + 1, col] = _df.loc[row, col]

            # define values for Credit and PTCR
            _df.loc[row + 1, "Credit"] = 0
            _df.loc[row + 1, "PTCR"] = 0

            # copy all values from parent row and make available for lab instructor
            row_dict = _df.loc[row].to_dict()
            row_dict["Instructor"] = ","
            row_dict["Credit"] = 0
            row_dict["PTCR"] = 1
            _df = pd.concat([_df, pd.DataFrame(row_dict, index=[0])], ignore_index=True)

    # add columns for Access Table
    _df.insert(len(_df.columns), "Class", " ")
    _df["Class"] = _df["Subj"] + " " + _df["Nmbr"]
    _df['DaysTimeLoc'] = _df['Days'] +  _df['Time'] + _df['Loc']
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

    # include in calculations
    _df['Calc'] = 'Y'
    for row in _df.index.to_list():
        if _df.loc[row, 'S'] == 'C':
            _df.loc[row, 'Calc'] = 'N'

    return _df, term_code, data_date


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

    # _df = pd.read_excel(file_contents,
                        # engine='openpyxl',
                        # converters={
                            # 'Subject':str,
                            # 'Number':str,
                            # 'CRN':str,
                            # 'Section':str,
                            # 'Campus':str,
                            # 'Title':str,
                            # 'Days':str,
                            # 'Time':str,
                            # 'Loc':str,
                            # 'Instructor':str,
                        # })

    # work around to import the Number and Section correctly since they are formulas
    from openpyxl import load_workbook
    wb = load_workbook(file_contents)
    sheet_names = wb.get_sheet_names()
    name = sheet_names[0]
    sheet_ranges = wb[name]
    df_test = pd.DataFrame(sheet_ranges.values)
    df_test.columns = df_test.iloc[0]
    df_test = df_test.iloc[1:,:]
    df_test["Number"] =  df_test["Number"].str.replace('"','')
    df_test["Number"] =  df_test["Number"].str.replace('=','')
    df_test["Section"] =  df_test["Section"].str.replace('"','')
    df_test["Section"] =  df_test["Section"].str.replace('=','')
    _df = df_test.copy()

    # create missing columns, if necessary
    if not 'S' in _df.columns:
        _df.insert(len(_df.columns), "S", "A")
    if not 'Begin/End' in _df.columns:
        _df.insert(len(_df.columns), "Begin/End", "01/01-01/01")
    if not 'T' in _df.columns:
        _df.insert(len(_df.columns), "T", 1)
    if not 'WCap' in _df.columns:
        _df.insert(len(_df.columns), "WCap", 0)
    if not 'WList' in _df.columns:
        _df.insert(len(_df.columns), "WList", 0)
    if not 'Enrolled' in _df.columns:
        _df.insert(len(_df.columns), "Enrolled", 0)
    if not 'Rcap' in _df.columns:
        _df.insert(len(_df.columns), "Rcap", 0)
    if not 'Max' in _df.columns:
        _df.insert(len(_df.columns), "Max", 1)
    if not 'Full' in _df.columns:
        _df.insert(len(_df.columns), "Full", 0)
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

    _df = _df[["Subject", "Number", "CRN", "Section", "S", "Campus", "T", "Title",
              "Credit", "Max", "Enrolled", "WCap", "WList", "Days", "Time", "Loc",
              "Rcap", "Full", "Begin/End", "Instructor"]]

    _df.insert(len(_df.columns), "Class", " ")
    _df["Class"] = _df["Subject"] + " " + _df["Number"]
    _df['DaysTimeLoc'] = _df['Days'] +  _df['Time'] + _df['Loc']

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

    # there might be CRNs that are unknown (blank), so fill sequentially starting
    # from 99999 and go down
    i = 1
    for row in _df[_df["CRN"].isna()].index.tolist():
        _df.loc[row, "CRN"] = str(100000 - i)
        i += 1

    # include in calculations
    _df['Calc'] = 'Y'
    for row in _df.index.to_list():
        if _df.loc[row, 'S'] == 'C':
            _df.loc[row, 'Calc'] = 'N'

    return _df, term_code, data_date


