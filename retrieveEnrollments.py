#!/usr/bin/env python3

from enrollmentUtils import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
# from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException
from private import USER, PASSWORD, CHROMEPATH, DEPTCODE
from time import sleep
from os import path, remove, rename
import argparse
import datetime as dt

def main(term,
         school,
         department,
         status,
         subject,
         campus,
         session,
         createmergefile,
         scheduletype,
         level):

# Initialize webdriver

# this is the chromedriver, not the chrome app
    driver = webdriver.Chrome(CHROMEPATH)
    actions = ActionChains(driver)

# Load our site

    driver.get("https://prod-ban-nav.msudenver.edu/applicationNavigator/seamless")
    sleep(3)
    if "Authentication" not in driver.title:
        raise WrongPageException

# Authenticate and login

    actions.reset_actions()
    actions.send_keys(USER)
    actions.send_keys(Keys.TAB)
    actions.send_keys(PASSWORD)
    actions.send_keys(Keys.RETURN)
    actions.perform()
    sleep(3)


# Head to the enrollment report

    if "Navigator" not in driver.title:
        raise WrongPageException
    assert "Navigator" in driver.title

# select the SWRCGSR query and wait for it to load
    actions.reset_actions()
    actions.send_keys("SWRCGSR")
    actions.send_keys(Keys.RETURN)
    actions.perform()
    sleep(12)

# don't change anything on this page, just click "GO"
    actions.reset_actions()
    actions.key_down(Keys.ALT)
    actions.send_keys(Keys.PAGE_DOWN)
    actions.perform()
    sleep(4)

# select printer and move to middle section
    actions.reset_actions()
    actions.send_keys("DATABASE")
    actions.key_down(Keys.ALT)
    actions.send_keys(Keys.PAGE_DOWN)
    actions.pause(0.2)
    actions.perform()

# input all of the values
    actions.reset_actions()
    actions.send_keys(Keys.TAB)
    actions.pause(0.1)
    actions.send_keys(term)
    actions.pause(0.1)
    actions.send_keys(Keys.DOWN)
    actions.pause(0.1)
    actions.send_keys(subject)
    actions.pause(0.1)
    actions.send_keys(Keys.DOWN)
    actions.pause(0.1)
    actions.send_keys(school)
    actions.pause(0.1)
    actions.send_keys(Keys.DOWN)
    actions.pause(0.1)
    actions.send_keys(department)
    actions.pause(0.1)
    actions.send_keys(Keys.DOWN)
    actions.pause(0.1)
    actions.send_keys(campus)
    actions.pause(0.1)
    actions.send_keys(Keys.DOWN)
    actions.pause(0.1)
    actions.send_keys(status)
    actions.pause(0.1)
    actions.send_keys(Keys.DOWN)
    actions.pause(0.1)
    actions.send_keys(session)
    actions.pause(0.1)
    actions.send_keys(Keys.DOWN)
    actions.pause(0.1)
    actions.send_keys(createmergefile)
    actions.pause(0.1)
    actions.send_keys(Keys.DOWN)
    actions.pause(0.1)
    actions.send_keys(scheduletype)
    actions.pause(0.1)
    actions.send_keys(Keys.DOWN)
    actions.pause(0.1)
    actions.send_keys(level)
    actions.pause(0.1)
    actions.perform()

# move to lower section
    actions.reset_actions()
    actions.key_down(Keys.ALT)
    actions.send_keys(Keys.PAGE_DOWN)
    actions.pause(0.2)
    actions.perform()

# save and wait for SQL query to complete
    actions.reset_actions()
    actions.send_keys(Keys.F10)
    actions.perform()
    sleep(1)

# open the Related tab and select first item which should be GJIREVO
    actions.reset_actions()
    actions.key_down(Keys.ALT)
    actions.key_down(Keys.SHIFT)
    actions.send_keys("r")
    actions.pause(0.2)
    actions.key_up(Keys.SHIFT)
    actions.key_up(Keys.ALT)
    actions.send_keys(Keys.DOWN)
    actions.send_keys(Keys.RETURN)
    actions.perform()


# we cannot do this dynamically so hopefully this is long enough
    sleep(45)


# wait until the file presents itself and then move to next input
    actions.reset_actions()
    actions.key_down(Keys.TAB)
    actions.perform()
    sleep(1)

# find the correct .lis file, select it, and export it
    actions.reset_actions()
    actions.key_down(Keys.F9)
    actions.pause(1)
    actions.send_keys(Keys.RETURN)
    actions.pause(1)
    actions.key_down(Keys.SHIFT)
    actions.key_down(Keys.F1)
    actions.pause(3)
    actions.perform()

    sleep(3)
    driver.close()

if __name__ == "__main__":

    ################################################################################
    # CHANGE THESE ACCORDINGLY
    infopath = "/Users/hbouwmee/Documents/Associate Chair/Schedule/Time Series/info.txt"
    filepath = "/Users/hbouwmee/Downloads/"
    ################################################################################


    # Set up command line parsing
    parser = argparse.ArgumentParser(
        description="Retrieve SWRCGSR data from BANNER databases."
    )
    parser.add_argument("-c", "--cancel", help="Include canceled classes", action="store_true")
    parser.add_argument("--excel", help="Provide formatted Excel output", action="store_true")
    args = parser.parse_args()

    # info.txt file is a plain text file that provides the parameters for the
    # report. At a minimum it must include the term(s) but all other variables are
    # optional.  The form of the file is the <variable> = <value>.  Note that the
    # term variable can be a list of comma separated term codes.
    #
    # Example:
    #
    #   term = 201940, 202030, 202040, 202050
    #   department = M&CS
    #   school = LA
    #   status = A
    #   createmergefile = N

    # check the info file exists
    path.exists(infopath)

    # parse the info file for the variable values
    info = text_parser(infopath)

    if args.cancel:
        status = "%"
    else:
        status = "A"

    # since there can be more than one term, loop through all of them
    for term in info["term"]:

        # remove existing file
        filename = "GJIREVO.csv"
        if path.exists(filepath + filename):
            remove(filepath + filename)

        main(term.strip(),
             info.get("school", "%"),
             info.get("department", "%"),
             status,
             info.get("subject", "%"),
             info.get("campus", "%"),
             info.get("session", "%"),
             info.get("createmergefile", "%"),
             info.get("scheduletype", "%"),
             info.get("level", "%"))

        # check to see if the file was downloaded
        assert path.exists(filepath + filename), "File does not exist: {:s}".format(filepath + filename)

        # parse the filename from the information in the csv file
        count = 0
        with open(filepath + filename, "r") as fp:
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

        rename(filepath + filename, filepath + newfilename)
        print()
        print("Report downloaded to {:s}".format(filepath + newfilename))

        # Provide formatted Excel output
        if args.excel:
            processEnrollment(filepath + newfilename)
            print("Report converted to Excel as {:s}".format(filepath + newfilename[:-3] + "xlsx"))

