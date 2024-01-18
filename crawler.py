from requests_html import HTMLSession
import pandas as pd

def get_url_information(link,session,headers):
    response = session.get(link,headers=headers)
    if response.status_code==200:
        text = response.html.xpath('//*[@id="article"]/p/text()')
        text = "".join(text)
        text.replace(u"\u3000",u"").replace("\n","").replace("\r","").replace(" ","")
        return text

def get_sina_news(url,save_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    docs = {'text':[], 'url':[]}
    session = HTMLSession()
    response = session.get(url,headers=headers)
    if response.status_code==200:
        links = response.html.absolute_links
        for link in links:
            if 'doc' in link:
                text = get_url_information(link,session,headers)
                docs['text'].append(text)
                docs['url'].append(link)
    docs = pd.DataFrame(docs)
    docs.to_csv(save_path,index=None)
    return docs

url = 'https://news.sina.com.cn/world/'
save_path = './data/sina_docs.csv'
docs = get_sina_news(url, save_path)