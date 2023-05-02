import re
import os
import pandas as pd
import usaddress
import random


state_list = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA',
                          'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                          'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT',
                          'VA', 'WA', 'WV', 'WI', 'WY']

def extract_salary_range(s):
    if 'hr' in s:
        # if the salary is in hourly range
        value = random.randint(80, 200)
        random_value = value * 1000
        return random_value
    elif 'yr' in s:
        # if the salary is in yearly range
        pattern = r'\$([\d\,\.]+)\/yr.*\$([\d\,\.]+)\/yr'
    else:
        return 80000  # default salary if no salary range is found

    matches = re.search(pattern, s)
    if matches:
        # return the lowest salary in the range
        return min(float(matches.group(1).replace(',', '')),
                   float(matches.group(2).replace(',', '')))
    else:
        return 80000  # default salary if no salary range is found

def get_experience_level(s):
    if 'Entry level' in s:
        return 'Entry level'
    elif 'Mid-Senior level' in s:
        return 'Mid-Senior level'
    elif 'Associate' in s:
        return 'Associate'
    else:
        return 'Entry level'

def get_state(location):
    try:
        parsed = usaddress.parse(location)
        state = next((p[0] for p in parsed if p[1] == 'StateName'), None)
        if state:
            return state
        else:
            return random.choice(state_list)
    except:
        return random.choice(state_list)
def get_file_names(folder_path,extention):
    dir_list = os.listdir(folder_path)
    file_list = []
    for file in dir_list:
        if file.endswith(extention) and file != "all_data.csv":
            file_list.append(file)
    return file_list

def get_domain_name(filename):
    name, ext = os.path.splitext(filename)
    name = name.replace('_', ' ')
    return name


list_of_files = get_file_names("/Users/akashkandarkar/Desktop/ischool_linkedin_project/Data/",".csv")
first = True
for file in list_of_files:
    ds_df = pd.read_csv('/Users/akashkandarkar/Desktop/LInkedInScraping/code/Data/'+file, header=None)
    ds_df.columns = ['job_title', 'company_name','company_location','work_method','post_date','job_details','link','job_desc','posted_rank']
    # extract salary, job type,experience level,state, and domain from the job_details column
    ds_df['salary'] = ds_df['job_details'].apply(extract_salary_range)
    ds_df['job_type'] = ds_df['job_details'].apply(lambda s: s.split('¬')[1].strip() if len(s.split('¬')) > 1 else 'Full-time')
    ds_df['experience_level'] = ds_df['job_details'].apply(get_experience_level)
    ds_df['state'] = ds_df['company_location'].apply(get_state)
    ds_df['domain'] = get_domain_name(file)
    # print the first file dataframe with column names
    if first:
        ds_df.to_csv('/Users/akashkandarkar/Desktop/LInkedInScraping/code/Data/all_data.csv',mode='a', index=False)
        first = False
    # print the first file dataframe without column names
    else:
        ds_df.to_csv('/Users/akashkandarkar/Desktop/LInkedInScraping/code/Data/all_data.csv', mode='a', index=False, header=None)