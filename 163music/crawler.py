from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
import re
from lxml import etree
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 网易云歌曲爬取
chrome_options = Options()
chrome_options.page_load_strategy = 'eager'
chrome_options.add_argument('blink-settings=imagesEnabled=false')
# chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('verify=False')
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://music.163.com/#/discover/toplist')
time.sleep(2)
driver.switch_to.frame("contentFrame")
# print(driver.page_source)
# elements = WebDriverWait(driver, 5, 0.5).until(
#                         EC.presence_of_element_located((By.XPATH, '//table[@class="m-table m-table-rank"]/tbody/tr')))
elements = driver.find_elements(By.XPATH, '//table[@class="m-table m-table-rank"]/tbody/tr')

urls = []
names = []
ids = []
play_urls = []
texts = []
for i in range(len(elements)):
    print(len(elements),i)
    url = elements[i].find_element(By.XPATH, './/span[@class="txt"]/a').get_attribute('href')
    song_name =elements[i].find_element(By.XPATH, './/span[@class="txt"]/a/b').get_attribute('title')
    id = url.split('id=')[1]
    # print(type(url),url.split('id='))
    play_url = f'http://music.163.com/song/media/outer/url?id={id}.mp3'
    print(f"url: {url} \nsong_name: {song_name} \nid: {id} \nplay_url: {play_url}")
    urls.append(url)
    names.append(song_name)
    ids.append(id)
    play_urls.append(play_url)

    driver.get(url)
    driver.switch_to.frame("contentFrame")

    song_txt = etree.HTML(driver.page_source)
    song_1 = song_txt.xpath('//div[@id="lyric-content"]/text()')
    song_2 = song_txt.xpath('//div[@id="lyric-content"]/div[@id="flag_more"]/text()')
    text = ",".join(song_1)+",".join(song_2)
    texts.append(text)

    print(f"text: {text}")

    driver.get('https://music.163.com/#/discover/toplist')
    time.sleep(2)
    driver.switch_to.frame("contentFrame")
    elements = driver.find_elements(By.XPATH, '//table[@class="m-table m-table-rank"]/tbody/tr')

driver.close()
driver.quit()

song_csv = {"ids":ids,"play_urls":play_urls, "urls":urls,"names":names,"texts":texts}
song_csv = pd.DataFrame(song_csv)
song_csv.to_csv('./songs.csv',index=False)
# //table[@class="m-table m-table-rank"]/td