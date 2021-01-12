# -*- coding: utf-8 -*
from flask import Flask, jsonify, request
import utils
import pandas as pd
import gdown
import sys
import argparse
import json
import ast
import asr
import jieba
from numpy import errstate,isneginf
from sklearn.preprocessing import normalize
import math
import numpy as np
from crawler import PttCrawler
import globals
from classification import *
from IR import *
from flask_socketio import SocketIO
from flask_cors import CORS
import wave

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')
app.config['JSON_SORT_KEYS'] = False
CORS(app)


@app.route('/')
def hello_world():
    return 'Flask Dockerized'


@app.route('/asr')
def asr_api():
    asr.asr(fbank_path = asr.wav2fbank())
    return 'asr'

@app.route('/crawler_ptt' , methods=["POST"])
def crawler_ptt_api():
    ptt_url = request.form.get('ptt')
    mode = 'all'
    crawler = PttCrawler()
    result = crawler.parse_article(ptt_url, mode)
    print(result)
    content = result['Content']
    tags = get_tag(content)
    news = get_news(content)
    result['tags'] = tags
    result['news'] = news
    return result

@app.route('/upload_wav' , methods=["POST"])
def upload_wav_api():
    # print(request.files)
    nchannels = 1
    sampwidth = 2
    framerate = 16000 
    nframes = 1 
    name = '/home/nlp/Demo/api/wav/output.wav' 
    audio = wave.open(name, 'wb') 
    audio.setnchannels(nchannels) 
    audio.setsampwidth(sampwidth) 
    audio.setframerate(framerate) 
    audio.setnframes(nframes) 
    
    audio_input = request.files['upfile'] 
    blob = audio_input.read()
    audio.writeframes(blob) 
    # setting language for asr model
    is_chinese = True
    language = 'Chinese' if is_chinese else 'Taiwanese'
    text = asr.recog(name)
    # fbank_path = asr.wav2fbank(name,language)
    # texts = asr.asr(fbank_path = fbank_path,language = language)
    # text = texts[0][:10]
    title_list,content_list = search(text) ##先預設10個字

    return jsonify(
        {
            'text' : text ,
            'title_list' : title_list ,
            'content_list' : content_list
        }
    )
        

@app.route('/get_tag' , methods=["POST"])
def get_tag_api():
    text_in = request.form.get('text')
    tags = get_tag(text_in)
    news = get_news(text_in)
    return jsonify(
        {
            'tags' : tags ,
            'news' : news
        }
    )
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    globals.initialize()

    app.run(debug=False, host='0.0.0.0', port=8787)
