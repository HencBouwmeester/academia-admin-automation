#!/bin/bash/env python3

# This is the both the headers and the associated line pattern of SWRCGSR output in Banner 9
HEADER_ROW = {
    "Subject": 5,
    "Number": 5,
    "CRN": 6,
    "Section": 4,
    "S": 2,
    "Campus": 4,
    "T": 2,
    "Title": 16,
    "Credit": 7,
    "Max": 5,
    "Enrolled": 5,
    "WCap": 5,
    "WList": 5,
    "Days": 8,
    "Time": 12,
    "Loc": 8,
    "Rcap": 5,
    "Full": 5,
    "Begin/End": 12,
    "Instructor": 19,
}

def write_and_format(input_list, output_name):
    """Take in a list of lists for output data and write an xlsx file.

    Args:
        input_list:
            input data (a list of lists) of output to write.
        output_name:
            a filename to write out to.

    Returns:
        Nothing.
    """

    import xlsxwriter

    # Initialize the xlsx file
    workbook = xlsxwriter.Workbook(output_name, {"strings_to_numbers": True})
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({"bold": True})

    # Process the data
    rowCount = 0
    for row in input_list:
        if rowCount == 0:
            colCount = 0
            for column in row:
                worksheet.write(rowCount, colCount, column, bold)
                colCount += 1
        else:
            colCount = 0
            for column in row:
                # force Excel to see the course and section numbers as text
                if colCount == 3 or colCount == 1:
                    column = '="' + column + '"'
                worksheet.write(rowCount, colCount, column)
                colCount += 1
        rowCount += 1

    # Set up for easy scrolling
    worksheet.freeze_panes(1, 0)

    # Format column widths
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
        rowCount - 1,  # last row
        10,  # column K
        {"type": "formula", "criteria": "=$K2>0.94*$J2", "format": format4},
    )

    # classes that have enrollment above 80% of capacity
    worksheet.conditional_format(
        1,  # row 2
        10,  # column K
        rowCount - 1,  # last row
        10,  # column K
        {"type": "formula", "criteria": "=$K2>0.8*$J2", "format": format3},
    )

    # classes that have enrollment below 10 students
    worksheet.conditional_format(
        1,  # row 2
        10,  # column K
        rowCount - 1,  # last row
        10,  # column K
        {"type": "formula", "criteria": "=$K2<10", "format": format1},
    )

    # classes that have students on the waitlist
    worksheet.conditional_format(
        1,  # row 2
        12,  # column M
        rowCount - 1,  # last row
        12,  # column M
        {"type": "cell", "criteria": ">", "value": 0, "format": format2},
    )

    # Close it out
    workbook.close()
    return

# utility to parse the info.txt file
def text_parser(filepath, separator="="):
    return_dict = {}
    with open(filepath, "r") as f:
        for line in f:
            line = line.rstrip().split(separator)
            items = line[1].split()
            if line[0].strip() == "term":
                return_dict[line[0].strip()] = line[1].split(",")
            elif len(items) > 1:
                return_dict[line[0].strip()] = items
            else:
                return_dict[line[0].strip()] = items[0]
    return return_dict


# convert time format from 12hr to 24hr and account for TBA times
def convertAMPMtime(timeslot):

    try:
        starthour = int(timeslot[0:2])
        endhour = int(timeslot[5:7])
        if timeslot[-3:-1] == "PM":
            starthour = starthour + 12 if starthour < 11 else starthour
            endhour = endhour + 12 if endhour < 12 else endhour
        timeslot = str(starthour).zfill(2) + ":" + \
                      timeslot[2:4] + "-" + \
                      str(endhour).zfill(2) + ":" + timeslot[7:9]
    except ValueError: # catch the TBA times
        timeslot = timeslot[:-1]

    return timeslot

def alternating_size_chunks(iterable, steps):
    """Break apart a line into chunks of provided sizes

    Args:
        iterable: Line of text to process.
        steps: Tuple of int sizes to divide text, will cycle.

    Returns:
        Return a generator that yields string chunks of the original line.
    """

    from itertools import cycle

    n = 0
    step = cycle(steps)
    while n < len(iterable):
        try:
            next_step = next(step)
        except StopIteration:
            continue
        yield iterable[n : n + next_step]
        n += next_step

