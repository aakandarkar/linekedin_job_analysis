

url = "https://www.linkedin.com/jobs/search/?currentJobId=3566989713&f_JT=F&geoId=103644278&keywords=electrical%20engineer&location=United%20States&refresh=true"

def get_domain(url):
    regex = r"&keywords=(.*?)&location"
    matches = re.search(regex, url)
    if matches:
        return matches.group(1).replace("%20","_")
    else:
        print("Domain not foudn in URL, enter domain(ex: data_science): ")
        domain = input()
        return domain

