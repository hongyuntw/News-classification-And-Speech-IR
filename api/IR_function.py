#!/usr/bin/env python
# coding: utf-8

# In[4]:


import numpy as np
import pandas as pd
from numpy import errstate,isneginf
from sklearn.preprocessing import normalize
import math
import jieba

def search(text):
    file_path = '/home/nlp/Demo/crawler/'
    column_names = ['type','title','text','time','url']
    udn = pd.read_csv(file_path+'udn_demo.tsv',sep = '\t',names=column_names)
    cn= pd.read_csv(file_path+'cn_demo.tsv',sep = '\t',names=column_names)
    ltn= pd.read_csv(file_path+'ltn_demo.tsv',sep = '\t',names=column_names)
    ## concat
    df = pd.concat([udn, cn,ltn], ignore_index=True)
    df = df.dropna()
    type_dict = {}
    ## 0：政治 1：生活 2：國際 3：體育 4：娛樂 5：社會 6：財經
    type_0 = df[df['type'] == '政治']
    type_1 = df[df['type'] == '生活']
    type_2 = df[df['type'] == '國際']
    type_3 = df[df['type'] == '體育']
    type_4 = df[df['type'] == '娛樂']
    type_5 = df[df['type'] == '社會']
    type_6 = df[df['type'] == '財經']
    type_dict['政治'] = 0
    type_dict['生活'] = 1
    type_dict['國際'] = 2
    type_dict['體育'] = 3
    type_dict['娛樂'] = 4
    type_dict['社會'] = 5
    type_dict['財經'] = 6
    test = pd.concat([type_0,type_1,type_2,type_3,type_4,type_5,type_6],ignore_index=True)
    test = test.drop_duplicates(keep='first',subset = 'text', inplace=False)
    ## get text & type
    doc_type = test['type'].tolist()
    doc_title = test['title'].tolist()
    doc = test['text'].tolist()
    ## tfidf
    doc_len_list = [] ##doc len
    all_doc_data = [] ##all doc split
    all_word = {} ##拿來算word_BG的tf值 過濾用
    all_word_idf = {}
    total_word = 0
    ## all doc tf 第一次 建好完整的字典
    for i in range(len(doc)):
        update = {}
        d_content = jieba.cut(doc[i])
        d_content_split = []
        for word in d_content:   ##all word
            d_content_split.append(word)
            if(word in all_word):
                all_word[word] +=1
            else:
                all_word[word] = 1
                all_word_idf[word] = 0
            if word not in update:
                all_word_idf[word] += 1
                update[word] = 1
        all_doc_data.append(d_content_split)
    ##過濾 tf值 得到新的dict
    ##過濾透過長度> 2 不含數字 tf>5 出現在95%以下的文章中
    new_dict = {} ##總共tf>10或是在query裡的字
    # bg_dict = {}
    id2word = {}
    word2id = {} #建完之後對照用的
    id_count = 0
    for word in all_word:
        if(all_word_idf[word]>=10):
            word2id[word] = id_count
            id2word[id_count] = word
            id_count += 1
            new_dict[word] = 0
    Doc = len(doc) ##總共幾篇文章
    Word = len(new_dict) ##總共幾個字
    Query = 1 ##總共幾個query
    R = 5 ##relevant 數量
    NR = 3 ##最爛幾個Non-relevant
    EPOCH = 3 ##Rocchio跑幾次
    tf_idf_matrix = np.load('./numpy_IR/demo_tfidf.npy')
    idf_dict = new_dict.copy()
    for q in range(Query):
        query_content = text
        query_tf = new_dict.copy() ##紀錄tf分數
        update = {}
        query_content = jieba.cut(query_content)
        for word in query_content:
            if word in new_dict:
                query_tf[word] += 1
                if word not in update:
                    idf_dict[word] += 1
                    update[word] = 0
        tf_idf_matrix[q] = np.array(list(query_tf.values()))
    ans_list = []
    ans_index_list = []
    for i in range(Query): ##總共幾個query
        query_ans_list = []   ##排序輸出結果
        score_list = np.matmul(tf_idf_matrix[Query:],tf_idf_matrix[i]) 
        result_score = sorted(range(Doc),reverse = True,key = lambda k :score_list[k])
        for j in range(Doc):
            query_ans_list.append(doc[result_score[j]])
        for k in range(100):
            ans_list.append(query_ans_list[k])
            ans_index_list.append(result_score[k]) ##relevant index
            
    result_list = [] ##分類過後的輸出
    title_list = []
    used_idx = [] ## already output
    used_type =[0,0,0,0,0,0,0]
    for i in range(20):  ##找到七篇就停止
        count = 0
        for check in range(7):
            if used_type[check] != 0:
                count += 1
        if count == 7: ## all type find
            break
        if used_type[type_dict[doc_type[i]]] == 0:
            result_list.append(ans_list[i])
            title_list.append(doc_title[ans_index_list[i]])
            used_type[type_dict[doc_type[i]]] += 1  ## used
            used_idx.append(i) ## used idx
    for i in range(100): ##再找13篇
        if i not in used_idx:
            result_list.append(ans_list[i])
            title_list.append(doc_title[ans_index_list[i]])
        count = len(result_list)
        if count == 20:
            break
    return title_list,result_list


# In[5]:


word = "機師"
title_list,text_list = search(word)
for i in range(20):
    print(i)
    print(title_list[i])
    print(text_list[i])

