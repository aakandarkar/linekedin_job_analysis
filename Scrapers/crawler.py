from selenium.webdriver.common.by import By
import yaml
import re
from selenium import webdriver
import time
from tqdm import tqdm
import pandas as pd
import traceback

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

with open('config.yaml') as f:
    var = yaml.safe_load(f)

def get_domain(url):
    regex = r"&keywords=(.*?)&location"
    matches = re.search(regex, url)
    if matches:
        return matches.group(1).replace("%20","_")
    else:
        print("Domain not foudn in URL, enter domain(ex: data_science): ")
        domain = input()
        return domain

#login to Linekdin using login details from config.yamal file.
driver.get("https://linkedin.com/uas/login")
driver.find_element("xpath", '//*[@id="username"]').send_keys(var['username'])
driver.find_element("xpath", '//*[@id="password"]').send_keys(var['password'])
time.sleep(1)
driver.find_element("xpath", '//*[@id="organic-div"]/form/div[3]/button').click()
driver.get(var['url'])
links = []

print('Links collecting now.')
try:
    for page in tqdm(range(2, var['total_pages'])):
        time.sleep(1)
        jobs_block = driver.find_element(By.CLASS_NAME, 'jobs-search-results-list')
        jobs_list = jobs_block.find_elements(By.CLASS_NAME, 'jobs-search-results__list-item')
        for job in jobs_list:
            all_links = job.find_elements(By.TAG_NAME, 'a')
            for a in all_links:
                if str(a.get_attribute('href')).startswith("https://www.linkedin.com/jobs/view") and a.get_attribute('href') not in links:
                    links.append(a.get_attribute('href'))
                else:
                    pass
            driver.execute_script("arguments[0].scrollIntoView();", job)
        driver.find_element(
            "xpath", f"//button[@aria-label='Page {page}']").click()
except Exception:
    traceback.print_exc()
print('Found ' + str(len(links)) + ' links for job offers')

# Create empty lists to store information
job_titles = []
company_names = []
company_locations = []
work_methods = []
post_dates = []
work_times = []
job_desc = []

i = 0
j = 1

for url in tqdm(links):
    time.sleep(2)
    try:
        driver.get(url)
        driver.find_element("xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[2]/footer').click()
        time.sleep(1)
    except Exception:
        pass
    try:
        driver.find_element("xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[4]/footer').click()
        time.sleep(2)
    except:
        pass
    try:
        job_titles.append(driver.find_element("xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/h1').text)
    except Exception:
        job_titles.append('unknown')

    try:
        company_names.append(driver.find_element("xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[1]/span[1]/span[1]').text)
    except Exception:
        company_names.append('unknown')

    try:
        company_locations.append(driver.find_element("xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[1]/span[1]/span[2]').text)
    except Exception:
        company_locations.append('unknown')

    try:
        work_methods.append(driver.find_element(By.XPATH, "//div//span[@class='jobs-unified-top-card__workplace-type']").text)
    except Exception:
        work_methods.append('unknown')

    try:
        post_dates.append(driver.find_element("xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[1]/span[2]/span[1]').text)
    except Exception:
        post_dates.append('unknown')

    try:
        work_times.append(driver.find_element(By.XPATH, "//div[@class ='mt5 mb2']//li[1]").text)
    except Exception:
        work_times.append('unknown')
    try:
        job_description = driver.find_elements(By.CLASS_NAME, 'jobs-description__content')
        for description in job_description:
            job_text = description.find_element(By.CLASS_NAME, "jobs-box__html-content").text
            job_desc.append(job_text)
    except:
        job_desc.append('No description found')

    j += 1


print("Total Jobs Scraped: ",j)
df = pd.DataFrame(list(zip(job_titles, company_names,
                           company_locations, work_methods,
                           post_dates, work_times, links, job_desc)),
                  columns=['job_title', 'company_name',
                           'company_location', 'work_method',
                           'post_date', 'work_time', 'job_links', 'job_desc'])

d = {"minutes ago": 1,"minute ago": 1, "hour ago" : 60, "hours ago": 60,"day ago" : 3600,"days ago": 3600,"week ago": 4000,"weeks ago": 4500,"month ago": 7900,
     "months ago": 8900,"unknown":10000}
df["sortvalue"] = 1
for i in range(len(df)):
    x = df.iloc[i,4].split(" ",1)
    if (len(x)==1):
        x[0] = 10000
        x.append( "unknown")
    df.iloc[i,-1] = int(x[0])*d[x[1]]

df = df.sort_values('sortvalue')
domain = get_domain(var['url'])
df.to_csv('../Data/'+domain+'.csv',mode='a', index=False, header=None)
