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
# pages = sys.argv[1]
save_path = '/home/nlp/Demo/crawler/cn_demo.tsv'
f = open(save_path, 'a')

for i in range(1,11):
    html = 'https://www.chinatimes.com/realtimenews/?page=' + str(i) + '&chdtv'
    print(html)
    res = requests.get(html).text
    soup = BeautifulSoup(res, 'html.parser')
    # print(soup)
    all_news = soup.find_all('h3', attrs={'class': 'title'})
    all_type = soup.find_all('div', attrs={'class': 'category'})
    all_time = soup.find_all('time')
    # print(len(all_time))
    # print(len(all_news))
    # print(len(all_type))
    typelist = []
    titlelist = []
    newslist = []
    timelist = []
    for typ in all_type:
        typelist.append(typ.get_text())
    for time in all_time:
        # print(str(time['datetime']))
        timelist.append(str(time['datetime']))
        
    
    for news in all_news:
        news_url = 'https://www.chinatimes.com' + str(news.find('a').get('href'))
        print(news_url)
        titlelist.append(news.find('a').get_text().replace(' ', '').replace('\n', '').replace('\t', ''))
        newslist.append(news_url)
    num = 0
    for news_url in newslist:
        html = requests.get(news_url).text
        soup = BeautifulSoup(html, 'html.parser')
        all_tag_p = soup.find('div',attrs={'class':'article-body'}).find_all('p')
        content = ''
        # Show article
        # print(len(all_tag_p))
        size = len(all_tag_p)
        c = 0
        for tag_p in all_tag_p:
            for child in tag_p.findAll():
                child.decompose()
            if (c != size - 1):
                content += tag_p.text
            c += 1
    
        content = content.replace(' ', '').replace('\n', '').replace('\t', '')
        # print(content)
        print(typelist[num] + '\t' + titlelist[num] + '\t' + content + '\t' + timelist[num] + '\t'+ news_url, file=f)
        num += 1
    


