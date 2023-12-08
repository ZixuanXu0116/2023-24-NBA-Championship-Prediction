from bs4 import BeautifulSoup
import os
from playwright.sync_api import sync_playwright, TimeoutError as playwrightTimeout
import time
import os
import zipfile
from tqdm import tqdm
from IPython.display import clear_output



DATA_DIR = 'data'
STANDINGS_DIR = os.path.join(DATA_DIR, 'standings')
SCORES_DIR = os.path.join(DATA_DIR, 'scores')

os.makedirs(STANDINGS_DIR, exist_ok = True)
os.makedirs(SCORES_DIR, exist_ok = True)

SEASONS = list(range(2015, 2025))

def compress(file_names, files_path, output_path):

    '''
    ----------
    Input:
        file_names: list of file names to compress (type: list)
        files_path: path to the files to compress (type: str)
        output_path: path to the output file (type: str)
    ----------
    Output:
        Compressed files in the path with the names in the list, as compressed_games.zip.
    '''
     
    print('Compressing files...')

    '''Select the compression mode ZIP_DEFLATED for compression
        or zipfile.ZIP_STORED to just store the file'''
    compression = zipfile.ZIP_DEFLATED

    '''create the zip file first parameter path/name, second mode'''
    zf = zipfile.ZipFile(os.path.join(output_path, 'compressed_games.zip'), mode="w")
    try:
        for file_name in tqdm(file_names):
            zf.write(os.path.join(files_path, file_name), file_name, compress_type=compression)

    except FileNotFoundError:
        print(f"An error occurred, file {os.path.join(files_path, file_name)} not found") 
    finally:
        zf.close()


def get_html(url, selector, sleep=4, retries=6): 
    """ 
        ----------------------
         Input:
            url: url to get the html from (type: str)
             selector: selector of the html to get (type: str)
              sleep: time to sleep between retries (type: int)
               retries: number of retries (type: int)
                ----------------------------------------
                 Output:
                    html: html page of the url (type: str) """

    html=None
    for i in range(1, retries+1):
        time.sleep(sleep) 

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


def scrape_boxscores(standing_file, season_year): '''getting the paths of the htmls'''
    """
          Input:
            standing_file: path to the standings file (type: str)
            Example: 'data/standings/NBA_2022_games-june.html'
            season_year: year of the season (type: int)
        ----------------------------------------
          Output:
            box_scores: list of box scores (type: list)
    """
    
    '''here we grab a month and go through all the month box scores'''
    with open(standing_file,'r') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    hrefs = [l.get('href') for l in links]
    box_scores = [href for href in hrefs if href and 'boxscore' in href and '.html' in href]
    box_scores = [f'https://www.basketball-reference.com/{href}' for href in box_scores ]
    '''print(f'Now scraping the box scores of the {standing_file.split("/")[-1]}')'''

    for url in tqdm(box_scores): 

        save_path = os.path.join(SCORES_DIR, url.split('/')[-1]) '''saving in directory the name of the BOX SCORE'''
            
        if os.path.exists(save_path):     
            continue

        html = get_html(url=url, selector='#content') '''grabing oly what we want from id selector'''
        if not html:
            print(f'still nothing on the first attempt to get the whole {url} content')
            continue '''if the link is broken or lagging we go on to the next '''
        else:
            '''print(f'attempt to get the {url} content succeed!')'''
            pass
            
        with open (save_path, 'w+', encoding="utf-8") as f:
            f.write(html) '''content to be saved in the file  with specified name'''




standing_file_names = os.listdir(STANDINGS_DIR) 

for name in tqdm(standing_file_names, desc='Scraping Htmls', unit='name'):
    file_path = os.path.join(STANDINGS_DIR, name)
    scrape_boxscores(file_path, season_year=SEASONS)






