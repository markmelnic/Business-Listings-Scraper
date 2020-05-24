
import csv
import requests
from bs4 import BeautifulSoup

global headers
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}

def format_properly(string):
    string = str(string.encode("utf8"))
    string = str(string.replace("\\n", "").replace("b'", "").replace("'", ""))
    return string
                        
class businessesforsale_com():
    def __init__(self, link):
        categories_links = self.get_categories(link)
        self.scrape_category(categories_links)
        
    def get_categories(self, link):
        page = requests.get(link, headers = headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        categories_links = []
        for category in soup.find_all(class_='cats-sector'):
            category_link = category.find('a')
            categories_links.append(category_link['href'])

        return categories_links
    
    def scrape_category(self, categories_links):        
        for link in categories_links:
            lindex = 0
            while True:
                lindex += 1
                # get next link
                if lindex != 1:
                    link = link + "-" + str(lindex)
                    
                page = requests.get(link, headers = headers)
                soup = BeautifulSoup(page.content, 'html.parser')
                
                # break if no results found
                if len(soup.find_all(class_='result')) == 0:
                    break
                
                # get all result links
                results = []
                for res in soup.find_all(class_='result'):
                    for result_link in res.find_all('a'):
                        results.append(result_link['href'])
                        break
                            
                # process every result
                with open("results.csv", "a", newline='') as resultsFile:
                    csvWriter = csv.writer(resultsFile)
                    for result in results:
                        print(result)
                        page = requests.get(result, headers = headers)
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
                            continue
                        
                        # get business details
                        real_estate = ''
                        reason = ''
                        employees = ''
                        year = ''
                        inventory = ''
                        ffe = ''
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
                        
                        # write n/a if none
                        if real_estate == '':
                            real_estate = "n/a"
                        if reason == '':
                            reason = "n/a"
                        if employees == '':
                            employees = "n/a"
                        if year == '':
                            year = "n/a"
                        if inventory == '':
                            inventory = "n/a"
                        if ffe == '':
                            ffe = "n/a"
                        
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
                        
                        csvWriter.writerow([source, state, region, title, description, real_estate, reason, employees, year, price, revenue, ebitda, cash_flow, inventory, ffe, result, contact])
                    resultsFile.close()
