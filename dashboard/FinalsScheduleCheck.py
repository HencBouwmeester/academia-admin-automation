import pandas as pd
import io
import datetime

"""
Step 1: Download SWRCGSR from Banner for current semester (should be saved as GJIREVO.csv)
Step 2: Export finals schedule for all subjects (ex: MTH and MTL), make sure to get
        the Saturday before finals week as well
Step 3: Using MS Excel, combine into one file named Exports.csv.

        The error codes are
             0: No final for this CRN
             1: Multiple finals for this CRN
             2: Day of final incorrect
             3: Overlap of time block
             4: Overlap between time blocks
             5: Instructor back-to-back within 5 minutes
             6: Overlap of time block
             7: Overlap between time blocks
             8: Back-to-back in same room
             9: Final start time not within one hour of regular start time

Step 3: Examine error codes
"""

DEBUG = False

# set option to show all rows
pd.set_option('display.max_rows', 1000)

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
        ['MTH 3130', 'Advd Matrix Mthds Phy Sciences',],
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

    # reset to the start of the IO stream
    # file_contents.seek(0)

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
    _df.drop(['T', 'Max', 'WCap', 'WList', 'Rcap', 'Full'], axis=1, inplace=True)

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

    # _file = file_contents.read()
    _file = ""
    for line in file_contents:
        _file = _file + line


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

def parse_finals(file_contents):

    rows = []
    for line in file_contents:
        line = line.replace('"','')
        fields = line.split(',')

        # only pick up classes for MTH or MTL
        if fields[1][:3] == "MTH" or fields[1][:3] == "MTL":
            CRN = fields[1].split(' ')[1]
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

    df = pd.DataFrame(rows, columns=['CRN', 'Days', 'Time', 'Loc', 'Date'])
    return df

# read in the schedule enrollment report (SWRCGSR)
with open('GJIREVO.csv') as infile:

    file_contents = infile.readlines()

    df_SWRCGSR = tidy_csv(file_contents)

# read in the finals schedule export
with open('Export.csv') as infile:
    file_contents = infile.readlines()

    df_FINALS = parse_finals(file_contents)

# remove all canceled classes
df_SWRCGSR.drop(df_SWRCGSR[df_SWRCGSR.S == "C"].index, inplace=True)

# remove any times that have TBA
df_SWRCGSR.drop(df_SWRCGSR[df_SWRCGSR.Time == "TBA"].index, inplace=True)

# remove any classes not on the main campus
df_SWRCGSR.drop(df_SWRCGSR[df_SWRCGSR.Campus != "M"].index, inplace=True)

# remove labs
df_SWRCGSR.drop(df_SWRCGSR[df_SWRCGSR.Number == "1082"].index, inplace=True)
df_SWRCGSR.drop(df_SWRCGSR[df_SWRCGSR.Number == "1101"].index, inplace=True)
df_SWRCGSR.drop(df_SWRCGSR[df_SWRCGSR.Number == "1116"].index, inplace=True)
df_SWRCGSR.drop(df_SWRCGSR[df_SWRCGSR.Number == "1312"].index, inplace=True)

# change time format from 12HR to 24HR
df_SWRCGSR['Time'] = df_SWRCGSR['Time'].apply(lambda x: convertAMPMtime(x))

# remove extraneous columns
df_SWRCGSR = df_SWRCGSR.drop(columns=['Begin/End', 'S'])

# reset the index
df_SWRCGSR = df_SWRCGSR.reset_index(drop=True)

# create columns for final information
df_SWRCGSR['Final_Day'] = ''
df_SWRCGSR['Final_Time'] = ''
df_SWRCGSR['Final_Loc'] = ''
df_SWRCGSR['Final_Time'] = ''
df_SWRCGSR['Final_Date'] = ''
df_SWRCGSR['Error'] = [[] for _ in range(len(df_SWRCGSR))]

# change time format from 12HR to 24HR
df_FINALS['Time'] = df_FINALS['Time'].apply(lambda x: convertAMPMtime(x))

