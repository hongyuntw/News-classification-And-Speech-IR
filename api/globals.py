# -*- coding: utf-8 -*
from ckiptagger import NER, POS, WS , data_utils , construct_dictionary
import pandas as pd
import gensim
import pickle
import csv
import jieba
from transformers import AdamW 
from transformers import BertTokenizer
from transformers import BertForSequenceClassification
from transformers import BertModel
from transformers import BertConfig
import torch
import numpy as np
import torch.nn as F



def initialize():
    # read csv/news......
    # loading model
    # example global model1 
    global tokenizer
    global model_list
    global news_model
    global tf_idf_matrix
    global new_dict

    tf_idf_matrix = np.load('./numpy_IR/demo_tfidf.npy')
    
    pretrain_model_path = '/home/nlp/NewsClassify/bert_pretrain_news/'
    model_path = '/home/nlp/NewsClassify/'
    ##新聞分類
    NUM_LABELS = 7
    tokenizer = BertTokenizer.from_pretrained(pretrain_model_path)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = BertForSequenceClassification.from_pretrained(pretrain_model_path,num_labels = NUM_LABELS)
    model = model.to(device)
    model.load_state_dict(torch.load(model_path+'BERT_for_xgboost_0.pkl'), strict=False)

    model.eval()
    model1 = BertForSequenceClassification.from_pretrained(pretrain_model_path,num_labels = NUM_LABELS)
    model1 = model1.to(device)
    model1.load_state_dict(torch.load(model_path+'BERT_for_xgboost_1.pkl'), strict=False)
    model1.eval()

    model2 = BertForSequenceClassification.from_pretrained(pretrain_model_path,num_labels = NUM_LABELS)
    model2 = model2.to(device)
    model2.load_state_dict(torch.load(model_path+'BERT_for_xgboost_2.pkl'), strict=False)
    model2.eval()
    model_list = [model,model1,model2] ##ensemble用

    # 報社model
    pretrain_model_path = '/home/nlp/NewsClassify/bert_pretrain_news/'
    model_path = '/home/nlp/NewsClassify/'
    ##報社分類
    LABELS = 3
    tokenizer = BertTokenizer.from_pretrained(pretrain_model_path)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    news_model = BertForSequenceClassification.from_pretrained(pretrain_model_path,num_labels = LABELS)
    news_model = news_model.to(device)
    news_model.load_state_dict(torch.load(model_path+'BERT_news_2e5_0.pkl'), strict=False)
    news_model.eval()
    

    
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
    # pass 

