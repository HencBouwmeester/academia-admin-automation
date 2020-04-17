#!/usr/bin/env python3

from enrollmentUtils import *

def readcsv(filename):
    import csv
    import datetime

    # capture the date from the file header
    with open(filename, "r") as currentfile:
        i = 0
        for line in currentfile:
            # the date is in the fourth line, last column, and remove the trailing comma
            if i == 4:
                d = line.split()[-1][:-1]
                break
            else:
                i += 1
    d = datetime.datetime.strptime(d, "%d-%b-%Y")
    datadate = datetime.datetime.strftime(d,"%Y%m%d")

    newfile = []

    # Open and process text file output
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        # eliminate top rows without data
        for _ in range(7):
            next(reader)
        for row in reader:
            # trim extra spaces or pad to adjust to 140 characters
            newrow = (
                row[0][:140].ljust(140) if len(row[0][:140]) < 140 else row[0][:140]
            )

            # break lines with data into a list of pieces
            newlist = list(alternating_size_chunks(newrow, HEADER_ROW.values()))

            # Catch non-data containing lines and skip them
            # if newlist[0][0:4] == "----" or newlist[0][0:4] == "Subj" or newlist[0][0] == " " or newlist[14] == 12*" " or newlist[2][0] == " ":
                # continue

            # if newlist[4][0] == "C":
                # continue

            # convert time format from 12hr to 24hr and account for TBA times
            newlist[14] = convertAMPMtime(newlist[14])

            # add date stamp column
            newlist.append(datadate)

            # Add the entry to our output list
            newfile.append(newlist)

    # Remove final non-data lines
    newfile = newfile[:-1]

    return newfile



if __name__ == "__main__":
    import os
    import glob
    import csv
    import pandas as pd

    # minimum enrollment for lower division
    l_minenrollment = 19

    # minimum enrollment for upper division
    u_minenrollment = 13

    # read in all csv files in current directory
    path = os.getcwd()
    files=glob.glob(path + "/*.csv")
    nf = len(files)

    campusCodes = ["M", "I", "O", "D", "S"]
    data = []
    for filename in files:
        current = readcsv(filename)
        for line in current:
            if (line[5].strip() in campusCodes):
                data.append([line[0].strip(),
                             line[1].strip(),
                             int(line[2].strip() or 0),
                             line[3].strip(),
                             line[4].strip(),
                             line[5].strip(),
                             int(line[9].strip() or 0),
                             int(line[10].strip() or 0),
                             int(line[12].strip() or 0),
                             line[13].strip(),
                             line[14].strip(),
                             line[15].strip(),
                             line[19].strip(),
                             line[-1]
                            ])

    # store the data as a dataframe
    data = pd.DataFrame(data, columns = ["Subj",
                                         "CourseNumber",
                                         "CRN",
                                         "Sec",
                                         "Status",
                                         "Campus",
                                         "Max",
                                         "Enrollment",
                                         "Wait",
                                         "Days",
                                         "Time",
                                         "Location",
                                         "Instructor",
                                         "Date"])

    # convert date column to datetime format
    data.Date = pd.to_datetime(data.Date, format="%Y%m%d")

    # show all rows in print
    # pd.set_option('display.max_rows', data.shape[0]+1)

    # print(data)

    # how many active and canceled
    # print(data[['CRN', 'Status']].groupby(['Status']).agg(['count']))

    # how many of each course
    # print(data[['CRN', 'Subj']].groupby(['Subj']).agg(['count']))

    print(data[(data["Subj"] == "MTH") & (data["CourseNumber"] == "1311")])

    '''
    # if there are duplicate dates, exit with an error.
    if nf != len(data.Date.unique()):
        print("ERROR:  There are {:d} files present in {:s}, but only {:d} unique dates.  Remove any duplicate dated files.".format(nf, path, len(data.Date.unique())))
        sys.exit(0)

    # Delete old graphs and create the new graphs
    path = os.getcwd()
    path += "/graphs"

    try:
        os.mkdir(path)
    except OSError:
        pass

    '''
