# PTT
# 資料說明 : https://www.ptt.cc/bbs/Stock/index.html
# 爬取 PTT Stocks 版 最新10頁 文章標題、內文、推文 + 噓文 + 箭頭數量，存成csv


# 安裝套件
pipenv install beautifulsoup4
pipenv install requests
pipenv install pandas

# 執行程式
pipenv run python crawler/ptt.py
pipenv run python crawler/ptt_1.py
pipenv run python crawler/ptt_2.py
pipenv run python crawler/ptt_3.py
pipenv run python crawler/ptt_4.py
pipenv run python crawler/ptt_5.py