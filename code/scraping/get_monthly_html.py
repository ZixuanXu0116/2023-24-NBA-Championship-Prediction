from bs4 import BeautifulSoup
import os
from playwright.sync_api import sync_playwright, TimeoutError as playwrightTimeout
import time
from tqdm import tqdm

SEASONS = list(range(2015, 2025))

DATA_DIR = 'data'
STANDINGS_DIR = os.path.join(DATA_DIR, 'standings') 
SCORES_DIR = os.path.join(DATA_DIR, 'scores')
os.makedirs(STANDINGS_DIR, exist_ok = True)
os.makedirs(SCORES_DIR, exist_ok = True)


def get_html(url, selector, sleep=4, retries=7): # async allow the code after it to imediatelly execute. 
    """ Info:
     This function will get the html content of a page and return it as a html file
      --------------------------------------------------------------------------------
       Input:
        url: url of the page to be scraped  
        selector: selector of the html element to be scraped
        sleep: time to wait between each try in seconds to avoid over the request limit
        retries: number of tries to get the html content of each page
        --------------------------------------------------------------------------------
        Output:
        html: html content of the page
        """
    html = None
    for i in range(1, retries+1):
        time.sleep(sleep * i) # each try is longer by a sleep multiplication factor

        try:
            with sync_playwright() as p: 
                browser = p.chromium.launch() # await will actually wait for the async load of the website complete to lauch the browser
                page = browser.new_page() # page will be a new tab
                page.goto(url)
                html = page.inner_html(selector) # we gonna get only part of the html page

        except playwrightTimeout:
            print(f'TimeoutError on the url {url}')
            continue 

        else: 
            break

    if html != None:
        return html
    
    else:
        print('Fail')

def scrapy_season(season):
    """ Info:
        This function will scrape the standings of a season and save them in a html file
        --------------------------------------------------------------------------------
        Input:
            season: season to be scraped
            --------------------------------------------------------------------------------
            Output:
            None
            """
    url  = f"https://www.basketball-reference.com/leagues/NBA_{season}_games.html"
    
    
    html = get_html(url=url, selector='#content .filter')
    if html == None:
        print('still nothing on the first attempt to get the whole page content')
    else:
        # print('attempt to get the whole page content succeed!')
        pass

        

    soup = BeautifulSoup(html, 'html.parser') #type: ignore
    links = soup.find_all('a')
    href = [l['href'] for l in links] # l is a hyperlink for a month
    stadings_pages = [f"https://www.basketball-reference.com{l}" for l in href]

    for url in stadings_pages: # navigate for each month page to save the file name first
        save_path = os.path.join(STANDINGS_DIR, url.split('/')[-1]) # saving in directory the name of the schedule month
        #print the save path
        print("save_path: ", save_path)

        #checking if the file already exists except for the current month that needs to be downloaded everytime
        if os.path.exists(save_path) and season != SEASONS[-1]: # if the file already exists and it is not the current season
            continue

        #grabbing table of month
        html = get_html(url=url, selector='#all_schedule')
        if html == None:
            print(f'still nothing on the first attempt to get the whole {url} content')
        else:
            # print(f'attempt to get the {url} content succeed!')
            pass
        
        with open (save_path, 'w+') as f:
            f.write(html) 
    
#scrapping every season
for season in tqdm(SEASONS, desc='Scraping Seasons', unit='season'):
    scrapy_season(season)
    print(f'scraped season {season} with success')
