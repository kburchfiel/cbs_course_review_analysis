# Analysis of CBS course ratings and difficulty ratings from cbscoursereview.com
# Kenneth Burchfiel
# First uploaded to Github on 2/19/2021

# This progam takes the csv file created in course_ratings_scraper.py and performs various statistical analyses, then exports those analyses to .txt, .csv, and .png files.

# I normally would have created a Jupyter notebook with this information, but wanted to keep the individual course rating data private.

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import statsmodels.api as sm

# The first step is to read the csv generated in course_ratings_scraper.py into a DataFrame.
df_ratings = pd.read_csv('course_ratings.csv',index_col='course_id')
pd.set_option('display.max_rows',1000)
df_ratings.sort_values('course_rating',ascending=False,inplace=True)
# print(df_ratings)

# Analysis 1: Estimate the course difficulty rating that corresponds to various percentiles (from 5 to 95, in increments of 5), then save that information in .csv format.

print("Course difficulty percentiles:")
percentile_table = [] # This will become a list of dictionaries
for i in range (5, 100, 5):
    percentile_dict = {} # This dictionary will store the percentile-difficulty pair created by this iteration of the for loop.
    percentile_dict['percentile'] = i
    percentile_dict['difficulty'] =  np.percentile(df_ratings['course_difficulty'],i) # The percentile is calculated with reference to all the ratings in the course_difficulty column in our DataFrame.
    percentile_table.append(percentile_dict) # Adds this dictionary to the list of dictionaries

df_difficulty_percentiles = pd.DataFrame(percentile_table) # Converts the list of dictionaries into a DataFrame
df_difficulty_percentiles.set_index('percentile',inplace=True)
df_difficulty_percentiles.sort_values('difficulty',ascending=False,inplace=True) 
print(df_difficulty_percentiles)
df_difficulty_percentiles.to_csv('difficulty_percentiles.csv')

# Analysis 2: Create a scatter plot that displays the relationship between difficulty ratings and course ratings, and include a best fit line. Then save the data to a .png file.

xset = df_ratings['course_difficulty']
yset = df_ratings['course_rating']
plt.scatter(xset,yset)
plt.plot(np.unique(xset), np.poly1d(np.polyfit(xset, yset, 1))(np.unique(xset))) # From user '1"' at https://stackoverflow.com/a/31800660/13097194
plt.xlabel("Course difficulty") # https://www.kite.com/python/answers/how-to-add-axis-labels-to-a-plot-in-matplotlib-in-python
plt.ylabel("Course rating")
plt.title("Relationship between course difficulty and course rating")
plt.savefig('difficulty_rating_scatter.png')
plt.show() # Placing this line before plt.savefig caused plot.savefig to return a blank image

# Analysis 3: Display a histogram of course rating data, and also include the mean and standard deviation of that data on the histogram. Then save the histogram as a .png file.

mean_text = "Mean: "+str(round(np.mean(df_ratings['course_rating']),2))
stdev_text = "Stdev: "+ str(round(np.std(df_ratings['course_rating']),2))
plt.hist(df_ratings['course_rating'],bins=20)
plt.xlabel("Course rating")
plt.ylabel("Number of courses")
plt.title("Course rating distribution")
plt.text(5, 12, mean_text)
plt.text(5, 10.5, stdev_text)
plt.savefig('course_rating_histogram.png')
plt.show()

# Analysis 4: Do the same as in Analysis 3, but with course difficulty data.

mean_text = "Mean: "+str(round(np.mean(df_ratings['course_difficulty']),2))
stdev_text = "Stdev: "+ str(round(np.std(df_ratings['course_difficulty']),2))
plt.hist(df_ratings['course_difficulty'],bins=20)
plt.xlabel("Course difficulty")
plt.ylabel("Number of courses")
plt.title("Course difficulty distribution")
plt.text(3, 20, mean_text)
plt.text(3, 18.5, stdev_text)
plt.savefig('course_difficulty_histogram.png')
plt.show()


# Analysis 5: Perform a regression analysis to better understand the relationship between difficulty ratings and course ratings, and output this analysis to a .txt file.

import statsmodels.api as sm
x = df_ratings.course_difficulty
y = df_ratings.course_rating
x = sm.add_constant(x)
results = sm.OLS(y, x).fit()
print(results.summary())
#export_summary = results.summary.Summary()
#export_summary.as_text()

# Code for exporting summary to a text file comes from Anton Taresenko (https://stackoverflow.com/a/53373860/13097194)
with open('difficulty_rating_regression.txt', 'w') as fh:
    fh.write(results.summary().as_text())

