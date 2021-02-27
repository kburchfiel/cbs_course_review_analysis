# Analysis of CBS course ratings and difficulty ratings from cbscoursereview.com
# Kenneth Burchfiel
# First uploaded to Github on 2/19/2021

# This progam takes the csv file created in course_ratings_scraper.py; performs various statistical
# analyses; and then exports those analyses to .txt, .csv, and .png files.

# I normally would have created a Jupyter notebook with this information, but wanted to keep the individual
# course rating data private.

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

# Analysis 1: Estimate the course difficulty ratings that correspond to various percentiles (from 5 to 95,
# in increments of 5), then save that information in .csv format.

print("Course difficulty percentiles:")
percentile_table = [] # This will become a list of dictionaries
for i in range (5, 100, 5):
    percentile_dict = {} # This dictionary will store the percentile-difficulty pair created by this
    # iteration of the for loop.
    percentile_dict['percentile'] = i
    percentile_dict['difficulty'] =  np.percentile(df_ratings['course_difficulty'],i) # The percentile is 
    # calculated with reference to all the ratings in the course_difficulty column in our DataFrame.
    percentile_table.append(percentile_dict) # Adds this dictionary to the list of dictionaries

df_difficulty_percentiles = pd.DataFrame(percentile_table) # Converts the list of dictionaries into a 
# DataFrame
df_difficulty_percentiles.set_index('percentile',inplace=True)
df_difficulty_percentiles.sort_values('difficulty',ascending=False,inplace=True) 
print(df_difficulty_percentiles)
df_difficulty_percentiles.to_csv('difficulty_percentiles.csv')

# Analysis 2: Create a scatter plot that displays the relationship between difficulty ratings and course
#  ratings, and include a best fit line. Then save the data to a .png file.

xset = df_ratings['course_difficulty']
yset = df_ratings['course_rating']
plt.scatter(xset,yset)
plt.plot(np.unique(xset), np.poly1d(np.polyfit(xset, yset, 1))(np.unique(xset))) # From user '1"' at 
# https://stackoverflow.com/a/31800660/13097194
plt.xlabel("Course difficulty") 
# https://www.kite.com/python/answers/how-to-add-axis-labels-to-a-plot-in-matplotlib-in-python
plt.ylabel("Course rating")
plt.title("Relationship between course difficulty and course rating")
plt.savefig('difficulty_rating_scatter.png')
plt.show() # Placing this line before plt.savefig caused plot.savefig to
# return a blank image. The show() statements can be commented out in order to
# prevent the program from pausing.

# Analysis 3: Display a histogram of course rating data, and also include the
# mean and standard deviation of that data on the histogram. Then save the
# histogram as a .png file.

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

# Analysis 5: Perform various regression analyses to better understand the
# relationship between difficulty ratings and course ratings, and output this
# analysis to a .txt file.

# First, I will create three additional columns for my df_ratings DataFrame.
# These columns will store course difficulty ratings raised to the second,
# third, and fourth power. I will then include these columns in my
# regression analyses in order to determine whether they add any explanatory
# power to my model. 
df_ratings['difficulty^2']=df_ratings['course_difficulty']**2
df_ratings['difficulty^3']=df_ratings['course_difficulty']**3
df_ratings['difficulty^4']=df_ratings['course_difficulty']**4

# Next, I will analyze four different regression models. I will first store each
# model and its corresponding name ('1_iv' for one independent variable, '2_iv'
# for two dependent variables, and so on) in a tuple. Next, I will add those
# tuples to a list (model_list).

model_list = []
model_tuple = ('1_iv', df_ratings['course_difficulty']) # Stores the regression model's name along with its
# independent variable(s). I used tuples instead of dictionaries to make it easier to access the model name later on.
model_tuple2 = ('2_iv', df_ratings[['course_difficulty', 'difficulty^2']])
model_tuple3 = ('3_iv', df_ratings[['course_difficulty', 'difficulty^2', 'difficulty^3']])
model_tuple4 = ('4_iv', df_ratings[['course_difficulty', 'difficulty^2', 'difficulty^3', 'difficulty^4']])
model_list.extend([model_tuple, model_tuple2, model_tuple3, model_tuple4])

# Next, I will perform a regression on each model; store the output of that
# model (along with its name) in a new tuple (results_tuple); then append that
# tuple to a list of results (results_list).

results_list = []
for model in model_list:
    print(f"Now testing a model.")
    x = model[1]
    y = df_ratings.course_rating
    x = sm.add_constant(x)
    results = sm.OLS(y, x).fit()
    results_tuple = (model[0], results) # I found a tuple to be more convenient than a dictionary here due
    # to its support for subscript operators
    results_list.append(results_tuple)
    
    
# I will now store the summary output for each regression, along with its name,
# into a text file. Code for exporting summary to a text file comes from Anton
# Taresenko (https://stackoverflow.com/a/53373860/13097194)
with open('difficulty_rating_regressions.txt', 'w') as fh: 
    for result in results_list:
        print(f"\n\nResults for the {result[0]} model:", file=fh) 
        # https://stackabuse.com/writing-to-a-file-with-pythons-print-function/
        fh.write(result[1].summary().as_text())

# The results of the regression (available within
# 'difficulty_rating_regressions.txt') indicate that the first model (with only
# one independent variable) performs just as well or better than the second and
# third models. Although the fourth model (with 4 independent variables) has the
# highest R^2 value, there is a possibility that the model is overfitting to the
# data. If I had more data points, I could try performing a 5-fold cross
# validation to better evaluate each model; however, for now, I will choose to
# use the one-variable model.

# My final analysis will be to determine the error value of my model's course
# rating prediction for each class. In my one-variable model, each class's predicted
# difficulty rating equals the model's intercept plus the product of the class's
# coefficient. 

# If a class's difficulty is seen as its 'cost'
# and its rating is seen as its quality, the error term (the discrepancy between
# its cost and its quality) reflects how much quality a student gets for the
# effort he or she puts into the class. In this case, the classes with the
# lowest error terms (i.e. -3) will offer the best value for students, and those with the
# highest error terms (i.e. 2) will offer the worst value.
# 

# First, I will extract the intercept and difficulty coefficients from my first
# model's regression results.

parameters = results_list[0][1].params 
# Retrieves the parameters from the second element (the results output) of the first tuple in results_list
#  (the one-variable model).
model_intercept = parameters[0]
model_difficulty_coeff = parameters[1]
print(model_intercept,model_difficulty_coeff)

# I will now create two news columns in my df_ratings DataFrame: (1) a
# 'prediction' column showing the rating my model predicts for each class, and
# (2) an 'error' column showing the discrepancy between my prediction and the
# actual rating. As discussed above, this error term also represents the 'value'
# a student gets from a given class.

df_ratings['prediction']=model_intercept + model_difficulty_coeff*df_ratings['course_difficulty']
df_ratings['error'] = df_ratings['prediction']-df_ratings['course_rating']
df_ratings.sort_values('error',inplace=True)
df_ratings

# Finally, I will export this expanded DataFrame to a new csv file so as not to
# overwrite the original DataFrame.
df_ratings.to_csv('course_ratings_expanded.csv')