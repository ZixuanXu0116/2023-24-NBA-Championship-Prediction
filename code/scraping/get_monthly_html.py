from bs4 import BeautifulSoup
import os
from playwright.sync_api import sync_playwright, TimeoutError as playwrightTimeout
import time
from tqdm import tqdm

SEASONS = list(range(2015, 2025))

new_directory = os.path.join(os.getcwd(), "code", "scraping")
os.chdir(new_directory)
DATA_DIR = 'data'
STANDINGS_DIR = os.path.join(DATA_DIR, 'standings') 
SCORES_DIR = os.path.join(DATA_DIR, 'scores')
os.makedirs(STANDINGS_DIR, exist_ok = True)
os.makedirs(SCORES_DIR, exist_ok = True)


def get_html(url, selector, sleep=4, retries=7): 
    ''' async allow the code after it to imediatelly execute. '''
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
        '''each try is longer by a sleep multiplication factor'''
        time.sleep(sleep * i)

        try:
            with sync_playwright() as p: 
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url)
                html = page.inner_html(selector)

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
        pass

        

    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    href = [l['href'] for l in links]
    stadings_pages = [f"https://www.basketball-reference.com{l}" for l in href]

    for url in stadings_pages:
        save_path = os.path.join(STANDINGS_DIR, url.split('/')[-1])
        '''print the save path'''
        print("save_path: ", save_path)

        '''checking if the file already exists except for the current month that needs to be downloaded everytime'''
        if os.path.exists(save_path) and season != SEASONS[-1]:
            continue

        '''grabbing table of month'''
        html = get_html(url=url, selector='#all_schedule')
        if html == None:
            print(f'still nothing on the first attempt to get the whole {url} content')
        else:
            '''print(f'attempt to get the {url} content succeed!')'''
            pass
        
        with open (save_path, 'w+') as f:
            f.write(html) 
    
'''scraping every season'''
for season in tqdm(SEASONS, desc='Scraping Seasons', unit='season'):
    scrapy_season(season)
    print(f'scraped season {season} with success')
