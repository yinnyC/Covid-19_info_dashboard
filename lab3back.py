# Project Name: CIS 41B - Lab 3:  web scraping and data storage with requests, beautifulsoup, sqlite3
# Name :        Yin Chang
# Discription:  Write an application that lets the user search for Covid-19 data of countries of the world
# Module:       lab3back.py
# Discription:  will produce a JSON file and an SQL database file

import requests
from bs4 import BeautifulSoup
import re
import json
import sqlite3
import string
import os

'''-------------------Scrapind Data from webpage and Storing into JSON file --------------------'''

# Define a Global variable to hold URL
dataURL = "https://www.worldometers.info/coronavirus/"
"""
# Download the webpage
try:
    page = requests.get(dataURL, timeout=3)
    page.raise_for_status()
except requests.exceptions.HTTPError as e:
    print("HTTP Error:", e)
except requests.exceptions.ConnectionError as e:
    print("Error Connecting:", e)
except requests.exceptions.Timeout as e:
    print("Timeout Error:", e)
except requests.exceptions.RequestException as e:
    print("Request exception: ", e)

# Parsing & Organizing Data
soup = BeautifulSoup(page.content, "lxml")
headings = []  # A container to hold headings in the table
data = []     # A container to hold contents in the table

# Read in headings
table = soup.table
table_head = table.find('thead')
table_headrows = table_head.find_all('th')
for row in table_headrows:
    cols = row.text.strip()
    headings.append(cols)

# Fix the messy data
headings = [elem.replace(',', '')
            for elem in headings]  # Remove the "," sign in data
headings = [elem.replace('/', '')
            for elem in headings]  # Remove the "/" sign in data
headings = [elem.replace(' ', '')
            for elem in headings]  # Remove the space in data
headings.pop(0)                                         # Remove the "#" column
headings[0] = "Country"
headings[-3] = "Tests1Mpop"
headings[-6] = "TotalCases1Mpop"


# Read in body content
table_body = table.find('tbody')
table_bodyrows = table_body.find_all('tr')
for row in table_bodyrows:
    cols = row.find_all('td')
    # Remove Extra Spaces,newline and the serial number
    cols = [elem.text.strip() for elem in cols[1:]]
    # Remove the "+" sign
    cols = [elem.strip("+") for elem in cols]
    # Remove the "," sign
    cols = [elem.replace(',', '') for elem in cols]
    # Replace null value & N/A with 0
    cols = ['0' if len(elem) == 0 or elem == "N/A" else elem for elem in cols]
    # Covert the number to int type
    cols = [int(elem) if elem.isdigit() else elem for elem in cols]
    data.append(cols)

# Data Cleaning
data.pop(6)  # The 7th line of data doesn't make sense

# Write in the data into JSON file
with open('downloadedData.json', 'w') as fh:
    json.dump((headings, data), fh, indent=3)
"""

'''------------------- Storing Data into lab3.db --------------------'''
# Read in the data from JSON file

filepath = os.path.dirname(__file__)
# Contains all the CA community college names
DownloadedData = os.path.join(filepath, "downloadedData.json")
with open(DownloadedData, 'r') as fh:
    readinJson = json.load(fh)

headings = readinJson[0]
covid19Data = readinJson[1]

# Create the database
conn = sqlite3.connect('lab3.db')
cur = conn.cursor()

# Create the covid19Update Table and set up columns names
cur.execute("DROP TABLE IF EXISTS covid19Update")
cur.execute('''CREATE TABLE covid19Update(             
                   "{}" TEXT NOT NULL PRIMARY KEY)'''.format(headings[0],))
for i in range(1, len(headings)-1):
    cur.execute('''ALTER  TABLE  covid19Update  
                   ADD COLUMN "{}" INTEGER'''
                .format(headings[i],))
cur.execute(
    '''ALTER  TABLE  covid19Update ADD COLUMN "{}" TEXT''' .format(headings[-1],))

# Insert data into covid19Update Table
for record in covid19Data:
    cur.execute(
        '''INSERT INTO covid19Update VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (*record[:],))

conn.commit()  # Save the change
