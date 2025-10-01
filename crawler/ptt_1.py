import requests
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime

BASE_URL = "https://pttweb.tw"
BOARD = "stock"
PAGE_LIMIT = 10  # 最多抓幾頁文章

def get_page_url(page_num):
    if page_num == 1:
        return f"{BASE_URL}/{BOARD}/"
    else:
        return f"{BASE_URL}/{BOARD}/page/{page_num}/"

def parse_article_list(page_url):
    resp = requests.get(page_url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    articles = []
    for title_div in soup.select("div.title"):
        a = title_div.find("a")
        if a:
            articles.append({
                "title": a.get_text().strip(),
                "url": BASE_URL + a["href"]
            })
    return articles

def parse_article(article_url):
    resp = requests.get(article_url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # 標題
    title_tag = soup.find("h1")
    title = title_tag.get_text().strip() if title_tag else ""

    # 內容
    content_div = soup.find("div", class_="content")
    content = ""
    if content_div:
        # 移除 meta 資訊
        for meta in content_div.select("div.article-metaline, div.article-metaline-right, span.push-tag, span.push-userid, span.push-content, span.push-ipdatetime"):
            meta.decompose()
        content = content_div.get_text().strip()

    # 推文數
    push_tags = soup.select("div.push span.push-tag")
    push = sum(1 for tag in push_tags if tag.get_text().strip() == "推")
    boo = sum(1 for tag in push_tags if tag.get_text().strip() == "噓")
    arrow = sum(1 for tag in push_tags if tag.get_text().strip() == "→")
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
                "board": BOARD,
                "url": art["url"],
                "title": art_detail["title"],
                "content": art_detail["content"],
                "push": art_detail["push"],
                "boo": art_detail["boo"],
                "arrow": art_detail["arrow"],
                "messages_count": art_detail["messages_count"],
                "crawl_time": datetime.now().isoformat()
            }
            results.append(record)
            time.sleep(1)  # 每篇文章睡 1 秒

        time.sleep(2)  # 每頁睡 2 秒

    # 儲存成 CSV
    csv_file = f"{BOARD}_pttweb_articles.csv"
    fieldnames = ["board", "url", "title", "content", "push", "boo", "arrow", "messages_count", "crawl_time"]
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"Saved {len(results)} articles to {csv_file}")

if __name__ == "__main__":
    main()
