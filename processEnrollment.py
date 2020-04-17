#!/usr/bin/env python3

from enrollmentUtils import *
import csv

def processEnrollment(filename):
    """Take in SWRCGSR output and format into usable excel-compatible format.

    Args:
        filename:
            input filename (full path optional) of txt format SWRCGSR output.

    Returns:
        Nothing.
    """

    newfile = []

    # SWRCGSR headers and spacer row
    newfile.append(HEADER_ROW.keys())

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
            if newlist[14] == 12*" ":
                continue
            if newlist[2][0] == " ":
                continue
            if newlist[0].strip()[:3] in ["---", "Sub", "Ter", "** "]:
                continue

            # convert time format from 12hr to 24hr and account for TBA times
            newlist[14] = convertAMPMtime(newlist[14])

            # remove leading and trailing whitespace
            newlist = [i.strip() for i in newlist]

            # Add the entry to our output list
            newfile.append(newlist)

    # Send it to the output function
    write_and_format(newfile, filename[:-3]+"xlsx")

    # Finish
    return

if __name__ == "__main__":

    import argparse
    from os import path, remove, rename
    import datetime as dt

    # Set up command line parsing
    parser = argparse.ArgumentParser(
        description="Process SWRCGSR data as Excel."
    )
    parser.add_argument("filename", help="Input file (text saved from SWRCGSR output)")
    args = parser.parse_args()

    filename = args.filename
    # check to see if the file was downloaded
    assert path.exists(filename), "File does not exist: {:s}".format(filename)

    # parse the filename from the information in the csv file
    count = 0
    with open(filename, "r") as fp:
        for line in fp:
            count += 1
            if count < 8:
                if count == 5:
                    items = line.split()
                    reportName = items[0].strip()
                    reportDate = dt.datetime.strptime(items[6][:-1].strip(), "%d-%b-%Y")
                if count == 7:
                    items = line.split()
                    reportTerm = items[1].strip()
            else:
                break

    newfilename = "{:s}_{:s}_{:s}.csv".format(reportName,
                                              reportTerm,
                                              dt.datetime.strftime(reportDate, "%Y%m%d"))

    rename(filename, newfilename)
    print("Report renamed as {:s}".format(newfilename))

    processEnrollment(newfilename)
    print("Report converted to Excel as {:s}".format(newfilename[:-3] + "xlsx"))
