# cbs_course_review_analysis

Our final Intro to Python lecture at Columbia Business School, which took place last night, covered web scraping. It inspired me to build a web scraper program (course_ratings_scraper.py) that searched through all Summer 2020, Fall 2020, and Spring 2021 courses on cbscoursereview.com . The program created a .csv file with course difficulty and course ratings data for the ~123 Columbia Business School classes that had this data available. (I chose not to upload this .csv file to GitHub.)

In order to analyze this data, I created a second program (ratings_analysis.py) that loaded the .csv file into a DataFrame, performed multiple analyses of the data, then stored those analyses into .csv, .png, and .txt files. These analyses can be found on the program's GitHub page.

One of the more interesting findings from this analysis was that course difficulty ratings and course ratings were positively correlated, with a statistically significant coefficient of 0.2842 and an R^2 value of 0.154. This suggests that students prefer classes that challenge them more, although it's also possible that students work harder in classes that they enjoy. 

Another analysis (in which I estimated the difficulty ratings that correspond to various difficulty percentiles) may also be valuable for students, as difficulty percentile data is not listed on cbscoursereview.com. The analysis data suggests that a course with a difficulty rating of 7.6 would be harder/more intense than 90% of CBS classes, whereas a class with a difficulty rating of 5 would be harder than 35% of classes.

This project was a great way for me to practice the Python skills I've learned this semester. I am grateful to my Python professor (Mattan Griffel) for a great class experience, and I look forward to taking his databases class later this semester.
