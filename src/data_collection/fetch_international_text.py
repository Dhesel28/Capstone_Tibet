"""
Fetch article text for International/Neutral media sources.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import re
from datetime import datetime


class InternationalArticleFetcher:
    """Fetches full article text from international news sources."""

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

            if 'aljazeera' in source.lower():
                return self._parse_aljazeera(response.text, url)
            elif 'dw' in source.lower() or 'deutsche' in source.lower():
                return self._parse_dw(response.text, url)
            elif 'scmp' in source.lower() or 'south china' in source.lower():
                return self._parse_scmp(response.text, url)
            elif 'reuters' in source.lower():
                return self._parse_reuters(response.text, url)
            elif 'bbc' in source.lower():
                return self._parse_bbc(response.text, url)
            elif 'france24' in source.lower():
                return self._parse_france24(response.text, url)
            else:
                return self._parse_generic(response.text, url)

        except Exception as e:
            return {"url": url, "error": str(e), "body_text": None}

    def _parse_aljazeera(self, html: str, url: str) -> dict:
        """Parse Al Jazeera article."""
        soup = BeautifulSoup(html, 'html.parser')

        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        body_text = ""
        article = soup.find('div', class_='wysiwyg') or \
                 soup.find('article') or \
                 soup.find('div', class_='article-body')
        if article:
            paragraphs = article.find_all('p')
            body_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "source": "Al Jazeera",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_dw(self, html: str, url: str) -> dict:
        """Parse Deutsche Welle article."""
        soup = BeautifulSoup(html, 'html.parser')

        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        body_text = ""
        article = soup.find('div', class_='rich-text') or \
                 soup.find('article') or \
                 soup.find('div', class_='longText')
        if article:
            paragraphs = article.find_all('p')
            body_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "source": "Deutsche Welle",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_scmp(self, html: str, url: str) -> dict:
        """Parse South China Morning Post article."""
        soup = BeautifulSoup(html, 'html.parser')

        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        body_text = ""
        article = soup.find('div', class_='article-body') or \
                 soup.find('article') or \
                 soup.find('div', {'data-qa': 'article-body'})
        if article:
            paragraphs = article.find_all('p')
            body_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "source": "SCMP",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_reuters(self, html: str, url: str) -> dict:
        """Parse Reuters article."""
        soup = BeautifulSoup(html, 'html.parser')

        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        body_text = ""
        article = soup.find('article') or \
                 soup.find('div', class_='article-body') or \
                 soup.find('div', {'data-testid': 'article-body'})
        if article:
            paragraphs = article.find_all('p')
            body_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "source": "Reuters",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_bbc(self, html: str, url: str) -> dict:
        """Parse BBC article."""
        soup = BeautifulSoup(html, 'html.parser')

        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        body_text = ""
        article = soup.find('article') or \
                 soup.find('div', {'data-component': 'text-block'})
        if article:
            paragraphs = article.find_all('p')
            body_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)

        # Fallback
        if not body_text:
            all_p = soup.find_all('p')
            body_text = '\n\n'.join(p.get_text(strip=True) for p in all_p if len(p.get_text(strip=True)) > 50)

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "source": "BBC",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_france24(self, html: str, url: str) -> dict:
        """Parse France 24 article."""
        soup = BeautifulSoup(html, 'html.parser')

        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        body_text = ""
        article = soup.find('div', class_='t-content__body') or \
                 soup.find('article') or \
                 soup.find('div', class_='article-body')
        if article:
            paragraphs = article.find_all('p')
            body_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "source": "France 24",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_generic(self, html: str, url: str) -> dict:
        """Generic parser."""
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
            "source": "Unknown",
            "fetched_at": datetime.now().isoformat()
        }


def main():
    """Fetch text for international media articles."""

    input_file = "data/raw/neutral_sources/international_media_tibet.csv"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return

    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} articles")

    fetcher = InternationalArticleFetcher()
    results = []
    failed = []

    total = len(df)
    start_time = datetime.now()

    print("=" * 70)
    print("FETCHING INTERNATIONAL MEDIA ARTICLE TEXT")
    print("=" * 70)

    for i, (_, row) in enumerate(df.iterrows()):
        url = row['url']
        source = row.get('source_name', row.get('source_domain', 'unknown'))

        if (i + 1) % 50 == 0:
            elapsed = (datetime.now() - start_time).seconds
            rate = (i + 1) / max(elapsed, 1) * 60
            print(f"\nProgress: {i + 1}/{total} ({100*(i+1)//total}%)")
            print(f"  Success: {len(results)}, Failed: {len(failed)}")
            print(f"  Rate: {rate:.1f} articles/min")

        try:
            result = fetcher.fetch_article(url, source)

            if result and result.get('body_text') and len(result.get('body_text', '')) > 100:
                result['original_title'] = row.get('title', '')
                result['source_name'] = source
                result['source_category'] = 'International/Neutral'
                results.append(result)
            else:
                failed.append({'url': url, 'source': source, 'reason': 'No text'})

        except Exception as e:
            failed.append({'url': url, 'source': source, 'reason': str(e)})

        time.sleep(random.uniform(0.5, 1.5))

        # Checkpoint every 100
        if (i + 1) % 100 == 0:
            checkpoint_df = pd.DataFrame(results)
            checkpoint_df.to_csv("data/raw/neutral_sources/fetch_checkpoint.csv", index=False)
            print(f"  [Checkpoint: {len(results)} articles]")

    # Final save
    print("\n" + "=" * 70)
    print("FETCH COMPLETE")
    print("=" * 70)
    print(f"Total: {total}")
    print(f"Success: {len(results)}")
    print(f"Failed: {len(failed)}")
    print(f"Success rate: {100*len(results)//total}%")

    if results:
        results_df = pd.DataFrame(results)

        print("\nBy source:")
        print(results_df['source_name'].value_counts().to_string())

        avg_len = results_df['body_text'].str.len().mean()
        print(f"\nAverage text length: {avg_len:.0f} chars")

        output_file = "data/raw/neutral_sources/international_media_with_text.csv"
        results_df.to_csv(output_file, index=False)
        print(f"\nSaved to: {output_file}")

    if failed:
        failed_df = pd.DataFrame(failed)
        failed_df.to_csv("data/raw/neutral_sources/failed_urls.csv", index=False)

    return results_df if results else None


if __name__ == "__main__":
    main()
