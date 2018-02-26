"""
Script to download gtfs from MOT ftp and upload to S3 bucket.
To use the script create a config file. see example /conf/gtfs_download.config.example
Provide in command line args the path to config file
"""

from configparser import ConfigParser
from boto3.session import Session
from ftplib import FTP
import datetime
import time
import hashlib
import os
import argparse
import re
import pickle
import operator
import re
# from splinter import Browser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from robobrowser import RoboBrowser
from getpass import getpass
from bs4 import BeautifulSoup as bs


def go_robo_browser():
    browser = RoboBrowser(history=True)
    browser.open('https://m.facebook.com/')

    # GETTING INPUT
    mail = input('Email : ')
    password = getpass('Password : ')

    # FORM FILL
    form = browser.get_form()
    form['email'].value = mail
    form['pass'].value = password
    browser.submit_form(form)

    # PARSER (can also be implemented from robobrowser)
    soup = browser.parsed
    try:
        soup = soup.find("label", {"for": "u_0_0"})
        username = soup.a
        username.clear()
        username = str(username)
        profile = username[username.find('/') + 1: username.find('?')]
        print(profile)
    except:
        print("wrong credentials!")
    return


def fix_bad_unicode(el):
    return el.decode(None, 'utf8').encode('cp1252').decode('utf8')


def tracker(code):
    br = RoboBrowser(parser="lxml")
    br.open('http://track.nederlandwereldwijd.nl/')

    form = br.get_forms()[0]
    form['ctl00$plhMain$ddlCountry'].value = "China"
    form['ctl00$plhMain$ddlLanguage'].value = "English"
    br.submit_form(form)

    form = br.get_forms()[0]
    form['ctl00$plhMain$txtTrackingNo'].value = code
    br.submit_form(form)

    table = br.select("#ctl00_plhMain_result_table")
    return fix_bad_unicode(table[0])


def go_splinter():
    br = Browser()

    # Ignore robots.txt
    br.set_handle_robots(False)
    # Google demands a user-agent that isn't a robot
    br.addheaders = [('User-agent', 'Firefox')]

    # Retrieve the Google home page, saving the response
    br.open("http://google.com")

    # Select the search box and search for 'foo'
    br.select_form('f')
    br.form['q'] = 'foo'

    # Get the search results
    br.submit()

    # Find the link to foofighters.com; why did we run a search?
    resp = None
    for link in br.links():
        siteMatch = re.compile('www.foofighters.com').search(link.url)
        if siteMatch:
            resp = br.follow_link(link)
            break

    # Print the site
    content = resp.get_data()
    print (content)
    return


def main():
    # go_robo_browser()
    html = tracker('1234567891234567')
    print(html)
    return


if __name__ == '__main__':
    main()
