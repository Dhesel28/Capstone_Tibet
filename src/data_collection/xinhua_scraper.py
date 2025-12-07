"""
Xinhua News Agency Scraper for Tibet News Analysis
Capstone Project - Dhesel Khando

Xinhua is China's official state news agency.
This script collects Tibet-related articles from Xinhua English.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime
from typing import Optional, List, Dict
from urllib.parse import urljoin
import random


class XinhuaScraper:
    """Scraper for Xinhua News Agency articles."""

    SEARCH_URL = "http://search.news.cn/language/search.jspa"
    BASE_URL = "http://english.news.cn"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    def __init__(self):
        """Initialize the scraper."""
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.collected_articles = []

    def search_articles(
        self,
        query: str = "Tibet",
        page: int = 1,
        sort: int = 0  # 0 = relevance, 1 = date
    ) -> Optional[Dict]:
        """
        Search for articles using Xinhua search.

        Args:
            query: Search term
            page: Page number (1-indexed)
            sort: Sort order (0=relevance, 1=date)

        Returns:
            Dictionary with search results or None
        """
        params = {
            "q": query,
            "ss": sort,
            "t": "0",  # All time
            "n": "10",  # Results per page
            "np": page,
            "lang": "en"
        }

        try:
            response = self.session.get(
                self.SEARCH_URL,
                params=params,
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()
            return self._parse_search_results(response.text)
        except requests.exceptions.RequestException as e:
            print(f"  Error searching: {e}")
            return None

    def _parse_search_results(self, html: str) -> Dict:
        """Parse search results from HTML."""
        soup = BeautifulSoup(html, 'html.parser')

        results = {
            "articles": [],
            "total": 0,
            "has_more": False
        }

        # Find article links - Xinhua uses various structures
        article_links = soup.find_all('a', href=re.compile(r'english\.news\.cn.*\.htm'))

        seen_urls = set()
        for link in article_links:
            href = link.get('href', '')
            if href and href not in seen_urls and 'tibet' in href.lower() or link.get_text():
                seen_urls.add(href)

                title = link.get_text(strip=True)
                if title and len(title) > 10:
                    full_url = href if href.startswith('http') else urljoin(self.BASE_URL, href)
                    results["articles"].append({
                        "url": full_url,
                        "title": title
                    })

        results["has_more"] = len(results["articles"]) > 0
        return results

    def fetch_article(self, url: str) -> Optional[Dict]:
        """
        Fetch and parse a single article.

        Args:
            url: Article URL

        Returns:
            Article dictionary or None
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return self._parse_article(response.text, url)
        except requests.exceptions.RequestException as e:
            print(f"    Error fetching {url}: {e}")
            return None

    def _parse_article(self, html: str, url: str) -> Optional[Dict]:
        """Parse article content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')

        try:
            # Title
            title_tag = soup.find('div', class_='head-line') or \
                       soup.find('h1', class_='title') or \
                       soup.find('h1') or \
                       soup.find('title')
            headline = title_tag.get_text(strip=True) if title_tag else ""
            headline = headline.replace(" - Xinhua | English.news.cn", "").strip()

            # Publication date
            date_str = ""

            # Try meta tag
            meta_date = soup.find('meta', {'name': 'publishdate'}) or \
                       soup.find('meta', {'property': 'article:published_time'})
            if meta_date:
                date_str = meta_date.get('content', '')

            # Try date span/div
            if not date_str:
                date_div = soup.find('span', class_=re.compile(r'time|date')) or \
                          soup.find('div', class_=re.compile(r'time|date'))
                if date_div:
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_div.get_text())
                    if date_match:
                        date_str = date_match.group(1)

            # Try URL pattern
            if not date_str:
                url_match = re.search(r'/(\d{4})-(\d{2})/(\d{2})/', url) or \
                           re.search(r'/(\d{4})(\d{2})(\d{2})/', url)
                if url_match:
                    date_str = f"{url_match.group(1)}-{url_match.group(2)}-{url_match.group(3)}"

            # Body text
            body_text = ""

            article_div = soup.find('div', id='detail') or \
                         soup.find('div', class_='article') or \
                         soup.find('div', class_='content') or \
                         soup.find('article')

            if article_div:
                paragraphs = article_div.find_all('p')
                body_text = '\n\n'.join(
                    p.get_text(strip=True) for p in paragraphs
                    if p.get_text(strip=True) and len(p.get_text(strip=True)) > 20
                )

            if not body_text:
                paragraphs = soup.find_all('p')
                body_text = '\n\n'.join(
                    p.get_text(strip=True) for p in paragraphs
                    if len(p.get_text(strip=True)) > 50
                )

            # Author/Source
            author = "Xinhua"
            source_tag = soup.find('span', class_='source') or \
                        soup.find('div', class_='source')
            if source_tag:
                author = source_tag.get_text(strip=True)

            if not headline or not body_text or len(body_text) < 100:
                return None

            return {
                "article_id": url.split('/')[-1].replace('.htm', ''),
                "headline": headline,
                "body_text": body_text,
                "publication_date": date_str,
                "source": "Xinhua",
                "source_category": "Chinese State Media",
                "section": "Tibet",
                "url": url,
                "author": author,
                "collected_at": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"    Error parsing article: {e}")
            return None

    def collect_articles(
        self,
        query: str = "Tibet",
        max_articles: int = 500,
        delay_range: tuple = (2, 5)
    ) -> pd.DataFrame:
        """
        Collect articles from search results.

        Args:
            query: Search term
            max_articles: Maximum articles to collect
            delay_range: Random delay range between requests (min, max)

        Returns:
            DataFrame with collected articles
        """
        all_articles = []
        page = 1
        max_pages = 100

        print(f"Starting Xinhua collection for '{query}'...")
        print(f"Target: up to {max_articles} articles")
        print("=" * 50)

        while len(all_articles) < max_articles and page <= max_pages:
            print(f"\nPage {page}...")

            results = self.search_articles(query=query, page=page)

            if not results or not results["articles"]:
                print(f"  No more results")
                break

            for article_info in results["articles"]:
                if len(all_articles) >= max_articles:
                    break

                print(f"  Fetching: {article_info['title'][:50]}...")
                article = self.fetch_article(article_info["url"])

                if article:
                    all_articles.append(article)
                    print(f"    ✓ Collected ({article['publication_date'][:10] if article['publication_date'] else 'no date'})")

                time.sleep(random.uniform(*delay_range))

            page += 1

            # Checkpoint every 50 articles
            if len(all_articles) % 50 == 0 and all_articles:
                self._save_checkpoint(all_articles)

        print("\n" + "=" * 50)
        print(f"Collection complete! Total: {len(all_articles)} articles")

        return pd.DataFrame(all_articles)

    def _save_checkpoint(self, articles: list):
        """Save checkpoint."""
        df = pd.DataFrame(articles)
        checkpoint_path = "xinhua_checkpoint.csv"
        df.to_csv(checkpoint_path, index=False)
        print(f"\n  [Checkpoint: {len(articles)} articles saved]")

    def save_to_csv(self, df: pd.DataFrame, filename: str = "xinhua_tibet_articles.csv"):
        """Save to CSV."""
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\nSaved to: {filename}")
        print(f"Total rows: {len(df)}")


def test_scraper():
    """Test the Xinhua scraper."""
    print("=" * 60)
    print("XINHUA SCRAPER - TEST MODE")
    print("=" * 60)

    scraper = XinhuaScraper()

    print("\n--- Testing Search ---")
    results = scraper.search_articles(query="Tibet", page=1)

    if results and results["articles"]:
        print(f"Found {len(results['articles'])} article links")

        print("\n--- Testing Article Fetch ---")
        first_url = results["articles"][0]["url"]
        print(f"Fetching: {first_url}")

        article = scraper.fetch_article(first_url)
        if article:
            print(f"  Title: {article['headline'][:60]}...")
            print(f"  Date: {article['publication_date']}")
            print(f"  Body: {len(article['body_text'])} chars")
            return True
        else:
            print("  Failed to parse article")
    else:
        print("No results or search blocked")

    return False


def main():
    """Main function."""
    success = test_scraper()

    if success:
        print("\n" + "=" * 60)
        print("Test successful! Ready to collect.")
        print("=" * 60)

        # Uncomment to run full collection:
        # scraper = XinhuaScraper()
        # df = scraper.collect_articles(query="Tibet", max_articles=500)
        # scraper.save_to_csv(df, "data/raw/xinhua/xinhua_tibet_articles.csv")
    else:
        print("\n" + "=" * 60)
        print("Xinhua may be blocking requests.")
        print("Consider using GDELT or proxy services.")
        print("=" * 60)


if __name__ == "__main__":
    main()
