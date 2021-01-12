import requests
from bs4 import BeautifulSoup
import os
import datetime
import re
import json
import sys
all_type = ['體育', '政治', '社會', '生活', '國際', '財經', '娛樂']
dateflag = False
def get_ltn_news(i):
    global dateflag
    #  today
    today = datetime.date.today()
    today = str(today)

    # get url
    ltn_url = 'https://news.ltn.com.tw/ajax/breakingnews/all/'
    ltn_url = ltn_url + str(i)
    print('urlpage:',ltn_url)
    news_list = []
    type_list = []
    title_list = []
    datelist = []
    response = requests.get(ltn_url)
    if response.status_code == 200:
        page_json = response.json()
        data = page_json['data']
        flag = True
        for d in data:
            news_list.append(data[d]['url'])
            if (data[d]['type_cn'] == ""):
                type_list.append('None')
            else:
                type_list.append(data[d]['type_cn'])
            title_list.append(data[d]['title'])
            datelist.append(today + ' '+ data[d]['time'])

    save_path = '/home/nlp/Demo/crawler/ltn_demo.tsv'
    with open(save_path, "a") as text_file:
        for j in range(len(news_list)):
            try:
                # crawler
                url = news_list[j]
                # url = 'http://sports.ltn.com.tw/news/breakingnews/3051506'
                print(url)
                res = requests.get(url)
                soup = BeautifulSoup(res.text)
                # print(soup)
                # 很多不同格式
                # type_list[j] = '體育'
                if (type_list[j] == '體育'):
                    context = soup.find('div', attrs={"itemprop": "articleBody"})
                elif (type_list[j] == '政治' or type_list[j] == '社會' or type_list[j] == '生活' or type_list[j] == '國際'):
                    context = soup.find('div', attrs={"class": "text boxTitle boxText","data-desc":"內容頁"})
                elif (type_list[j] == '財經'):
                    context = soup.find('div', attrs={"itemprop": "articleBody", "class": "text"})
                elif (type_list[j] == '娛樂'):
                    context = soup.find('div', attrs={"itemprop": "articleBody","class":"news_content"})                
                else:
                    continue
                
                # print(context.text)        
                all_tag_p =context.find_all('p', {"class":None})
                list_len = len(all_tag_p)
                mystr = ''
                for tag_p in all_tag_p:
                    flag = False
                    for c in tag_p.contents:
                        if c.name == 'figure':
                            flag = True
                            break
                    if (not flag):
                        mystr += tag_p.text
                # print(mystr)
                mystr = mystr.replace('\t', '')
                mystr = mystr.replace('\n', '')
                mystr = mystr.replace('\r\n', '')
                mystr = mystr.replace('\r', '')
                mystr = mystr.replace(' ', '')
                mystr = mystr.replace('（','(').replace('）',')')
                mystr = mystr.replace('〔', '(').replace('〕', ')')
                mystr = mystr.replace('[', '(').replace('］', ')')
                count = 0
                loopflag = False
                while (1):
                    count += 1
                    if (count >= 20):
                        loopflag = True
                        break
                    start = mystr.find('(')
                    end = mystr.find(')')
                    if(start == -1 or end ==-1):
                        break
                    elif (start != -1 and end != -1):
                        mystr = mystr[:start] + mystr[end+1:]
                if (loopflag):
                    continue
                print(type_list[j] + '\t' + title_list[j].replace('\n', '').replace('\t', '').replace(' ', '') + '\t' + mystr.replace('\n', '').replace('\t', '').replace(' ', '') + '\t' + datelist[j] + '\t' + url, file=text_file)
            except:
                pass
    if (dateflag):
        return

            
if __name__ == '__main__':
    # read last time 
    # datetime_save_path = 'HongYunData/ltn_date.txt'
    # f = open(datetime_save_path, "r")
    # olddate_string = f.readline()
    # old_date_time = datetime.datetime.strptime(olddate_string, '%Y-%m-%d %H:%M:%S')
    # f.close()
    pages = sys.argv[1]
    # pages = 3
    for k in range(2, int(pages)):
        # if (dateflag):
        #     print('剩下得新聞之前讀過啦！！')
        #     break
        get_ltn_news(k)


    
    