if DEBUG:
    print(df_FINALS.sort_values(by='CRN'))
    print(df_SWRCGSR.sort_values(by='CRN'))
# df_FINALS.to_csv('FINALS.csv', index=False)
# df_SWRCGSR.to_csv('SWRCGSR.csv', index=False)

# go through each row
for row in df_SWRCGSR.index.tolist():
    CRN = df_SWRCGSR.loc[row, 'CRN']

    # check if there is a final for this CRN
    if df_FINALS[df_FINALS['CRN'] == CRN].shape[0] == 0:
        # ERROR 0: No final for this CRN
        df_SWRCGSR.loc[row, 'Error'].append(0)

    # check for multiple finals for this CRN
    else:
        if df_FINALS[df_FINALS['CRN'] == CRN].shape[0] > 1:
            # ERROR 1: Multiple finals for this CRN
            df_SWRCGSR.loc[row, 'Error'].append(1)

        else: # only one final found
            # check if day of final is one of the days of the class
            day = df_FINALS[df_FINALS['CRN'] == CRN]['Days'].iloc[0]
            date = df_FINALS[df_FINALS['CRN'] == CRN]['Date'].iloc[0]
            time = df_FINALS[df_FINALS['CRN'] == CRN]['Time'].iloc[0]
            room = df_FINALS[df_FINALS['CRN'] == CRN]['Loc'].iloc[0]
            days = df_SWRCGSR.loc[row, 'Days']
            if days.find(day) < 0:

                # day of week does not match, is this an Algebra class
                if df_SWRCGSR.loc[row, 'Number'] in ['1109', '1110', '1111']:
                    if day == "S":
                        df_SWRCGSR.loc[row, 'Final_Day'] = day
                        df_SWRCGSR.loc[row, 'Final_Date'] = date
                        df_SWRCGSR.loc[row, 'Final_Time'] = time
                        df_SWRCGSR.loc[row, 'Final_Loc'] = room
                    else:
                        # ERROR 2: Day of final incorrect
                        df_SWRCGSR.loc[row, 'Error'].append(2)

                else:
                    # ERROR 2: Day of final incorrect
                    df_SWRCGSR.loc[row, 'Error'].append(2)

            else:
                df_SWRCGSR.loc[row, 'Final_Day'] = day
                df_SWRCGSR.loc[row, 'Final_Date'] = date
                df_SWRCGSR.loc[row, 'Final_Time'] = time
                df_SWRCGSR.loc[row, 'Final_Loc'] = room

# check for instructor overlap
instructors = df_SWRCGSR['Instructor'].unique()
for instructor in instructors:
    days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
    for day in days:
        # filter by location and day
        df = df_SWRCGSR[(df_SWRCGSR['Instructor'] == instructor) & (df_SWRCGSR['Final_Day'] == day)]

        # check for instructor overlap of same time blocks (this does not calculate all overlaps)
        if df.shape[0] > 1 and (df['Time'].nunique() != df['Final_Time'].nunique()):
            for row in df.index.tolist():
                # ERROR 3: Overlap of time block
                df_SWRCGSR.loc[row, 'Error'].append(3)

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
                            df_SWRCGSR.loc[row, 'Error'].append(4)

            # check for instructor back-to-back (different rooms) within 5 minutes
            end_times = [datetime.datetime.strptime(time[-5:], "%H:%M")+datetime.timedelta(minutes=5) for time in times]
            for k in range(n):
                s = ([x > start_times[k] for x in end_times])
                e = ([x < end_times[k] for x in start_times])
                if sum([x*y for x,y in zip(s,e)]) > 1:
                    for row in df.index.tolist():
                        if df.loc[row, 'Final_Time'] == times[k]:
                            # ERROR 5: Instructor back-to-back within 5 minutes
                            df_SWRCGSR.loc[row, 'Error'].append(5)



