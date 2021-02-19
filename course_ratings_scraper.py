# Course Ratings Scraper
# This Python program scrapes ratings information for recent Columbia Business School courses from cbscoursereview.com, stores them in a DataFrame, adds difficulty percentile information, then stores them in a CSV file for further analysis.
# By Kenneth Burchfiel (first uploaded to GitHub on 2/19/2021)

# As a relative newcomer to Python, I borrowed heavily from various resources in order to put this code together, including:
# https://stackoverflow.com/a/60165588/13097194
# https://www.scrapingbee.com/blog/selenium-python/
# https://stackoverflow.com/questions/3030487/is-there-a-way-to-get-the-xpath-in-google-chrome
# Lecture materials from my Python professor (Mattan Griffel)

import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import seaborn as sns
import lxml
import time
import numpy as np
from scipy import stats

# The first step is to determine which course IDs to look up on cbscoursereview.com. I can accomplish this by creating a list (course_ids), then filling that list with IDs for all courses listed on the CBS website in the last 3 semesters.
course_ids = []
# In order to fill the list, I will create a list of soups, then go through this list in order to gather course IDs.
souplist = []
response1 = requests.get('https://www8.gsb.columbia.edu/courses/mba/2021/Spring')
soup1 = BeautifulSoup(response1.text, features='lxml')
time.sleep(2)
response2 = requests.get('https://www8.gsb.columbia.edu/courses/mba/2020/Fall')
soup2 = BeautifulSoup(response2.text, features='lxml')
time.sleep(2)
response3 = requests.get('https://www8.gsb.columbia.edu/courses/mba/2020/Summer')
soup3 = BeautifulSoup(response3.text, features='lxml')
souplist.extend([soup1, soup2, soup3])

# Now that I have my list of soups, I can go through each soup and add all new course ids to my course_ids list.
for soup in souplist:
    courses = soup.find_all(class_='mba-course')
    for i in range(0,len(courses)): 
        course_id_result = courses[i].find('a').text
        course_id = course_id_result.split('-')[0] # Keeps only the first part of course_id_result, which contains the actual course ID.
        if course_id not in course_ids: # Prevents the program from adding duplicate ids into the list
            course_ids.append(course_id)
            # print(course_id)
print(f"{(len(course_ids))} courses loaded into course list.")

# Now that I have my list of course ids, I can use them to look up various courses on cbscoursereview.com.
# Because cbscoursereview.com is password protected, I needed to use Selenium in order to enable the program to log into the website.
driver = webdriver.Firefox() # I needed to download geckodriver.exe and add it to my PATH folder in Windows for this to work.
driver.get('http://cbscoursereview.com/index.php?page=login')

# Getting my cbscoursereview.com username and password from another folder
with open('..\\pwds\\em.txt') as file: 
    email = file.read()
with open('..\\pwds\\pw.txt') as file: 
    password = file.read()

# Logging into cbscoursereview.com using Selenium
login = driver.find_element_by_name("userid").send_keys(email)
password = driver.find_element_by_name("password").send_keys(password)
submit = driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/form/ul/li[3]/input[2]').click() # Used Web Inspector in Chrome to copy the XPath (for the Login button)

