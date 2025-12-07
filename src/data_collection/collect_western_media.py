"""
Collect Western Media Sources from GDELT (2017-2024)
Expands beyond Guardian to include major Western news outlets.

Western Media Sources:
- New York Times
- Washington Post
- BBC (UK)
- CNN
- NPR
- The Independent
- The Telegraph
- Los Angeles Times
- Wall Street Journal
- The Atlantic
- Time Magazine
- Newsweek
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


# GDELT API endpoint
GDELT_API = "https://api.gdeltproject.org/api/v2/doc/doc"

# Western media domains
WESTERN_SOURCES = {
    # US Sources
    'nytimes.com': 'New York Times',
    'washingtonpost.com': 'Washington Post',
    'cnn.com': 'CNN',
    'npr.org': 'NPR',
    'latimes.com': 'Los Angeles Times',
    'wsj.com': 'Wall Street Journal',
    'theatlantic.com': 'The Atlantic',
    'time.com': 'Time Magazine',
    'newsweek.com': 'Newsweek',
    'usatoday.com': 'USA Today',
    'nbcnews.com': 'NBC News',
    'cbsnews.com': 'CBS News',
    'abcnews.go.com': 'ABC News',
    'politico.com': 'Politico',
    'vox.com': 'Vox',

    # UK Sources
    'bbc.com': 'BBC',
    'bbc.co.uk': 'BBC',
    'independent.co.uk': 'The Independent',
    'telegraph.co.uk': 'The Telegraph',
    'thetimes.co.uk': 'The Times (UK)',
    'dailymail.co.uk': 'Daily Mail',

    # Other Western
    'theglobeandmail.com': 'Globe and Mail (Canada)',
    'smh.com.au': 'Sydney Morning Herald',
    'theage.com.au': 'The Age (Australia)',
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def search_gdelt_western(year, domain=None):
    """Search GDELT for Western media Tibet coverage."""

    articles = []

    # Build query - simpler format works better
    if domain:
        query = f"tibet domain:{domain}"
    else:
        query = "tibet"

    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": 250,
        "format": "json",
        "startdatetime": f"{year}0101000000",
        "enddatetime": f"{year}1231235959",
        "sort": "datedesc"
    }

    try:
        response = requests.get(GDELT_API, params=params, timeout=60)

        if response.status_code == 200:
            data = response.json()

            if "articles" in data:
                for article in data["articles"]:
                    url = article.get("url", "")

                    # Identify source
                    source_name = "Unknown"
                    for domain_key, name in WESTERN_SOURCES.items():
                        if domain_key in url.lower():
                            source_name = name
                            break

                    articles.append({
                        "url": url,
                        "title": article.get("title", ""),
                        "seendate": article.get("seendate", ""),
                        "source_name": source_name,
                        "domain": article.get("domain", ""),
                        "language": article.get("language", ""),
                        "source_category": "Western Media",
                        "collection_year": year
                    })

    except Exception as e:
        print(f"    GDELT error: {e}")

    return articles


def fetch_article_text(url, source_name):
    """Fetch full article text."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()

        # Source-specific parsing
        if 'nytimes' in url:
            article = soup.find('article') or soup.find('div', class_=re.compile('story|article'))
        elif 'washingtonpost' in url:
            article = soup.find('article') or soup.find('div', class_=re.compile('article-body'))
        elif 'bbc' in url:
            article = soup.find('article') or soup.find('div', {'data-component': 'text-block'})
        elif 'cnn' in url:
            article = soup.find('article') or soup.find('div', class_=re.compile('article__content'))
        else:
            article = soup.find('article') or soup.find('div', class_=re.compile('article|content|story|post'))

        if article:
            paragraphs = article.find_all('p')
        else:
            paragraphs = soup.find_all('p')

        # Filter and join paragraphs
        text = '\n\n'.join(
            p.get_text(strip=True)
            for p in paragraphs
            if len(p.get_text(strip=True)) > 40
        )

        # Get title
        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        return title, text

    except Exception as e:
        return None, None