# check for room overlap
rooms = df_SWRCGSR['Final_Loc'].unique()
for room in rooms:
    days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
    for day in days:
        # filter by location and day
        df = df_SWRCGSR[(df_SWRCGSR['Final_Loc'] == room) & (df_SWRCGSR['Final_Day'] == day)]

        # check for room overlap of same time blocks (this does not calculate all overlaps)
        if df.shape[0] > 1 and (df['Time'].nunique() != df['Final_Time'].nunique()):
            for row in df.index.tolist():
                # ERROR 6: Overlap of time block
                df_SWRCGSR.loc[row, 'Error'].append(6)

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
                            df_SWRCGSR.loc[row, 'Error'].append(7)
            # check for back-to-back in same room
            for k in range(n):
                s = ([x == start_times[k] for x in end_times[:-1]])
                e = ([x == end_times[k] for x in start_times[1:]])
                if sum(s+e) > 0:
                    for row in df.index.tolist():
                        if df.loc[row, 'Final_Time'] == times[k]:
                            # ERROR 8: Back-to-back in same room
                            df_SWRCGSR.loc[row, 'Error'].append(8)

# check that start time is within one hour of regular class start time
for row in df_SWRCGSR.index.tolist():
    class_start = datetime.datetime.strptime(df_SWRCGSR.loc[row, 'Time'][:5], "%H:%M")
    plusone = class_start + datetime.timedelta(hours=1)
    minusone = class_start + datetime.timedelta(hours=-1)
    try:
        final_start = datetime.datetime.strptime(df_SWRCGSR.loc[row, 'Final_Time'][:5], "%H:%M")
        final_day = df_SWRCGSR.loc[row, 'Final_Day']
        if (final_start < minusone or final_start > plusone) and (final_day != "S"):
            # ERROR 9: Final start time not within one hour of regular start time
            df_SWRCGSR.loc[row, 'Error'].append(9)

    except: # no final time provided
        pass

room_capacities = {
    "CN 109": 47,
    "KC 307": 48,
    "KC 313": 48,
    "PL 329": 24,
    "PL M204": 110,
    "PL M206": 46,
    "SI 1007": 25,
    "SI 1008": 44,
    "SI 1010": 40,
    "SI 1011": 42,
    "SI 1015": 36,
    "SI 1058": 40,
    "SI 1068": 16,
    "SI 1113": 54,
    "SSB 213": 24,
}

# check enrollment by instructor, if room large enough, remove error
rows = []
for row in df_SWRCGSR.index.tolist():
    # same room, different instructor
    if 3 in df_SWRCGSR.loc[row, 'Error']:
        rows.append(row)
# now add up all the enrollments and compare against room capacity
df = df_SWRCGSR[df_SWRCGSR.index.isin(rows)]
for row in rows:
    enrl = df[(df['Instructor'] == df.loc[row, 'Instructor']) & (df['Final_Time'] == df.loc[row, 'Final_Time'])]['Enrolled'].sum()
    if enrl < room_capacities[df.loc[row, 'Final_Loc']]:
        try: # only can be done if the room exists in the room_capacity dictionary
            df_SWRCGSR.loc[row, 'Error'].remove(3)
        except:
            pass

# check enrollment by room, if room large enough, remove error
rows = []
for row in df_SWRCGSR.index.tolist():
    # same room, different CRN
    if 6 in df_SWRCGSR.loc[row, 'Error']:
        rows.append(row)
# now add up all the enrollments and compare against room capacity
df = df_SWRCGSR[df_SWRCGSR.index.isin(rows)]
for row in rows:
    enrl = df[(df['Final_Loc'] == df.loc[row, 'Final_Loc']) & (df['Final_Time'] == df.loc[row, 'Final_Time'])]['Enrolled'].sum()
    if enrl < room_capacities[df.loc[row, 'Final_Loc']]:
        try: # only can be done if the room exists in the room_capacity dictionary
            df_SWRCGSR.loc[row, 'Error'].remove(6)
        except:
            pass


# print(df_SWRCGSR.sort_values(by='CRN'))
print(df_SWRCGSR.sort_values(by=['Subject', 'Number', 'Section']))

# save to CSV file
df_SWRCGSR.to_csv('FinalsChecked.csv', index=False)
