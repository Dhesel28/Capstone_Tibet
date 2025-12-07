#!/usr/bin/env python3
"""
Scraper for Chinese State Media Tibet articles (2023-2024)
Targets: China Daily, Xinhua, Global Times, ECNS
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime
import re
from urllib.parse import urljoin, quote
import json

# Headers to mimic browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

BASE_PATH = '/Users/dhekha/Desktop/Capstone_Tibet'

def fetch_page(url, timeout=30):
    """Fetch a page with retry logic"""
    for attempt in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)
    return None

def scrape_china_daily_search(query="Tibet", years=[2023, 2024]):
    """Scrape China Daily search results"""
    articles = []

    for year in years:
        print(f"\nScraping China Daily for {year}...")

        # China Daily search URL
        for page in range(1, 20):  # Up to 20 pages
            search_url = f"https://www.chinadaily.com.cn/search?query={query}&from={year}-01-01&to={year}-12-31&page={page}"

            print(f"  Page {page}: {search_url}")
            response = fetch_page(search_url)

            if not response:
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find article links
            results = soup.find_all('div', class_='search-result') or soup.find_all('li', class_='item')

            if not results:
                print(f"  No more results on page {page}")
                break

            for result in results:
                try:
                    link = result.find('a')
                    if link and link.get('href'):
                        url = link.get('href')
                        if not url.startswith('http'):
                            url = urljoin('https://www.chinadaily.com.cn', url)

                        title = link.get_text(strip=True)

                        articles.append({
                            'url': url,
                            'headline': title,
                            'source': 'China Daily',
                            'year': year,
                            'fetched_at': datetime.now().isoformat()
                        })
                except Exception as e:
                    continue

            time.sleep(random.uniform(1, 3))

    return articles

def scrape_xinhua_search(query="Tibet", years=[2023, 2024]):
    """Scrape Xinhua search results"""
    articles = []

    for year in years:
        print(f"\nScraping Xinhua for {year}...")

        # Xinhua search API
        for page in range(1, 20):
            search_url = f"http://so.news.cn/getNews?keyword={quote(query)}&curPage={page}&sortField=0&searchFields=1&lang=en"

            print(f"  Page {page}")
            response = fetch_page(search_url)

            if not response:
                break

            try:
                data = response.json()
                items = data.get('content', {}).get('results', [])

                if not items:
                    print(f"  No more results")
                    break

                for item in items:
                    pub_date = item.get('pubtime', '')
                    if pub_date and str(year) in pub_date:
                        articles.append({
                            'url': item.get('url', ''),
                            'headline': item.get('title', ''),
                            'source': 'Xinhua',
                            'year': year,
                            'publication_date': pub_date,
                            'fetched_at': datetime.now().isoformat()
                        })
            except:
                # Try HTML parsing
                soup = BeautifulSoup(response.text, 'html.parser')
                results = soup.find_all('div', class_='item') or soup.find_all('li')

                for result in results:
                    link = result.find('a')
                    if link:
                        articles.append({
                            'url': link.get('href', ''),
                            'headline': link.get_text(strip=True),
                            'source': 'Xinhua',
                            'year': year,
                            'fetched_at': datetime.now().isoformat()
                        })

            time.sleep(random.uniform(1, 3))

    return articles

def scrape_global_times(query="Tibet", years=[2023, 2024]):
    """Scrape Global Times search results"""
    articles = []

    for year in years:
        print(f"\nScraping Global Times for {year}...")

        for page in range(1, 20):
            search_url = f"https://www.globaltimes.cn/search/index.html?q={quote(query)}&page={page}"

            print(f"  Page {page}")
            response = fetch_page(search_url)

            if not response:
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='row-content') or soup.find_all('li', class_='item')

            if not results:
                break

            for result in results:
                link = result.find('a')
                if link:
                    url = link.get('href', '')
                    if not url.startswith('http'):
                        url = urljoin('https://www.globaltimes.cn', url)

                    # Check if URL contains year
                    if f'/{year}' in url or f'{year}' in url:
                        articles.append({
                            'url': url,
                            'headline': link.get_text(strip=True),
                            'source': 'Global Times',
                            'year': year,
                            'fetched_at': datetime.now().isoformat()
                        })

            time.sleep(random.uniform(1, 3))

    return articles

def scrape_ecns(query="Tibet", years=[2023, 2024]):
    """Scrape ECNS (English China News Service)"""
    articles = []

    for year in years:
        print(f"\nScraping ECNS for {year}...")

        for page in range(1, 20):
            search_url = f"http://www.ecns.cn/search.html?keyword={quote(query)}&page={page}"

            print(f"  Page {page}")
            response = fetch_page(search_url)

            if not response:
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='list-item') or soup.find_all('li')

            if not results:
                break

            for result in results:
                link = result.find('a')
                date_elem = result.find('span', class_='date') or result.find('time')

                if link:
                    url = link.get('href', '')
                    if not url.startswith('http'):
                        url = urljoin('http://www.ecns.cn', url)

                    pub_date = date_elem.get_text(strip=True) if date_elem else ''

                    if str(year) in url or str(year) in pub_date:
                        articles.append({
                            'url': url,
                            'headline': link.get_text(strip=True),
                            'source': 'ECNS',
                            'year': year,
                            'publication_date': pub_date,
                            'fetched_at': datetime.now().isoformat()
                        })

            time.sleep(random.uniform(1, 3))

    return articles

def fetch_article_text(url):
    """Fetch full article text"""
    response = fetch_page(url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove unwanted elements
    for elem in soup.find_all(['script', 'style', 'nav', 'footer', 'aside', 'iframe']):
        elem.decompose()

    # Try different content selectors
    content = None
    for selector in ['article', '.article-content', '.content', '#content', '.story-body', '.text']:
        content = soup.select_one(selector)
        if content:
            break

    if not content:
        content = soup.find('div', class_=re.compile(r'(article|content|story|text)', re.I))

    if content:
        paragraphs = content.find_all('p')
        text = ' '.join([p.get_text(strip=True) for p in paragraphs])
        return text

    return None

def main():
    print("=" * 70)
    print("SCRAPING CHINESE STATE MEDIA FOR TIBET ARTICLES (2023-2024)")
    print("=" * 70)

    all_articles = []

    # Scrape each source
    # all_articles.extend(scrape_china_daily_search())
    # all_articles.extend(scrape_xinhua_search())
    # all_articles.extend(scrape_global_times())
    # all_articles.extend(scrape_ecns())

    # For now, let's try a simpler approach - scrape directly from site maps
    # China Daily Tibet section
    print("\nScraping China Daily Tibet section...")
    tibet_urls = [
        'https://www.chinadaily.com.cn/china/xizang.html',
        'https://www.chinadaily.com.cn/china/tibet.html',
    ]

    for base_url in tibet_urls:
        response = fetch_page(base_url)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)

            for link in links:
                url = link.get('href', '')
                if 'tibet' in url.lower() or 'xizang' in url.lower():
                    if '/2023' in url or '/2024' in url:
                        full_url = urljoin(base_url, url)
                        all_articles.append({
                            'url': full_url,
                            'headline': link.get_text(strip=True),
                            'source': 'China Daily',
                            'fetched_at': datetime.now().isoformat()
                        })

    print(f"\nFound {len(all_articles)} article URLs")

    # Remove duplicates
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)

    print(f"After deduplication: {len(unique_articles)} unique articles")

    # Fetch article text
    print("\nFetching article text...")
    for i, article in enumerate(unique_articles):
        print(f"  [{i+1}/{len(unique_articles)}] {article['url'][:60]}...")
        text = fetch_article_text(article['url'])
        article['body_text'] = text if text else ''
        time.sleep(random.uniform(0.5, 1.5))

    # Save results
    if unique_articles:
        df = pd.DataFrame(unique_articles)
        df['source_category'] = 'Chinese State Media'

        output_path = f'{BASE_PATH}/data/raw/china_daily/scraped_2023_2024.csv'
        df.to_csv(output_path, index=False)
        print(f"\nSaved {len(df)} articles to {output_path}")

        # Show summary
        print("\nSummary by source and year:")
        if 'year' in df.columns:
            print(df.groupby(['source', 'year']).size())

    return unique_articles

if __name__ == "__main__":
    main()
