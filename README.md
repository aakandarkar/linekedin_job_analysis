# linekedin_job_analysis

Steps
1) #install all required packages for the project,
>pip install requriement.txt,

2) enter login details in config.yaml file
    -linkedin username
    -linkedin password
    -job urls you want to scrape
3) run /Scrapers/crwaler.py  (usual time to scrape one url is 2 hrs)

4) check files in /Data/ and check the names of files to be used in next step 
    (Instead of orignal database I have used CSV files here)

5) run /Data_Cleaning/cleaning.py to clean data and pull all data into all_data.csv file

6) run /Dashboard/dashboard.py to display dashboard.
