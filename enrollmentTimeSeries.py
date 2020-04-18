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
    import numpy as np
    import glob
    import csv
    import pandas as pd
    from matplotlib import pyplot as plt
    from matplotlib import dates as mdates
    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()

    # minimum enrollment for lower division
    l_minenrollment = 19

    # minimum enrollment for upper division
    u_minenrollment = 13

    # read in all csv files in current directory
    current_path = os.getcwd()
    files=glob.glob(current_path + "/*.csv")
    nf = len(files)

    campusCodes = ["M", "I", "O", "D", "S"]
    rawdata = []
    for filename in files:
        current = readcsv(filename)
        for line in current:
            if (line[5].strip() in campusCodes):
                rawdata.append([line[0].strip(),
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
                                line[0].strip() + " " + line[1].strip(),
                                line[-1]
                               ])

    # store the data as a dataframe
    rawdata = pd.DataFrame(rawdata, columns = ["Subj",
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
                                               "Course",
                                               "Date"])

    # convert date column to datetime format
    rawdata.Date = pd.to_datetime(rawdata.Date, format="%Y%m%d")

    # if there are duplicate dates, exit with an error.
    if nf != len(rawdata.Date.unique()):
        print("ERROR:  There are {:d} files present in {:s}, but only {:d} unique dates.  Remove any duplicate dated files.".format(nf, path, len(rawdata.Date.unique())))
        sys.exit(0)

    # create graphs directory if it does not exist
    try:
        os.mkdir(current_path + "/graphs")
    except OSError:
        pass


    # remove all courses that have been canceled
    CRNs = rawdata[rawdata["Status"] == "C"].CRN.unique()
    data = rawdata[rawdata["CRN"].isin(CRNs) == False]


    # load stacked courses
    assert os.path.exists(current_path + "/stacked.py"), "File does not exist: {:s}".format(current_path + "/stacked.py")
    exec(open(current_path + "/stacked.py").read())

    stackedCRNsFlat = []
    for stack in stackedCRNs:
        for course in stack:
            stackedCRNsFlat.append(course)

    stackedCoursesFlat = []
    for stack in stackedCourses:
        for course in stack:
            stackedCoursesFlat.append(course)

    # Enrollment for each CRN by date for non-stacked CRNs
    for CRN in data.CRN.unique():

        current_data = data[data.CRN == CRN]

        # collect course and max capacity
        current_subj = current_data['Subj'].unique()[0]
        current_CourseNumber = current_data['CourseNumber'].unique()[0]
        maxenrollment = current_data['Max'].max()
        course = "{:s} {:s} ({:d})".format(current_subj, current_CourseNumber, CRN)

        if not CRN in stackedCRNsFlat:

            x_values = current_data.Date.tolist()
            M = len(x_values)
            y_values = current_data.Enrollment.tolist()
            w_values = current_data.Wait.tolist()

            # Create figure and plot space
            fig, ax = plt.subplots(figsize=(6, 6))
            formatter = mdates.DateFormatter("%m-%d")
            ax.xaxis.set_major_formatter(formatter)
            ax.bar(x_values,
                   y_values,
                   linewidth = 1,
                   edgecolor = ["white"]*M)
            ax.bar(x_values,
                   w_values,
                   bottom = y_values,
                   color="gray",
                   linewidth = 1,
                   edgecolor = ["white"]*M)
            ax.set(xlabel="Date",
                   ylabel="Enrollment",
                   title="Enrollment for {:s}".format(course, CRN))


            # set max on y to make graphs comparable if less that 45
            # highest value needs to include the wait list
            plt.ylim(0,max(45,max([sum(y) for y in zip(y_values, w_values)])+5))

            # set minimum enrollment dependent on lower or upper division
            if int(course.split()[1][0]) >= 3:
                m = u_minenrollment
            else:
                m = l_minenrollment
            plt.plot([min(x_values), max(x_values)],[m, m],'--', color = "gray")

            # set maximum enrollment based on room capacity
            plt.plot([min(x_values), max(x_values)],[maxenrollment, maxenrollment],'--', color = "gray")

            # create filename and save the graph as a PDF
            figname = current_path + "/graphs/" + course + ".pdf"
            plt.savefig(figname)
            plt.close(fig)

    # Combined enrollment for each CRN in stacked CRNs by date
    for stack in stackedCRNs:

        # filter data per stack
        stackedData = data[data["CRN"].isin(stack)]

        # get totals for each date
        stackedDataTotals = data[data["CRN"].isin(stack)].groupby("Date", sort=False).sum()

        # compute the total maximum enrollment for all course in stack
        maxenrollment = max(stackedDataTotals.Max.tolist())

        # Create figure and plot space
        fig, ax = plt.subplots(figsize=(6, 6))
        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)

        # set the colors for the bars
        cmap = plt.get_cmap("Dark2")
        colors = cmap(np.linspace(0,1.0,len(stack)))

        x_values = stackedDataTotals.index.tolist()
        M = len(x_values)

        course = ""

        # create a bar plot for each CRN stacked on the previous one
        b = M*[0]
        for j, CRN in enumerate(stack):

            current_data = stackedData[stackedData.CRN == CRN]

            current_subj = current_data['Subj'].unique()[0]
            current_CourseNumber = current_data['CourseNumber'].unique()[0]
            course += "{:s} {:s} ({:d}), ".format(current_subj, current_CourseNumber, CRN)

            y_values = current_data.Enrollment.tolist()
            ax.bar(x_values,
                   y_values,
                   bottom = b,
                   label = CRN,
                   color = colors[j],
                   linewidth = 1,
                   edgecolor = ["white"]*M)
            b = [sum(y) for y in zip(b, y_values)]

        # remove trailing comma and space
        course = course[:-2]

        w_values = stackedDataTotals.Wait.tolist()

        # add bar for wait list
        ax.bar(x_values,
               w_values,
               bottom = b,
               linewidth = 1,
               label = "Wait List",
               color = "#D3D3D3",
               edgecolor = ["white"]*M)

        # set a title for the figure
        ax.set(xlabel="Date",
               ylabel="Enrollment",
               title="Enrollment for {:s}".format(course))


        # set max on y to make graphs comparable if less that 45
        # highest value needs to include the wait list
        plt.ylim(0,max(45,max([sum(y) for y in zip(b, w_values)])+5))

        # set minimum enrollment dependent on lower or upper division
        if int(course.split()[1][0]) >= 3:
            m = u_minenrollment
        else:
            m = l_minenrollment
        plt.plot([min(x_values), max(x_values)],[m, m],'--', color = "gray")

        # set maximum enrollment based on room capacity
        plt.plot([min(x_values), max(x_values)],[maxenrollment, maxenrollment],'--', color = "gray")

        # include a legend of all the CRNs
        plt.legend(loc="upper left")

        # create filename and save the graph as a PDF
        figname = current_path + "/graphs/" + course + ".pdf"
        plt.savefig(figname)
        plt.close(fig)


    for Course in data.Course.unique():

        combinedData = data[data.Course == Course]
        combinedDataTotals = combinedData.groupby("Date", sort=False).sum()
        CRNs = combinedData.CRN.unique()

        N = len(CRNs)

        if N > 1:

            # compute the total maximum enrollment for all course in stack
            maxenrollment = max(combinedDataTotals.Max.tolist())

            # Create figure and plot space
            fig, ax = plt.subplots(figsize=(6, 6))
            formatter = mdates.DateFormatter("%m-%d")
            ax.xaxis.set_major_formatter(formatter)

            # set the colors for the bars
            cmap = plt.get_cmap("Dark2")
            colors = cmap(np.linspace(0,1.0,N))

            x_values = combinedDataTotals.index.tolist()
            M = len(x_values)

            # create a bar plot for each CRN stacked on the previous one
            b = M*[0]
            for j, CRN in enumerate(CRNs):
                current_data = combinedData[combinedData.CRN == CRN]

                y_values = current_data.Enrollment.tolist()
                ax.bar(x_values,
                       y_values,
                       bottom = b,
                       label = CRN,
                       color = colors[j],
                       linewidth = 1,
                       edgecolor = ["white"]*M)
                b = [sum(y) for y in zip(b, y_values)]

            w_values = combinedDataTotals.Wait.tolist()

            # add bar for wait list
            ax.bar(x_values,
                   w_values,
                   bottom = b,
                   linewidth = 1,
                   label = "Wait List",
                   color = "#D3D3D3",
                   edgecolor = ["white"]*M)

            # set a title for the figure
            ax.set(xlabel="Date",
                   ylabel="Enrollment",
                   title="Enrollment for {:s}".format(Course))


            # set max on y to make graphs comparable if less that 45
            # highest value needs to include the wait list
            plt.ylim(0,max(maxenrollment, max([sum(y) for y in zip(b, w_values)]))+5)

            # set maximum enrollment based on room capacity
            plt.plot([min(x_values), max(x_values)],[maxenrollment, maxenrollment],'--', color = "gray")

            # include a legend of all the CRNs
            plt.legend(loc="upper left")

            # create filename and save the graph as a PDF
            figname = current_path + "/graphs/" + Course + ".pdf"
            plt.savefig(figname)
            plt.close(fig)

    for stack in stackedCourses:

        # filter data per stack
        stackedData = data[data["CourseNumber"].isin(stack)]
        stackedDataTotals = stackedData.groupby("Date", sort=False).sum()

        # combine the names of the courses
        Courses = stackedData["Subj"].str.cat(stackedData["CourseNumber"], sep=" ")
        course = ""
        for item in Courses.unique():
            course += item + "/"
        course = course[:-1]

        # compute the total maximum enrollment for all course in stack
        maxenrollment = max(stackedDataTotals.Max.tolist())

        # Create figure and plot space
        fig, ax = plt.subplots(figsize=(6, 6))
        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)

        # set the colors for the bars
        cmap = plt.get_cmap("Dark2")
        colors = cmap(np.linspace(0,1.0,len(stack)))

        x_values = stackedDataTotals.index.tolist()
        M = len(x_values)

        # create a bar plot for each CRN stacked on the previous one
        b = M*[0]
        for j, CourseNumber in enumerate(stack):

            current_data = stackedData[stackedData["CourseNumber"] == CourseNumber].groupby("Date", sort=False).sum()

            y_values = current_data.Enrollment.tolist()
            ax.bar(x_values,
                   y_values,
                   bottom = b,
                   label = CourseNumber,
                   color = colors[j],
                   linewidth = 1,
                   edgecolor = ["white"]*M)
            b = [sum(y) for y in zip(b, y_values)]

        w_values = stackedDataTotals.Wait.tolist()

        # add bar for wait list
        ax.bar(x_values,
               w_values,
               bottom = b,
               linewidth = 1,
               label = "Wait List",
               color = "#D3D3D3",
               edgecolor = ["white"]*M)

        # set a title for the figure
        ax.set(xlabel="Date",
               ylabel="Enrollment",
               title="Enrollment for {:s}".format(course))


        # set max on y to make graphs comparable if less that 45
        # highest value needs to include the wait list
        plt.ylim(0,max(maxenrollment, max([sum(y) for y in zip(b, w_values)]))+5)

        # set maximum enrollment based on room capacity
        plt.plot([min(x_values), max(x_values)],[maxenrollment, maxenrollment],'--', color = "gray")

        # include a legend of all the CRNs
        plt.legend(loc="upper left")

        # create filename and save the graph as a PDF
        figname = current_path + "/graphs/" + course.replace("/","_") + ".pdf"
        plt.savefig(figname)
        plt.close(fig)
