import argparse
import requests
from lxml import html
import logging
import logging.handlers
from bs4 import BeautifulSoup

"""
python src/fp_dl.py -u https://www.fantasypros.com/nfl/rankings/half-point-ppr-flex.php?week=1\\&export=xls 
-d dat/2017/week-1-half-point-ppr-flex-raw.txt 
-c dat/2017/week-1-half-point-ppr-flex-raw.csv -n 9
infile = 'dat/2017/week-1-half-point-ppr-flex-raw.xls'
outfile = 'dat/2017/week-1-half-point-ppr-flex-raw.csv'
'flex' in outfile
ncol = 9
"""

def convertXlsToCsv(infile, outfile):
    if 'FLX' in outfile:
        ncol = 9
    else:
        ncol = 8
    
    # Open xls file, parse headings and format each row, write to csv
    file = open(infile, 'r') 
    text = file.read() 
    soup = BeautifulSoup(text,features="html.parser")
    tables = soup.findAll("table")
    table = tables[0]
    headings = [th.get_text().strip() for th in table.find("tr").find_all("th")]    
    fout = open(outfile, 'w')
    fout.write(','.join(headings[:-1]) + '\n')
    rows = []
    for row in table.find_all("tr")[1:]:
        try:
            nextrow = [td.get_text("| ") for td in row.find_all("td")]
            if (int(len(nextrow)) >= ncol):
                line = ','.join(nextrow[:int(ncol)])
                line = line.replace(' \n', '')
                fout.write(line + '\n')
                rows.append(nextrow)
        except:
            pass
    fout.close()
    return

def perform_session_download(args, url, xls_file_name):
    """
    creates a session that allows the user to log in to FantasyPros and use the tokens
    :param args: list of parameters can be used to get data directories
    :param url: string of the export xls url
    :param xls_file_name: string of the full file path and name of file to be saved
    """
    logger = logging.getLogger()
    # get payload values from command line parameters
    username, password, token = args['username'], args['password'], args['token']
    payload = {"username": username,
               "password": password,
               "csrfmiddlewaretoken": token}
    # start session
    print("Starting download session...")
    logger.debug("Starting download session...")
    session_requests = requests.session()
    login_url = "https://secure.fantasypros.com/accounts/login/?"
    result = session_requests.get(login_url)
    # refresh token on new request
    tree = html.fromstring(result.text)
    logger.debug("Updating token...")
    authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]
    payload["csrfmiddlewaretoken"] = authenticity_token
    session_requests.post(login_url,
                          data=payload,
                          headers=dict(referer=login_url))
    # prepare to write data to file
    #logger.debug("Opening xls file to write data...")
    with open(xls_file_name, 'wb') as handle:
        response = session_requests.get(url)
        if not response.ok:
            logger.info("Writing to xls failed...")
        for block in response.iter_content(1024):
            handle.write(block)
        logger.info("Writing to xls succeeded...")


if __name__ == "__main__":    # get all of the commandline arguments
    """
    python src/fp_dl.py -u https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php?export=xls -d dat/2016/week-0-all-raw.xls
    """
    parser = argparse.ArgumentParser("FantasyPros Ranking Scraper")
    parser.add_argument('-u', dest='url', help="FantasyPros url", required=True)
    parser.add_argument('-d', dest='xls_file_name', help="Destination", required=True)
    parser.add_argument('-c', dest='csv_file_name', help="CSV Destination", required=True)
    
    userargs = {'username':'borischen003', 'password':'borischen1', 'token':'1'}

    args = parser.parse_args()
    url = args.url
    xls_file_name = args.xls_file_name
    csv_file_name = args.csv_file_name
    
    # Testing file format with kickers
    # url = 'https://www.fantasypros.com/nfl/rankings/k.php?filters=64:113:120:125:127:317:406:534\\&week=2\\&export=xls'
    # xls_file_name = 'dat/2020/week-2-K-STD-raw.xls'
    # csv_file_name = 'dat/2020/week-2-K-STD-raw.csv'
    # ncol = 9
    
    # Testing file format with flex
    # url = 'https://www.fantasypros.com/nfl/rankings/flx.php?filters=64:113:120:125:127:317:406:534\\&week=2\\&export=xls'
    # xls_file_name = 'dat/2020/week-2-FLX-PPR-raw.xls'
    # csv_file_name = 'dat/2020/week-2-FLX-PPR-raw.csv'
    # ncol = 10
    
    perform_session_download(userargs, url, xls_file_name)
    convertXlsToCsv(xls_file_name, csv_file_name)

