
from businessesforsale_com import businessesforsale_com

if __name__=='__main__':
    # read all links
    with open("links.txt", "r") as linksFile:
        links = linksFile.read().splitlines()
        linksFile.close()

    # find link corresponding function
    for link in links:
        if "businessesforsale" in link:
            businessesforsale_com(link)