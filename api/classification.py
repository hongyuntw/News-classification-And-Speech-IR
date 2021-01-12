#!/usr/bin/env python
# coding: utf-8

# In[1]:


import torch
import numpy as np
import torch.nn as F
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from transformers import AdamW 
from transformers import BertTokenizer
from transformers import BertForSequenceClassification
from transformers import BertModel
from transformers import BertConfig
import globals

##回傳類別
def get_tag(str_in):
#     pretrain_model_path = '/home/nlp/NewsClassify/bert_pretrain_news/'
#     model_path = '/home/nlp/NewsClassify/'
#     ##新聞分類
    NUM_LABELS = 7
#     tokenizer = BertTokenizer.from_pretrained(pretrain_model_path)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#     model = BertForSequenceClassification.from_pretrained(pretrain_model_path,num_labels = NUM_LABELS)
#     model = model.to(device)
#     model.load_state_dict(torch.load(model_path+'BERT_for_xgboost_0.pkl'), strict=False)

#     model.eval()
#     model1 = BertForSequenceClassification.from_pretrained(pretrain_model_path,num_labels = NUM_LABELS)
#     model1 = model1.to(device)
#     model1.load_state_dict(torch.load(model_path+'BERT_for_xgboost_1.pkl'), strict=False)
#     model1.eval()

#     model2 = BertForSequenceClassification.from_pretrained(pretrain_model_path,num_labels = NUM_LABELS)
#     model2 = model2.to(device)
#     model2.load_state_dict(torch.load(model_path+'BERT_for_xgboost_2.pkl'), strict=False)
#     model2.eval()
#     model_list = [model,model1,model2] ##ensemble用
    class TestDataset(Dataset):
        def __init__(self, input_dict):
            self.input_ids = input_dict['input_ids']
            self.token_type_ids = input_dict['token_type_ids']
            self.attention_mask = input_dict['attention_mask']
        def __getitem__(self, idx):
            input_id = self.input_ids[idx]
            tokentype = self.token_type_ids[idx]
            attentionmask = self.attention_mask[idx]
            return input_id, tokentype, attentionmask
        def __len__(self):
            return len(self.input_ids)
    tag_map = ['政治','生活','國際','體育','娛樂','社會','財經']
    score_list = [0,0,0,0,0,0,0]
    tag_list = []
    threshold = 3
    str_in = [str_in] #list
    test_input_dict = globals.tokenizer.batch_encode_plus(str_in,
                                             add_special_tokens = True,
                                             max_length = 512,
                                             truncation = True,
                                             return_special_tokens_mask = True,
                                             pad_to_max_length = True,
                                             return_tensors = 'pt')
    testset = TestDataset(test_input_dict)
    testloader = DataLoader(testset, batch_size = 1)
    for data in testloader:
        tokens_tensors , segment_tensors,masks_tensors = [t.to(device) for t in data]
        for model in globals.model_list:
            outputs = model(input_ids = tokens_tensors,
                            token_type_ids = segment_tensors,
                            attention_mask = masks_tensors)
            for idx in range(NUM_LABELS):
                score_list[idx] += outputs[0][0][idx]
        for idx in range(len(score_list)):
            if score_list[idx] >= threshold:
                tag_list.append(tag_map[idx])
    return tag_list  

## 回傳報社
def get_news(str_in):
#     pretrain_model_path = '/home/nlp/NewsClassify/bert_pretrain_news/'
#     model_path = '/home/nlp/NewsClassify/'
#     ##報社分類
    LABELS = 3
#     tokenizer = BertTokenizer.from_pretrained(pretrain_model_path)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

#     news_model = BertForSequenceClassification.from_pretrained(pretrain_model_path,num_labels = LABELS)
#     news_model = news_model.to(device)
#     news_model.load_state_dict(torch.load(model_path+'BERT_news_2e5_0.pkl'), strict=False)
#     news_model.eval()
    class TestDataset(Dataset):
        def __init__(self, input_dict):
            self.input_ids = input_dict['input_ids']
            self.token_type_ids = input_dict['token_type_ids']
            self.attention_mask = input_dict['attention_mask']
        def __getitem__(self, idx):
            input_id = self.input_ids[idx]
            tokentype = self.token_type_ids[idx]
            attentionmask = self.attention_mask[idx]
            return input_id, tokentype, attentionmask
        def __len__(self):
            return len(self.input_ids)
    tag_map = ['中國時報','自由時報','聯合報']
    tag_list = []
    str_in = [str_in] #list
    test_input_dict = globals.tokenizer.batch_encode_plus(str_in,
                                             add_special_tokens = True,
                                             max_length = 512,
                                             truncation = True,
                                             return_special_tokens_mask = True,
                                             pad_to_max_length = True,
                                             return_tensors = 'pt')
    testset = TestDataset(test_input_dict)
    testloader = DataLoader(testset, batch_size = 1)
    for data in testloader:
        tokens_tensors , segment_tensors,masks_tensors = [t.to(device) for t in data]
        outputs = globals.news_model(input_ids = tokens_tensors,
                        token_type_ids = segment_tensors,
                        attention_mask = masks_tensors)
        pred_idx = torch.argmax(outputs[0],dim = -1)
        tag_list.append(tag_map[pred_idx])
    return tag_list  


# In[2]:
##這邊是test

# test = '71名書法老師、志工義賣春聯7天20萬助清寒小朋友	基隆市榮民服務處結合采慧珠寶銀樓、青田書學會及青溪新文藝學會，在年前聯合發起春聯義賣活動，一連7天動用書法老師及志工計71人輪番上陣，義賣所得20萬多元全數捐助清寒榮民遺孤小朋友。采慧珠寶銀樓執行長翁瑞芬連續5年無償提供義賣場地及親自煮貢丸湯慰勞老師及志工，榮民服務處長高復隨今天專程前往采慧珠寶銀樓致贈感謝狀，感謝善行義舉，化小愛為大愛，集結社會大眾的力量，扶助弱勢榮民遺孤。這次義賣多虧書法老師及榮欣志工，不畏寒冷天氣，發揮團隊力量，日夜排班現場揮毫，為了吸引過往的民眾，老師們更是發揮創意，如配合今年鼠年，以客製作方式來書寫春聯，各種可愛逗趣的老鼠造型春聯，讓很多民眾愛不釋手，也使義賣現場熱鬧滾滾，義買金額相當不錯，書法老師各種迎春春聯，也都很受歡迎。連續7天的義賣，人氣很旺，金額隨喜，高復隨感謝所有熱心捐款的民眾，讓家庭清寒的榮民遺孤小朋友，可以獲得經濟上幫助，協助他們度過難關。'
# ans = get_tag(test)
# news_ans = get_news(test)
# print(ans)
# print(news_ans)

