import requests
from bs4 import BeautifulSoup
import os
import datetime
import re
import json
import sys
# datetime_save_path = 'HongYunData/udn_date.txt'
# fdate = open(datetime_save_path, "r")
# olddate_string = fdate.readline()
# old_date_time = datetime.datetime.strptime(olddate_string, '%Y-%m-%d %H:%M:%S')
# fdate.close()
# pages =20
pages = sys.argv[1]
save_path = '/home/nlp/Demo/crawler/udn_demo.tsv'
f = open(save_path, 'a')

for i in range(2, int(pages)):
    number = 5436
    html = 'https://udn.com/api/more?page='+str(i)+'&id=&channelId=1&cate_id=0&type=breaknews&totalRecNo='+str(number)
    print(html)
    res = requests.get(html)
    page_json = res.json()
    page_news = page_json['lists']
    urllist = []
    titlelist = []
    timelist = []
    for page_new in page_news:
        url = 'https://udn.com'+ page_new['titleLink']
        urllist.append(url)
        title = page_new['title']
        title = title.replace(' ', '').replace('\t', '').replace('\n', '')
        titlelist.append(title)
        timelist.append(page_new['time']['date'])
    # print(soup)
    # all_news = soup.find_all('dt')
    k = 0
    for url in urllist:
        # url = 'https://udn.com/news/story/120958/4328567?from=udn-ch1_breaknews-1-0-news'
        print(url)
        res = requests.get(url)
        soup = BeautifulSoup(res.text)
        newstype = soup.find_all('a', attrs={'class': 'breadcrumb-items'})
        try:
            print(newstype[1].text)
        except:
            k += 1
            continue
        all_tag_p = soup.find('section',attrs={'class':'article-content__editor'}).find_all('p')
        content = ''
        # Show article
        for tag_p in all_tag_p:
            flag = False
            for c in tag_p.contents:
                if c.name == 'figure':
                    flag = True
                    break
            if (not flag):
                content += tag_p.text
            # print(tag_p.text)
        content = content.replace(' ', '')
        content = content.replace('\n', '')
        content = content.replace('\t', '')
        content = content.replace('\r\n', '')
        content = content.replace('\r', '')
        # print(content)
        print(newstype[1].text + '\t' + titlelist[k] + '\t' + content + '\t' + timelist[k] + '\t' + url, file=f)
        k+=1




