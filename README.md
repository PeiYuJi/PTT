# 爬取網站 : https://www.ptt.cc/bbs/Stock/index.html
# 資料說明 : 爬取 PTT Stocks 版 最新10頁 文章標題、作者、時間、內文、推文數量 + 噓文數量 + 箭頭數量，存成csv


# 安裝套件
pipenv install beautifulsoup4
pipenv install requests
pipenv install pandas

# 執行程式
pipenv run python crawler/PTT.py
