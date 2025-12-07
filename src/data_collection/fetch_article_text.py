"""
Article Text Fetcher
Capstone Project - Dhesel Khando

Fetches full article body text from URLs collected via GDELT.
Handles multiple Chinese state media domains.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from datetime import datetime
from typing import Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import os


class ArticleTextFetcher:
    """Fetches full article text from news URLs."""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    # Domain-specific parsing rules
    PARSERS = {
        "globaltimes.cn": "_parse_globaltimes",
        "chinadaily.com.cn": "_parse_chinadaily",
        "xinhuanet.com": "_parse_xinhua",
        "news.cn": "_parse_xinhua",
        "ecns.cn": "_parse_ecns",
        "cgtn.com": "_parse_cgtn",
        "china.org.cn": "_parse_chinaorg",
        "cri.cn": "_parse_cri",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def fetch_article(self, url: str, domain: str = None) -> Optional[Dict]:
        """
        Fetch and parse article from URL.

        Args:
            url: Article URL
            domain: Source domain (auto-detected if not provided)

        Returns:
            Dict with article data or None
        """
        if not domain:
            domain = self._extract_domain(url)

        try:
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()

            # Get appropriate parser
            parser_name = self.PARSERS.get(domain, "_parse_generic")
            parser = getattr(self, parser_name)

            return parser(response.text, url)

        except Exception as e:
            return {"url": url, "error": str(e), "body_text": None}

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        for domain in self.PARSERS.keys():
            if domain in url:
                return domain
        return "generic"

    def _parse_globaltimes(self, html: str, url: str) -> Dict:
        """Parse Global Times article."""
        soup = BeautifulSoup(html, 'html.parser')

        # Title
        title = ""
        title_tag = soup.find('h3', class_='article-title') or \
                   soup.find('h1', class_='article-title') or \
                   soup.find('h1') or \
                   soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            title = title.replace(" - Global Times", "").strip()

        # Body - try multiple selectors
        body_text = ""
        article_div = soup.find('div', class_='article_content') or \
                     soup.find('div', class_='article-content') or \
                     soup.find('div', class_='article_body') or \
                     soup.find('article')

        if article_div:
            # Get all text content, not just paragraphs
            paragraphs = article_div.find_all(['p', 'div'])
            texts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Filter out navigation, ads, etc.
                if text and len(text) > 20 and not any(x in text.lower() for x in ['share', 'comment', 'related', 'recommend']):
                    texts.append(text)
            body_text = '\n\n'.join(texts)

        # If still no text, get all paragraphs from page
        if not body_text or len(body_text) < 100:
            all_paragraphs = soup.find_all('p')
            body_text = '\n\n'.join(
                p.get_text(strip=True) for p in all_paragraphs
                if len(p.get_text(strip=True)) > 30
            )

        # Date
        date_str = ""
        pub_time = soup.find('span', class_='pub_time') or \
                  soup.find('span', class_='time')
        if pub_time:
            date_match = re.search(r'(\w+ \d+, \d{4})', pub_time.get_text()) or \
                        re.search(r'(\d{4}-\d{2}-\d{2})', pub_time.get_text())
            if date_match:
                date_str = date_match.group(1)

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "publication_date": date_str,
            "source": "Global Times",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_chinadaily(self, html: str, url: str) -> Dict:
        """Parse China Daily article."""
        soup = BeautifulSoup(html, 'html.parser')

        # Title
        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            title = title.replace(" - Chinadaily.com.cn", "").strip()

        # Body
        body_text = ""
        article_div = soup.find('div', id='Content') or \
                     soup.find('div', class_='article_content') or \
                     soup.find('article')
        if article_div:
            paragraphs = article_div.find_all('p')
            body_text = '\n\n'.join(
                p.get_text(strip=True) for p in paragraphs
                if p.get_text(strip=True) and len(p.get_text(strip=True)) > 20
            )

        # Date from meta or URL
        date_str = ""
        meta_date = soup.find('meta', {'name': 'publishdate'})
        if meta_date:
            date_str = meta_date.get('content', '')
        else:
            url_match = re.search(r'/(\d{4})-(\d{2})/(\d{2})/', url) or \
                       re.search(r'/(\d{4})(\d{2})/(\d{2})/', url)
            if url_match:
                date_str = f"{url_match.group(1)}-{url_match.group(2)}-{url_match.group(3)}"

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "publication_date": date_str,
            "source": "China Daily",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_xinhua(self, html: str, url: str) -> Dict:
        """Parse Xinhua/news.cn article."""
        soup = BeautifulSoup(html, 'html.parser')

        # Title
        title = ""
        title_tag = soup.find('div', class_='head-line') or \
                   soup.find('h1', class_='title') or \
                   soup.find('h1')
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Body
        body_text = ""
        article_div = soup.find('div', id='detail') or \
                     soup.find('div', class_='article') or \
                     soup.find('div', class_='content')
        if article_div:
            paragraphs = article_div.find_all('p')
            body_text = '\n\n'.join(
                p.get_text(strip=True) for p in paragraphs
                if p.get_text(strip=True) and len(p.get_text(strip=True)) > 20
            )

        # Date from URL
        date_str = ""
        url_match = re.search(r'/(\d{4})-(\d{2})/(\d{2})/', url) or \
                   re.search(r'/(\d{4})(\d{2})/(\d{2})/', url)
        if url_match:
            date_str = f"{url_match.group(1)}-{url_match.group(2)}-{url_match.group(3)}"

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "publication_date": date_str,
            "source": "Xinhua",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_ecns(self, html: str, url: str) -> Dict:
        """Parse ECNS article."""
        soup = BeautifulSoup(html, 'html.parser')

        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        body_text = ""
        article_div = soup.find('div', class_='article_txt') or \
                     soup.find('div', class_='content')
        if article_div:
            paragraphs = article_div.find_all('p')
            body_text = '\n\n'.join(
                p.get_text(strip=True) for p in paragraphs
                if p.get_text(strip=True) and len(p.get_text(strip=True)) > 20
            )

        date_str = ""
        url_match = re.search(r'/(\d{4})/(\d{2})-(\d{2})/', url)
        if url_match:
            date_str = f"{url_match.group(1)}-{url_match.group(2)}-{url_match.group(3)}"

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "publication_date": date_str,
            "source": "ECNS",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_cgtn(self, html: str, url: str) -> Dict:
        """Parse CGTN article."""
        soup = BeautifulSoup(html, 'html.parser')

        title = ""
        title_tag = soup.find('h1', class_='title') or soup.find('h1')
        if title_tag:
            title = title_tag.get_text(strip=True)

        body_text = ""
        article_div = soup.find('div', class_='content-body') or \
                     soup.find('article')
        if article_div:
            paragraphs = article_div.find_all('p')
            body_text = '\n\n'.join(
                p.get_text(strip=True) for p in paragraphs
                if p.get_text(strip=True) and len(p.get_text(strip=True)) > 20
            )

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "publication_date": "",
            "source": "CGTN",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_chinaorg(self, html: str, url: str) -> Dict:
        """Parse China.org.cn article."""
        soup = BeautifulSoup(html, 'html.parser')

        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        body_text = ""
        article_div = soup.find('div', id='content') or \
                     soup.find('div', class_='content')
        if article_div:
            paragraphs = article_div.find_all('p')
            body_text = '\n\n'.join(
                p.get_text(strip=True) for p in paragraphs
                if p.get_text(strip=True) and len(p.get_text(strip=True)) > 20
            )

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "publication_date": "",
            "source": "China.org",
            "fetched_at": datetime.now().isoformat()
        }

    def _parse_cri(self, html: str, url: str) -> Dict:
        """Parse CRI article."""
        return self._parse_generic(html, url)

    def _parse_generic(self, html: str, url: str) -> Dict:
        """Generic parser for unknown domains."""
        soup = BeautifulSoup(html, 'html.parser')

        # Title
        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Body - get all substantial paragraphs
        paragraphs = soup.find_all('p')
        body_text = '\n\n'.join(
            p.get_text(strip=True) for p in paragraphs
            if len(p.get_text(strip=True)) > 50
        )

        return {
            "url": url,
            "headline": title,
            "body_text": body_text,
            "publication_date": "",
            "source": "Unknown",
            "fetched_at": datetime.now().isoformat()
        }

    def fetch_batch(
        self,
        urls: list,
        domains: list = None,
        delay_range: tuple = (1, 3),
        max_workers: int = 3
    ) -> pd.DataFrame:
        """
        Fetch multiple articles with rate limiting.

        Args:
            urls: List of article URLs
            domains: List of domains (parallel to urls)
            delay_range: Random delay between requests
            max_workers: Number of parallel workers

        Returns:
            DataFrame with fetched articles
        """
        results = []
        total = len(urls)

        print(f"Fetching {total} articles...")
        print("=" * 50)

        for i, url in enumerate(urls):
            domain = domains[i] if domains else None

            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{total} ({100*(i+1)//total}%)")

            result = self.fetch_article(url, domain)
            if result:
                results.append(result)

            # Rate limiting
            time.sleep(random.uniform(*delay_range))

            # Checkpoint every 100 articles
            if (i + 1) % 100 == 0:
                checkpoint_df = pd.DataFrame(results)
                checkpoint_df.to_csv("fetch_checkpoint.csv", index=False)
                print(f"  [Checkpoint: {len(results)} articles with text]")

        print(f"\nFetched {len(results)} articles")
        return pd.DataFrame(results)


def fetch_chinese_media_text():
    """Main function to fetch text for collected GDELT URLs."""

    # Load GDELT data
    input_file = "data/raw/china_daily/chinese_state_media_tibet_2008_2024.csv"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return

    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} articles from GDELT")

    # Initialize fetcher
    fetcher = ArticleTextFetcher()

    # Get URLs and domains
    urls = df['url'].tolist()
    domains = df['domain'].tolist() if 'domain' in df.columns else df['source_domain'].tolist()

    # Fetch article text
    results_df = fetcher.fetch_batch(urls, domains, delay_range=(1, 2))

    # Merge with original data
    merged = df.merge(
        results_df[['url', 'headline', 'body_text', 'fetched_at']],
        on='url',
        how='left'
    )

    # Filter to articles with body text
    with_text = merged[merged['body_text'].notna() & (merged['body_text'].str.len() > 100)]

    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Total URLs: {len(df)}")
    print(f"Successfully fetched: {len(with_text)}")
    print(f"Success rate: {100*len(with_text)//len(df)}%")

    # Save
    output_file = "data/raw/china_daily/chinese_state_media_with_text.csv"
    with_text.to_csv(output_file, index=False)
    print(f"\nSaved to: {output_file}")

    # Summary by source
    print("\nBy source:")
    print(with_text['source_domain'].value_counts().to_string())

    return with_text


if __name__ == "__main__":
    fetch_chinese_media_text()
