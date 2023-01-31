import configparser
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup as Soup
import time


###### Config ######
config = configparser.ConfigParser()
###### Config ######

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class customInstagram:
    async def downloadPost(url):
        options = Options()

        options.add_argument('lang=en') 
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        options.add_argument('--headless') 
        options.add_argument('--no-sandbox')
        options.add_argument('--single-process')
        options.add_argument('--disable-dev-shm-usage')

        options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/5$')

        driver = webdriver.Chrome(options=options)

        driver.get(url)

        time.sleep(5)

        media_url = []
        video_url = []
        try: 
            button = driver.find_element(By.CLASS_NAME, '_9zm2')
            while(button != None):
                try:
                    button.click()
                except:
                    button = None
                time.sleep(1)
                soup = Soup(driver.page_source,"lxml")
                articleTag = soup.find_all("article")
                img_frame = articleTag[0].find_all("img", attrs={'style':'object-fit: cover;'})
                for i in img_frame:
                    src = i.get('src')
                    if src not in media_url:
                        media_url.append(src)
                video_frame = articleTag[0].find_all("video")
                for v in video_frame:
                    src = v.get('src')
                    if src not in video_url:
                        video_url.append(src)
        except NoSuchElementException:
            soup = Soup(driver.page_source,"lxml")
            articleTag = soup.find_all("article")
            img_frame = articleTag[0].find_all("img", attrs={'style':'object-fit: cover;'})
            for i in img_frame:
                src = i.get('src')
                if src not in media_url:
                    media_url.append(src)
            video_frame = articleTag[0].find_all("video")
            for v in video_frame:
                src = v.get('src')
                if src not in video_url:
                    video_url.append(src)
        driver.close()
        data = {'image':media_url, 'video':video_url}
        #logger.info(data)
        return data