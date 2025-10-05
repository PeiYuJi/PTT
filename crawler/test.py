import requests
from bs4 import BeautifulSoup

# 設定目標 PTT 文章 URL
url = 'https://www.ptt.cc/bbs/Stock/M.1759667950.A.73C.html'

# 設定 headers，模擬瀏覽器行為
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 發送 GET 請求
response = requests.get(url, headers=headers)

# 檢查回應狀態碼
if response.status_code == 200:
    # 解析 HTML 內容
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)   
    # 找出所有推文與噓文
    push_comments = soup.find_all('span', class_='push-tag')
    print(push_comments)
    # 統計推文與噓文數量
    push_count = sum(1 for tag in push_comments if tag.text == '推 ')
    boo_count = sum(1 for tag in push_comments if tag.text == '噓 ')
    
    # 輸出結果
    print(f'推文數量: {push_count}')
    print(f'噓文數量: {boo_count}')
else:
    print(f'無法取得網頁內容，狀態碼：{response.status_code}')
