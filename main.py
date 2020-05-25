
import csv
from businessesforsale_com import businessesforsale_com

if __name__=='__main__':
    # read all links
    with open("links.txt", "r") as linksFile:
        links = linksFile.read().splitlines()
        linksFile.close()

    # check if file is empty and write first line
    try:
        with open("results.csv", "r", newline='') as resultsFile:
            data = resultsFile.read()
            resultsFile.close()
    except:
        with open("results.csv", "a", newline='') as resultsFile:
            data = ''
            resultsFile.close()
        
    if data == '':
        with open("results.csv", "a", newline='') as resultsFile:
            csvWriter = csv.writer(resultsFile)
            csvWriter.writerow(["Source", "State", "Region", "Title", "Description", "Real estate", "Reason for selling", "Employees", "Year", "Price", "Revenue", "EBITDA", "Cash flow", "Inventory", "FFE", "Result", "Contact"])
            resultsFile.close()
                    
    # find link corresponding function
    for link in links:
        if "businessesforsale" in link:
            businessesforsale_com(link)