# Now that the program has logged into Selenium, it can begin to access ratings information. For each course ID in my list, the for loop below accesses the course's corresponding URL; adds course information into a dictionary; and then adds that dictionary into a list of dictionaries (called ratings_table) that will be converted into a DataFrame. 
ratings_table = []
for i in range(0,len(course_ids)): # Using an integer makes it easier to test changes to the loop, as it's possible to set the range to just 3 or 4 courses rather than all of them. 
    driver.get('http://cbscoursereview.com/index.php?page=courseinfo&courseid='+course_ids[i]) # Conveniently, each course's URL ends with its course ID, so accessing the URL is relatively simple.
    time.sleep(2) # Helps ensure that the scraper does not overload the server
    ratings_info = {} # This dictionary will store the information gathered for this URL. Each ratings_info dictionary will become a row in the DataFrame.
    textblock = driver.find_element_by_xpath("/html/body/div/div[1]/div[3]/p").text # This is the path that contains the text "This course has not yet been rated" in courses that don't yet have ratings data on cbscoursereview.
    if "not yet been rated" in textblock: # Without this line, the scraper will stop once it fails to find the elements below for courses that don't yet have ratings information.
        print("Not enough ratings--moving on to next course")
        continue # Goes back to the for loop so that the code can access the next course
    else: # i.e. if ratings information is indeed present on the webpage
        print(f"Now analyzing {course_ids[i]} (course {i} of {len(course_ids)})") # This program takes a while to run (about 20 minutes on my computer), so it's helpful to output a progress update in the terminal.
        course_name = driver.find_element_by_xpath('/html/body/div/div[1]/div[3]/h2').text # I used a web inspector to figure out where relevant text was located on each page.
        course_name = course_name.split(':') # Course names appear on the website as course_id: course name: additional part of course name (if present). Since I only want to store the course name, I added in code to remove the course_id from the course name. First, I split the name wherever a colon appeared.
        course_name = course_name[1:] # Next, I stored only the text after the course ID within the course name.
        delimiter = ':'
        course_name = delimiter.join(course_name) # I then joined together all parts of the course name into one string.
        course_name = course_name.strip() # Finally, I removed extra spaces from the course name.
        course_rating_text = driver.find_element_by_xpath("/html/body/div/div[1]/div[3]/table[1]/tbody/tr[1]/td[2]").text # Xpath is for the <img src="graphs..."> element, within which is the course ratings data
        course_difficulty_text = driver.find_element_by_xpath("/html/body/div/div[1]/div[3]/table[1]/tbody/tr[3]/td[2]").text
        course_rating_components = course_rating_text.split('/') # Removes extra text from course_rating
        course_rating = course_rating_components[0].strip()
        course_difficulty_components = course_difficulty_text.split('/') # Removes extra text from course_difficulty
        course_difficulty = course_difficulty_components[0].strip()
        # print(course_rating) # for debugging
        # print(course_difficulty) # for debugging
        ratings_info['course_id']=course_ids[i] # Now that I've gathered the course information I wanted from the webpage, I can store it in the ratings_info dictionary for that course.
        ratings_info['course_name']=course_name
        ratings_info['course_rating']=float(course_rating) # The course_rating and course_difficulty values aren't stored as numbers by default, hence the float() operation.
        ratings_info['course_difficulty']=float(course_difficulty)
        ratings_table.append(ratings_info) # Adds this course's dictionary into our table of all course information
# Debug code:
# print(ratings_table)
# for rating in ratings_table:
#     print(rating)
#     print(rating['course_rating']*10) # Makes sure the course rating is now a float
#     print(rating['course_difficulty']*10)

df_ratings = pd.DataFrame(ratings_table) # Converts the ratings table into a DataFrame
df_ratings.set_index('course_id',inplace=True)
pd.set_option('display.max_rows',1000) # Instructs the terminal to display more rows than normal

# I also wanted to determine the difficulty percentile for each course. The following code compares each course_difficulty value with all the values in the course_difficulty column to determine its percentile, then adds that percentile to a list (difficulty_percentiles). Finally, it adds those percentiles to the DataFrame as a new column.
difficulty_percentiles = []
for difficulty in df_ratings['course_difficulty']:
    percentile_value = stats.percentileofscore(df_ratings['course_difficulty'],difficulty,kind='mean') # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.percentileofscore.html
    print(percentile_value)
    difficulty_percentiles.append(percentile_value)
df_ratings['difficulty_percentile'] = difficulty_percentiles

print(df_ratings)
df_ratings.to_csv('course_ratings.csv')

# It would not be ideal to perform further data analysis on df_ratings in this program, since I would need to run the scraper again, wasting time and bandwidth. Instead, I created a new program to analyze this data.