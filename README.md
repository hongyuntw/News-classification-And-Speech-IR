# speech_and_news_classify


## Text classification

給定文本/ptt，用train好的BERT model predict內容類別(娛樂,社會,生活,國際,財經,娛樂,體育)，即可能屬於哪間報社(自由時報,中國時報，聯合報)


## ASR + IR

提供中文語音辨識模型，輸入想要查詢新聞的關鍵字，透過VSM找出資料庫中最相關的文本，及語音辨識結果

語音辨識模型可參考[ESPnet](https://github.com/hongyuntw/ESPnet)，此專案為更改ESPnet model，採用conformer + self - mixed attention decode
