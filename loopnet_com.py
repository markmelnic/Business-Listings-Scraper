
import csv
import requests
import threading
from bs4 import BeautifulSoup

# request headers
HEADERS = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}

# encode and format
def format_properly(string):
    string = str(string.encode("utf8"))
    string = str(string.replace("\\n", "").replace("b'", "").replace("'", ""))
    return string

class loopnet_com():
    def __init__(self, link, mode):
        self.scrape_page(link, mode)

    # scrape listings page
    def scrape_page(self, link, mode):
        permalink = link
        lindex = 0
        while True:
            lindex += 1
            # get next link
            if lindex != 1:
                link = permalink + "/" + str(lindex)

            # make request and generate code soup
            page = requests.get(link, headers = HEADERS, timeout=30)
            soup = BeautifulSoup(page.content, 'html.parser')

            # break if no results found
            if len(soup.find_all('app-listing-showcase')) == 0:
                break

            # get all result links
            results = []
            try:
                for res in soup.find_all('app-listing-diamond'):
                    result_link = res.find('a')
                    results.append("https://www.loopnet.com" + result_link['href'])
            except:
                None

            for res in soup.find_all('app-listing-showcase'):
                result_link = res.find('a')
                results.append("https://www.loopnet.com" + result_link['href'])

            # read current data
            with open("results.csv", "r", newline='') as resultsFile:
                reader = csv.reader(resultsFile)
                alldata = list(reader)
                data = []
                for d in alldata:
                    data.append(d[15])

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

    # scrape listing
    def scrape_result(self, result, csvWriter, changesWriter, mode, data):
        print(result)
        # make request and generate code soup
        page = requests.get(result, headers = HEADERS, timeout=30)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # source
        source = "Loopnet.com"

        #listing
        full_listing = soup.find(class_ = "imageContact")

        # title
        title = full_listing.find("h1")
        title = format_properly(title.find('span').text)

        # description
        try:
            description = format_properly(soup.find(class_ = "col-parent col-12 mobile-col-6 tablet-col-6 summary text-light descriptionAd").text)
        except:
            return # ad or franchise

        # get top results
        year = "n/a"
        price = "n/a"
        revenue = "n/a"
        ebitda = "n/a"
        cash_flow = "n/a"
        inventory = "n/a"
        ffe = "n/a"
        for body in soup.find_all('tbody'):
            for tr in body.find_all('tr'):
                try:
                    tds = tr.find_all('td')
                    if "asking price" in tds[0].find('span').text.lower():
                        price = format_properly(tds[1].find('span').text)
                    elif "revenue" in tds[0].find('span').text.lower():
                        revenue = format_properly(tds[1].find('span').text)
                    elif "ff&e" in tds[0].find('span').text.lower():
                        ffe = format_properly(tds[1].find('span').text)
                    elif "year" in tds[0].find('span').text.lower():
                        year = format_properly(tds[1].find('span').text)
                    elif "cash flow" in tds[0].find('span').text.lower():
                        cash_flow = format_properly(tds[1].find('span').text)
                    elif "inventory" in tds[0].find('span').text.lower():
                        inventory = format_properly(tds[1].find('span').text)
                    elif "ebitda" in tds[0].find('span').text.lower():
                        ebitda = format_properly(tds[1].find('span').text)
                except:
                    pass

        # get location
        state = "n/a"
        region = "n/a"
        location = soup.find(class_ = "col-12 col-parent locationHeight")
        loc_divs = location.find_all('div')
        if "location" in loc_divs[0].text.lower():
            location = format_properly(loc_divs[1].text).split(',')
            if len(location) == 1:
                state = location[0]
            else:
                region = location[0]
                state = location[1]

        # get business details
        real_estate = "n/a"
        reason = "n/a"
        employees = "n/a"
        for detail in soup.find_all(class_ = "col-12 col-parent detailInformationHeight"):
            divs = detail.find_all('div')
            if "real estate" in divs[0].text.lower():
                real_estate = format_properly(divs[1].text)
            elif "employees" in divs[0].text.lower():
                employees = format_properly(divs[1].text)
            elif "reason for selling" in divs[0].text.lower():
                reason = format_properly(divs[1].text)

        # contact
        contact = ''
        try:
            for div in soup.find(class_ = 'broker-profile-name'):
                contact = contact + format_properly(div.text)
        except:
            contact = "n/a"

        # phone
        phone = soup.find(class_ = 'profile-phone')
        phone = format_properly(phone.text)

        # write data to csv file
        # if mode is 'f' then changes will not be taken into consideration
        if mode.lower() == 'f':
            csvWriter.writerow([source, state, region, title, description, real_estate, reason, employees, year, price, revenue, ebitda, cash_flow, inventory, ffe, result, contact, phone])
        # if mode is 't' then only changes will be written to the output file
        else:
            listing_data = [source, state, region, title, description, real_estate, reason, employees, year, price, revenue, ebitda, cash_flow, inventory, ffe, result, contact, phone]
            if not result in data:
                changesWriter.writerow([source, state, region, title, description, real_estate, reason, employees, year, price, revenue, ebitda, cash_flow, inventory, ffe, result, contact, phone])
