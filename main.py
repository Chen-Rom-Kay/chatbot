from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
import re
from lxml import etree
import pandas as pd

# 网易云歌曲歌词爬取
chrome_options = Options()
chrome_options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://music.163.com/#/discover/toplist')
time.sleep(2)
driver.switch_to.frame("contentFrame")
# print(driver.page_source)
elements = driver.find_elements(By.XPATH, '//table[@class="m-table m-table-rank"]/tbody/tr')

urls = []
names = []
texts = []
for i in range(len(elements)):
    url = elements[i].find_element(By.XPATH, './/span[@class="txt"]/a').get_attribute('href')
    song_name =elements[i].find_element(By.XPATH, './/span[@class="txt"]/a/b').get_attribute('title')
    print(url, song_name)

    urls.append(url)
    names.append(song_name)

    driver.get(url)
    driver.switch_to.frame("contentFrame")

    song_txt = etree.HTML(driver.page_source)
    song_1 = song_txt.xpath('//div[@id="lyric-content"]/text()')
    song_2 = song_txt.xpath('//div[@id="lyric-content"]/div[@id="flag_more"]/text()')
    text = ",".join(song_1)+",".join(song_2)
    texts.append(text)

    print(text)

    driver.back()
    time.sleep(2)
    driver.switch_to.frame("contentFrame")
    elements = driver.find_elements(By.XPATH, '//table[@class="m-table m-table-rank"]/tbody/tr')

driver.close()
driver.quit()

song_csv = {"urls":urls,"names":names,"texts":texts}
song_csv = pd.DataFrame(song_csv)
song_csv.to_csv('./songs.csv')
# //table[@class="m-table m-table-rank"]/td