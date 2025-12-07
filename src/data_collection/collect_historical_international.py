"""
Historical International Media Collection (2008-2016)
Uses APIs and archives:
1. Al Jazeera (has archive)
2. BBC News Archive
3. Deutsche Welle Archive
4. Reuters via Wayback Machine
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


def search_wayback_machine(domain, year, limit=50):
    """Search Wayback Machine for historical snapshots."""
    articles = []

    cdx_url = "http://web.archive.org/cdx/search/cdx"

    # Search for Tibet-related URLs
    params = {
        'url': f'{domain}/*tibet*',
        'matchType': 'prefix',
        'from': f'{year}0101',
        'to': f'{year}1231',
        'output': 'json',
        'limit': limit * 2,
        'filter': 'statuscode:200',
        'collapse': 'urlkey'
    }

    try:
        response = requests.get(cdx_url, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1:
                for row in data[1:limit+1]:
                    if len(row) >= 3:
                        timestamp, original_url = row[1], row[2]
                        wayback_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
                        articles.append({
                            'url': wayback_url,
                            'original_url': original_url,
                            'timestamp': timestamp,
                            'source_domain': domain,
                            'year': year
                        })
    except Exception as e:
        print(f"    Wayback error: {e}")

    return articles


def search_bbc_archive(year):
    """Search BBC News archive for Tibet articles."""
    articles = []

    # BBC has a search API
    search_url = f"https://www.bbc.co.uk/search"
    params = {
        'q': 'Tibet',
        'filter': 'news',
        'd': 'YEAR',
        'page': 1
    }

    try:
        # BBC archive search
        for page in range(1, 6):
            params['page'] = page
            response = requests.get(search_url, params=params, headers=HEADERS, timeout=30)
            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find article links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if f'/news/' in href and str(year) in href:
                    title = link.get_text(strip=True)
                    if title and 'tibet' in title.lower():
                        full_url = href if href.startswith('http') else f"https://www.bbc.co.uk{href}"
                        articles.append({
                            'url': full_url,
                            'title': title,
                            'source': 'BBC',
                            'source_domain': 'bbc.com',
                            'year': year
                        })

            time.sleep(1)

    except Exception as e:
        print(f"    BBC search error: {e}")

    return articles


def fetch_article_text(url, source):
    """Fetch article text from URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove scripts and styles
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()

        # Source-specific parsing
        if 'bbc' in source.lower():
            article = soup.find('article') or soup.find('div', {'data-component': 'text-block'})
        elif 'aljazeera' in source.lower():
            article = soup.find('div', class_='wysiwyg') or soup.find('article')
        elif 'dw' in source.lower():
            article = soup.find('div', class_='rich-text') or soup.find('article')
        else:
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


def collect_historical_international(start_year=2008, end_year=2016):
    """Collect historical international media articles."""

    all_articles = []

    # International media domains
    domains = {
        'aljazeera.com': 'Al Jazeera',
        'dw.com': 'Deutsche Welle',
        'bbc.com': 'BBC',
        'bbc.co.uk': 'BBC',
        'reuters.com': 'Reuters',
        'france24.com': 'France 24',
        'scmp.com': 'South China Morning Post'
    }

    print("=" * 70)
    print("HISTORICAL INTERNATIONAL MEDIA COLLECTION (2008-2016)")
    print("=" * 70)

    for year in range(start_year, end_year + 1):
        print(f"\n--- Year {year} ---")
        year_articles = []

        # Search Wayback Machine for each domain
        for domain, source_name in domains.items():
            print(f"  Searching Wayback: {source_name}...")
            wb_articles = search_wayback_machine(domain, year, limit=30)
            for a in wb_articles:
                a['source_name'] = source_name
            print(f"    Found {len(wb_articles)} archived URLs")
            year_articles.extend(wb_articles)
            time.sleep(0.5)

        # Also try BBC archive directly
        bbc_articles = search_bbc_archive(year)
        print(f"  BBC direct search: {len(bbc_articles)} articles")
        year_articles.extend(bbc_articles)

        print(f"  Year {year} total candidates: {len(year_articles)}")

        # Fetch text for candidates
        fetched = 0
        target = 40  # Target per year

        for article in year_articles:
            if fetched >= target:
                break

            url = article.get('url', '')
            source = article.get('source_name', article.get('source', 'Unknown'))
            title, text = fetch_article_text(url, source)

            if text and len(text) > 200:
                article['headline'] = title or article.get('title', '')
                article['body_text'] = text
                article['source_category'] = 'International/Neutral'
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

        if 'source_name' in df.columns:
            print("\nBy source:")
            print(df['source_name'].value_counts())

        if 'collection_year' in df.columns:
            print("\nBy year:")
            print(df['collection_year'].value_counts().sort_index())

        output_path = "data/raw/neutral_sources/historical_international_2008_2016.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"\nSaved to: {output_path}")

        return df

    return pd.DataFrame()


if __name__ == "__main__":
    df = collect_historical_international(2008, 2016)
