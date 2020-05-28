
import csv
import requests
import threading
from bs4 import BeautifulSoup

# request headers
global headers
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}

# encode and format
def format_properly(string):
    string = str(string.encode("utf8"))
    string = str(string.replace("\\n", "").replace("b'", "").replace("'", ""))
    return string
                        
class businessesforsale_com():
    def __init__(self, link, mode):
        categories_links = self.get_categories(link)
        self.scrape_category(categories_links, mode)
        
    # get all categories from categories page
    def get_categories(self, link):
        # make request and generate code soup
        page = requests.get(link, headers = headers, timeout=30)
        soup = BeautifulSoup(page.content, 'html.parser')

        # get each link
        categories_links = []
        for category in soup.find_all(class_='cats-sector'):
            category_link = category.find('a')
            categories_links.append(category_link['href'])

        return categories_links
    
    # start scraping a category
    def scrape_category(self, categories_links, mode):        
        for link in categories_links:
            lindex = 0
            while True:
                lindex += 1
                # get next link
                if lindex != 1:
                    link = link + "-" + str(lindex)
                    
                page = requests.get(link, headers = headers, timeout=30)
                soup = BeautifulSoup(page.content, 'html.parser')
                
                # break if no results found
                if len(soup.find_all(class_='result')) == 0:
                    break
                
                # get all result links
                results = []
                for res in soup.find_all(class_='result'):
                    # get the link for each result
                    for result_link in res.find_all('a'):
                        results.append(result_link['href'])
                        break
                
                # read current data
                with open("results.csv", "r", newline='') as resultsFile:
                    reader = csv.reader(resultsFile)
                    alldata = list(reader)
                    data = []
                    for d in alldata:
                        data.append(d[15])
                    resultsFile.close()
                    
                # process every result
                with open("changes.csv", "a", newline='') as changesFile:
                    # generate writer object for changes file
                    changesWriter = csv.writer(changesFile)
                    with open("results.csv", "a", newline='') as resultsFile:
                        # generate writer object for results file
                        csvWriter = csv.writer(resultsFile)
                        # open new thread for each result on the page
                        threads = []
                        for result in results:
                            thread = threading.Thread(target = self.scrape_result, args = (result, csvWriter, changesWriter, mode, data))
                            threads.append(thread)
                            thread.start()
                        # wait for all threads to execute
                        for thread in threads:
                            thread.join()
                        # close files
                        resultsFile.close()
                    changesFile.close()

    # scrape listing
    def scrape_result(self, result, csvWriter, changesWriter, mode, data):
        print(result)
        # make request and generate code soup
        page = requests.get(result, headers = headers, timeout=30)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # source
        source = "Businessesforsale.com"
        
        # state
        try:
            state = soup.find(attrs={"itemprop" : "addressRegion"}).text
        except:
            state = "n/a"
            
        # region  
        try:
            region = soup.find(attrs={"itemprop" : "addressLocality"}).text
        except:
            region = "n/a"
        
        try:
            # title
            title = format_properly(soup.find(attrs={"itemprop" : "name"}).text)
            
            # description
            description = format_properly(soup.find(class_ = "listing-section-content").text)
        except:
            # skip (add / franchise page)
            return
        
        # get business details
        real_estate = "n/a"
        reason = "n/a"
        employees = "n/a"
        year = "n/a"
        inventory = "n/a"
        ffe = "n/a"
        for inf in soup.find_all(class_ = 'listing-details'):
            for detail in inf.find_all('dt'):
                
                # real estate
                if "real estate" in detail.text.lower():
                    real_estate = format_properly(inf.find('p').text)
                # reason for selling
                elif "reasons for selling" in detail.text.lower():
                    reason = format_properly(inf.find('p').text)
                # number of employees
                elif "employees" in detail.text.lower():
                    employees = inf.find('dd').text
                # years established
                elif "years established" in detail.text.lower():
                    year = inf.find('dd').text
                # inventory
                elif "inventory" in detail.text.lower():
                    inventory = format_properly(inf.find('dd').text)
                # furniture / fixtures value
                elif "furniture / fixtures value" in detail.text.lower():
                    ffe = format_properly(inf.find('dd').text)
        
        # get asking price
        price = soup.find(class_ = 'price')
        price = format_properly(price.find('span').text)
        
        # sales revenue
        revenue = soup.find(id = 'revenue')
        revenue = format_properly(revenue.find('dd').text)
        
        # EBITDA
        ebitda = "n/a"
        
        # cash flow
        cash_flow = soup.find(id = 'profit')
        cash_flow = format_properly(cash_flow.find('dd').text)
        
        # contact
        contact = ''
        try:
            contact = soup.find(class_ = 'broker-details')
            contact = format_properly(contact.find('h4').text)
        except:
            contact = "n/a"
        
        # phone
        phone = "n/a"
        
        # write data to csv file
        # if mode is 'f' then changes will not be taken into consideration
        if mode.lower() == 'f':
            csvWriter.writerow([source, state, region, title, description, real_estate, reason, employees, year, price, revenue, ebitda, cash_flow, inventory, ffe, result, contact, phone])
        # if mode is 't' then only changes will be written to the output file
        else:
            listing_data = [source, state, region, title, description, real_estate, reason, employees, year, price, revenue, ebitda, cash_flow, inventory, ffe, result, contact, phone]
            if not result in data:
                changesWriter.writerow([source, state, region, title, description, real_estate, reason, employees, year, price, revenue, ebitda, cash_flow, inventory, ffe, result, contact, phone])
