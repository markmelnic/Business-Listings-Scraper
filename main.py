
import csv
from loopnet_com import loopnet_com
from businessesforsale_com import businessesforsale_com

if __name__=='__main__':
    # read all links from 'links.txt'
    with open("links.txt", "r") as linksFile:
        links = linksFile.read().splitlines()
        mode = links[0]
        links.pop(0)

    # check if file is empty or non existent
    try:
        with open("results.csv", "r", newline='') as resultsFile:
            alldata = resultsFile.read()
    except:
        with open("results.csv", "a", newline='') as resultsFile:
            alldata = ''

    # write first line if file is empty
    if alldata == '':
        with open("results.csv", "a", newline='') as resultsFile:
            csvWriter = csv.writer(resultsFile)
            csvWriter.writerow(["Source", "State", "Region", "Title", "Description", "Real estate", "Reason for selling", "Employees", "Year", "Price", "Revenue", "EBITDA", "Cash flow", "Inventory", "FFE", "Result", "Contact", "Phone"])

    # find link corresponding function
    for link in links:
        if "businessesforsale" in link:
            businessesforsale_com(link, mode)
        if "loopnet" in link:
            loopnet_com(link, mode)
