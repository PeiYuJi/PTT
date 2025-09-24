import requests
from bs4 import BeautifulSoup
import time
import json

BASE_URL = "https://pttweb.tw"
BOARD = "stock"
PAGE_LIMIT = 10

def get_page_url(page_num):
    # 假設第 1 頁是 BASE_URL/stock/
    # 接下來的頁面可能是 /stock/page/2、或 indexX、要依照實際觀察
    # 這裡示範猜測 "/stock/page/{page}"
    if page_num == 1:
        return f"{BASE_URL}/{BOARD}/"
    else:
        return f"{BASE_URL}/{BOARD}/page/{page_num}/"

def parse_article_list(page_url):
    resp = requests.get(page_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    articles = []
    # 以下 selector 依照該頁 HTML 結構來定
    # 假設文章在 <div class="title"> <a href="...">標題</a> ... </div>
    for title_div in soup.select("div.title"):
        a = title_div.find("a")
        if a:
            article = {
                "title": a.get_text().strip(),
                "url": BASE_URL + a["href"]
            }
            articles.append(article)
    return articles

def parse_article(article_url):
    resp = requests.get(article_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # 取標題（應該和列表頁標題相符）
    title = soup.find("h1").get_text().strip() if soup.find("h1") else ""

    # 取內文（排除推文、作者時間那部分）
    content_div = soup.find("div", class_="content")  # 注意要依實際 class name 修改
    content = ""
    if content_div:
        # 去掉推文／meta 資訊
        for meta in content_div.find_all(["div", "span"], class_="meta"):
            meta.decompose()
        content = content_div.get_text().strip()

    # 推噓數量、留言數
    # 看 HTML 如何標示推噓；假設有標籤 class="push", class="boo", etc.
    push = len(soup.select("div.push"))  # 推文數
    boo = len(soup.select("div.boo"))    # 噓文數
    arrow = len(soup.select("div.arrow"))  # 箭頭／中性

    # 留言總數可能是推 + 噓 + arrow，或者另有留言區
    total_messages = push + boo + arrow

    return {
        "title": title,
        "content": content,
        "push": push,
        "boo": boo,
        "arrow": arrow,
        "messages_count": total_messages
    }

def main():
    results = []
    for page in range(1, PAGE_LIMIT+1):
        page_url = get_page_url(page)
        print(f"Processing page {page}: {page_url}")
        try:
            articles = parse_article_list(page_url)
        except Exception as e:
            print(f"Failed to fetch list page {page}: {e}")
            continue

        for art in articles:
            print(f"  -> {art['title']}")
            try:
                art_detail = parse_article(art["url"])
            except Exception as e:
                print(f"     Failed to fetch article {art['url']}: {e}")
                continue

            record = {
                "url": art["url"],
                "title": art_detail["title"],
                "content": art_detail["content"],
                "push": art_detail["push"],
                "boo": art_detail["boo"],
                "arrow": art_detail["arrow"],
                "messages_count": art_detail["messages_count"]
            }
            results.append(record)
            time.sleep(1)  # 睡 1 秒避免太快

        time.sleep(2)  # 分頁間隔

    # 儲存成 JSON
    with open("stock_pttweb_articles.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
