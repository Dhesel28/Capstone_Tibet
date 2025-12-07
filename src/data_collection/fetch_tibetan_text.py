"""
Fetch article text for Tibetan-focused media sources.
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


class TibetanArticleFetcher:
    """Fetches full article text from Tibetan news sources."""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def fetch_article(self, url: str, source: str) -> dict:
        """Fetch article based on source."""
        try:
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()

            if 'phayul' in url.lower():
                return self._parse_phayul(response.text, url)
            elif 'tibet.net' in url.lower():
                return self._parse_tibetnet(response.text, url)
            else:
                return self._parse_generic(response.text, url, source)

        except Exception as e:
            return {"url": url, "error": str(e), "body_text": None}

    def _parse_phayul(self, html: str, url: str) -> dict:
        """Parse Phayul article."""
        soup = BeautifulSoup(html, 'html.parser')

        title = ""
        title_tag = soup.find('h1', class_='entry-title') or soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        body_text = ""
        article = soup.find('div', class_='entry-content') or \
                 soup.find('article') or \
                 soup.find('div', class_='post-content')
        if article:
            paragraphs = article.find_all('p')
            body_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "source": "Phayul",
            "source_category": "Tibetan Media",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_tibetnet(self, html: str, url: str) -> dict:
        """Parse Tibet.net (CTA) article."""
        soup = BeautifulSoup(html, 'html.parser')

        title = ""
        title_tag = soup.find('h1', class_='entry-title') or soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        body_text = ""
        article = soup.find('div', class_='entry-content') or \
                 soup.find('article') or \
                 soup.find('div', class_='content')
        if article:
            paragraphs = article.find_all('p')
            body_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "source": "Central Tibetan Administration",
            "source_category": "Tibetan Media",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_generic(self, html: str, url: str, source: str) -> dict:
        """Generic parser for Tibetan news sites."""
        soup = BeautifulSoup(html, 'html.parser')

        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        paragraphs = soup.find_all('p')
        body_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50)

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "source": source,
            "source_category": "Tibetan Media",
            "fetched_at": datetime.now().isoformat()
        }


def main():
    """Fetch text for Tibetan media articles."""

    input_file = "data/raw/tibetan_media/tibetan_media_articles.csv"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return

    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} articles")

    fetcher = TibetanArticleFetcher()
    results = []
    failed = []

    total = len(df)

    print("=" * 70)
    print("FETCHING TIBETAN MEDIA ARTICLE TEXT")
    print("=" * 70)

    for i, (_, row) in enumerate(df.iterrows()):
        url = row['url']
        source = row.get('source_name', 'Unknown')

        if (i + 1) % 20 == 0:
            print(f"Progress: {i + 1}/{total} - Success: {len(results)}")

        try:
            result = fetcher.fetch_article(url, source)

            if result and result.get('body_text') and len(result.get('body_text', '')) > 100:
                result['original_title'] = row.get('title', '')
                result['source_name'] = source
                results.append(result)
            else:
                failed.append({'url': url, 'source': source})

        except Exception as e:
            failed.append({'url': url, 'source': source, 'error': str(e)})

        time.sleep(random.uniform(0.5, 1.0))

    # Save results
    print("\n" + "=" * 70)
    print("FETCH COMPLETE")
    print("=" * 70)
    print(f"Total: {total}")
    print(f"Success: {len(results)}")
    print(f"Failed: {len(failed)}")

    if results:
        results_df = pd.DataFrame(results)

        print("\nBy source:")
        print(results_df['source'].value_counts().to_string())

        avg_len = results_df['body_text'].str.len().mean()
        print(f"\nAverage text length: {avg_len:.0f} chars")

        output_file = "data/raw/tibetan_media/tibetan_media_with_text.csv"
        results_df.to_csv(output_file, index=False)
        print(f"\nSaved to: {output_file}")

    return results_df if results else None


if __name__ == "__main__":
    main()