def collect_western_media(start_year=2017, end_year=2024):
    """Collect Western media articles from GDELT."""

    all_articles = []

    print("=" * 70)
    print("WESTERN MEDIA COLLECTION FROM GDELT (2017-2024)")
    print("=" * 70)
    print(f"Sources: {len(WESTERN_SOURCES)} Western outlets")
    print("=" * 70)

    for year in range(start_year, end_year + 1):
        print(f"\n--- Year {year} ---")
        year_articles = []

        # Search by major domains individually for better coverage
        major_domains = [
            'nytimes.com', 'washingtonpost.com', 'bbc.com', 'cnn.com',
            'npr.org', 'independent.co.uk', 'telegraph.co.uk'
        ]

        for domain in major_domains:
            print(f"  Searching {WESTERN_SOURCES.get(domain, domain)}...")
            articles = search_gdelt_western(year, domain)
            print(f"    Found {len(articles)} articles")
            year_articles.extend(articles)
            time.sleep(1)  # Rate limiting

        # Also do a general search
        print(f"  General Western media search...")
        general_articles = search_gdelt_western(year)
        print(f"    Found {len(general_articles)} articles")
        year_articles.extend(general_articles)

        # Remove duplicates by URL
        seen_urls = set()
        unique_articles = []
        for article in year_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)

        print(f"  Year {year} unique articles: {len(unique_articles)}")

        # Fetch text for articles
        fetched = 0
        target = min(100, len(unique_articles))  # Target per year

        print(f"  Fetching article text (target: {target})...")

        for article in unique_articles:
            if fetched >= target:
                break

            url = article['url']
            source = article['source_name']

            title, text = fetch_article_text(url, source)

            if text and len(text) > 200:
                article['headline'] = title or article.get('title', '')
                article['body_text'] = text
                article['fetched_at'] = datetime.now().isoformat()
                all_articles.append(article)
                fetched += 1

                if fetched % 20 == 0:
                    print(f"    Fetched {fetched}/{target}")

            time.sleep(random.uniform(0.5, 1.5))

        print(f"  Successfully fetched: {fetched} articles")

    # Save results
    if all_articles:
        df = pd.DataFrame(all_articles)

        print("\n" + "=" * 70)
        print("COLLECTION COMPLETE")
        print("=" * 70)
        print(f"Total articles with text: {len(df)}")

        if 'source_name' in df.columns:
            print("\nBy source:")
            print(df['source_name'].value_counts().head(15))

        if 'collection_year' in df.columns:
            print("\nBy year:")
            print(df['collection_year'].value_counts().sort_index())

        # Calculate average text length
        if 'body_text' in df.columns:
            avg_len = df['body_text'].str.len().mean()
            print(f"\nAverage article length: {avg_len:.0f} characters")

        output_path = "data/raw/western_media/gdelt_western_media_with_text.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"\nSaved to: {output_path}")

        return df

    return pd.DataFrame()


def merge_western_sources():
    """Merge GDELT Western media with Guardian data."""

    print("\n" + "=" * 70)
    print("MERGING WESTERN MEDIA SOURCES")
    print("=" * 70)

    dfs = []

    # Guardian data (2008-2024)
    guardian_path = "data/raw/guardian/guardian_tibet_articles.csv"
    if os.path.exists(guardian_path):
        guardian_df = pd.read_csv(guardian_path)
        guardian_df['source_name'] = 'The Guardian'
        guardian_df['source_category'] = 'Western Media'
        guardian_df['data_source'] = 'Guardian API'
        dfs.append(guardian_df)
        print(f"Guardian (2008-2024): {len(guardian_df)} articles")

    # GDELT Western media (2017-2024)
    gdelt_path = "data/raw/western_media/gdelt_western_media_with_text.csv"
    if os.path.exists(gdelt_path):
        gdelt_df = pd.read_csv(gdelt_path)
        gdelt_df['data_source'] = 'GDELT'
        dfs.append(gdelt_df)
        print(f"GDELT Western (2017-2024): {len(gdelt_df)} articles")

    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        combined['source_category'] = 'Western Media'

        # Remove duplicates
        if 'url' in combined.columns:
            original_len = len(combined)
            combined = combined.drop_duplicates(subset=['url'], keep='first')
            print(f"Removed {original_len - len(combined)} duplicates")

        output_path = "data/processed/western_media_2008_2024.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        combined.to_csv(output_path, index=False)

        print(f"\n{'=' * 70}")
        print(f"MERGED WESTERN MEDIA: {len(combined)} total articles")
        print(f"{'=' * 70}")

        if 'source_name' in combined.columns:
            print("\nBy source:")
            print(combined['source_name'].value_counts())

        if 'collection_year' in combined.columns:
            print("\nBy year:")
            print(combined['collection_year'].value_counts().sort_index())

        print(f"\nSaved to: {output_path}")
        return combined

    return pd.DataFrame()


if __name__ == "__main__":
    # Collect Western media from GDELT
    df = collect_western_media(2017, 2024)

    # Merge with Guardian data
    if len(df) > 0:
        merged = merge_western_sources()
