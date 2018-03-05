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
import getpass
# import urllib
import urllib.request
import urllib.parse
# from splinter import Browser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from robobrowser import RoboBrowser
from bs4 import BeautifulSoup as bs


def go_urllib():
    print("go_urllib: start")
    urllib.request.urlretrieve("https://sso.godaddy.com/login", "somefile.html", lambda x, y, z: 0,
                               urllib.parse.quote_plus({"username": "xxx", "password": "pass"}))
    return


def go_robo_browser():
    print("go_robo_browser: start")
    browser = RoboBrowser(history=True)
    # browser.open('https://m.facebook.com/')
    browser.open("https://sso.godaddy.com/login/")

    # GETTING INPUT
    # mail = input('input username: ')
    # password = getpass('input password: ')
    # getpass.getpass(prompt='What is your favorite color? ')

    # FORM FILL
    # form = browser.get_form(action='/login')
    form = browser.get_form()

    if form is not None:
        # form["Username or Customer #"].value = mail
        form["Username or Customer #"] = 'name'
        form["Password"] = 'password'
        # form['pass'].value = password
        browser.submit_form(form)
        print(str(browser.select))
    else:
        print("Error: form is None")

    # PARSER (can also be implemented from robobrowser)
    # soup = browser.parsed
    # try:
    #     soup = soup.find("label", {"for": "u_0_0"})
    #     username = soup.a
    #     username.clear()
    #     username = str(username)
    #     profile = username[username.find('/') + 1: username.find('?')]
    #     print(profile)
    # except Exception:
    #     print("wrong credentials!")
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


def go_twitter():
    browser = RoboBrowser()
    browser.open('http://twitter.com')

    # Get the signup form
    signup_form = browser.get_form(class_='signup')
    # signup_form  # <RoboForm user[name]=, user[email]=, ...

    # Inspect its values
    # signup_form['authenticity_token'].value = '6d03597'

    # Fill it out
    signup_form['user[name]'].value = 'python-robot'
    signup_form['user[user_password]'].value = 'secret'

    # Serialize it to JSON
    signup_form.serialize()  # {'data': {'authenticity_token': '6d03597...',
    #  'context': '',
    #  'user[email]': '',
    #  'user[name]': 'python-robot',
    #  'user[user_password]': ''}}

    # And submit
    browser.submit_form(signup_form)
    return


def main():
    # go_robo_browser()
    # html = tracker('1234567891234567')
    # print(html)
    # go_urllib()
    go_robo_browser()
    # go_twitter()
    return


if __name__ == '__main__':
    main()
