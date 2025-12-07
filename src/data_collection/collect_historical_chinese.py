"""
Historical Chinese State Media Collection (2008-2016)
Uses multiple approaches:
1. China Daily Archive (has historical search)
2. Xinhua Archive
3. Wayback Machine for historical snapshots
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def search_china_daily_archive(year):
    """Search China Daily archive for Tibet articles."""
    articles = []

    # China Daily has a search archive
    base_url = "https://www.chinadaily.com.cn/china/tibet"

    print(f"  Searching China Daily archive for {year}...")

    try:
        # Try the Tibet section archive pages
        for page in range(1, 11):  # Try first 10 pages
            url = f"https://www.chinadaily.com.cn/china/tibet/page_{page}.html" if page > 1 else base_url

            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find article links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                # China Daily URLs often contain date: /a/202301/15/...
                if f'/a/{year}' in href or f'/{year}/' in href:
                    title = link.get_text(strip=True)
                    if title and len(title) > 10 and 'tibet' in title.lower():
                        full_url = href if href.startswith('http') else f"https://www.chinadaily.com.cn{href}"
                        articles.append({
                            'url': full_url,
                            'title': title,
                            'source': 'China Daily',
                            'year': year
                        })

            time.sleep(1)

    except Exception as e:
        print(f"    Error: {e}")

    return articles


def search_wayback_machine(domain, query, year):
    """Search Wayback Machine for historical snapshots."""
    articles = []

    # Wayback Machine CDX API
    cdx_url = "http://web.archive.org/cdx/search/cdx"

    params = {
        'url': f'{domain}/*tibet*',
        'matchType': 'prefix',
        'from': f'{year}0101',
        'to': f'{year}1231',
        'output': 'json',
        'limit': 100,
        'filter': 'statuscode:200',
        'collapse': 'urlkey'
    }

    try:
        response = requests.get(cdx_url, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1:  # First row is header
                for row in data[1:]:
                    timestamp, original_url = row[1], row[2]
                    wayback_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
                    articles.append({
                        'url': wayback_url,
                        'original_url': original_url,
                        'timestamp': timestamp,
                        'source': domain,
                        'year': year
                    })
    except Exception as e:
        print(f"    Wayback error for {domain}: {e}")

    return articles


def fetch_article_text(url):
    """Fetch article text from URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()

        # Try to find article content
        article = soup.find('article') or soup.find('div', class_=re.compile('article|content|story'))

        if article:
            paragraphs = article.find_all('p')
        else:
            paragraphs = soup.find_all('p')

        text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)

        # Get title
        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        return title, text

    except Exception as e:
        return None, None


def collect_historical_chinese_media(start_year=2008, end_year=2016):
    """Collect historical Chinese state media articles."""

    all_articles = []

    # Chinese state media domains for Wayback Machine
    domains = [
        'chinadaily.com.cn',
        'xinhuanet.com',
        'globaltimes.cn',
        'english.cctv.com',
        'ecns.cn'
    ]

    print("=" * 70)
    print("HISTORICAL CHINESE STATE MEDIA COLLECTION (2008-2016)")
    print("=" * 70)

    for year in range(start_year, end_year + 1):
        print(f"\n--- Year {year} ---")
        year_articles = []

        # Method 1: Search Wayback Machine for each domain
        for domain in domains:
            print(f"  Searching Wayback Machine: {domain}...")
            wb_articles = search_wayback_machine(domain, 'tibet', year)
            print(f"    Found {len(wb_articles)} archived URLs")
            year_articles.extend(wb_articles)
            time.sleep(1)

        # Method 2: China Daily archive (if accessible)
        cd_articles = search_china_daily_archive(year)
        print(f"  China Daily archive: {len(cd_articles)} articles")
        year_articles.extend(cd_articles)

        print(f"  Year {year} total candidates: {len(year_articles)}")

        # Fetch text for top candidates (limit per year)
        fetched = 0
        target = 50  # Target 50 articles per year

        for article in year_articles[:min(len(year_articles), target * 2)]:
            if fetched >= target:
                break

            url = article.get('url', '')
            title, text = fetch_article_text(url)

            if text and len(text) > 200:
                article['headline'] = title or article.get('title', '')
                article['body_text'] = text
                article['source_category'] = 'Chinese State Media'
                article['collection_year'] = year
                article['fetched_at'] = datetime.now().isoformat()
                all_articles.append(article)
                fetched += 1

            time.sleep(random.uniform(1, 2))

        print(f"  Successfully fetched: {fetched} articles")

    # Save results
    if all_articles:
        df = pd.DataFrame(all_articles)

        print("\n" + "=" * 70)
        print("COLLECTION COMPLETE")
        print("=" * 70)
        print(f"Total articles: {len(df)}")

        if 'collection_year' in df.columns:
            print("\nBy year:")
            print(df['collection_year'].value_counts().sort_index())

        output_path = "data/raw/chinese_state_media/historical_chinese_2008_2016.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"\nSaved to: {output_path}")

        return df

    return pd.DataFrame()


if __name__ == "__main__":
    df = collect_historical_chinese_media(2008, 2016)
