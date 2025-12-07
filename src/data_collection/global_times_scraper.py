"""
Global Times Scraper for Tibet News Analysis
Capstone Project - Dhesel Khando

Global Times is a Chinese state-affiliated newspaper known for
nationalistic commentary. Important for understanding Chinese state perspective.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime
from typing import Optional, List, Dict
from urllib.parse import urljoin, urlencode
import random


class GlobalTimesScraper:
    """Scraper for Global Times articles."""

    SEARCH_URL = "https://search.globaltimes.cn/QuickSearchCtrl"
    BASE_URL = "https://www.globaltimes.cn"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.globaltimes.cn/",
        "X-Requested-With": "XMLHttpRequest",
    }

    def __init__(self):
        """Initialize the scraper."""
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def search_articles(
        self,
        query: str = "Tibet",
        page: int = 1,
        page_size: int = 20
    ) -> Optional[Dict]:
        """
        Search for articles.

        Args:
            query: Search term
            page: Page number
            page_size: Results per page

        Returns:
            Search results dictionary
        """
        params = {
            "query": query,
            "page_no": page,
            "page_size": page_size,
            "type": "article"
        }

        try:
            response = self.session.get(
                self.SEARCH_URL,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            # Try JSON response first
            try:
                data = response.json()
                return self._parse_json_results(data)
            except:
                # Fall back to HTML parsing
                return self._parse_html_results(response.text)

        except requests.exceptions.RequestException as e:
            print(f"  Search error: {e}")
            return None

    def _parse_json_results(self, data: dict) -> Dict:
        """Parse JSON search results."""
        results = {"articles": [], "total": 0, "has_more": False}

        if isinstance(data, dict):
            items = data.get("data", []) or data.get("results", []) or []
            results["total"] = data.get("total", len(items))

            for item in items:
                if isinstance(item, dict):
                    url = item.get("url", "") or item.get("link", "")
                    title = item.get("title", "") or item.get("headline", "")

                    if url and title:
                        if not url.startswith("http"):
                            url = urljoin(self.BASE_URL, url)
                        results["articles"].append({"url": url, "title": title})

        results["has_more"] = len(results["articles"]) > 0
        return results

    def _parse_html_results(self, html: str) -> Dict:
        """Parse HTML search results."""
        soup = BeautifulSoup(html, 'html.parser')
        results = {"articles": [], "total": 0, "has_more": False}

        # Find article links
        links = soup.find_all('a', href=re.compile(r'globaltimes\.cn.*\d+\.shtml'))

        seen = set()
        for link in links:
            href = link.get('href', '')
            title = link.get_text(strip=True)

            if href not in seen and title and len(title) > 15:
                seen.add(href)
                url = href if href.startswith('http') else urljoin(self.BASE_URL, href)
                results["articles"].append({"url": url, "title": title})

        results["has_more"] = len(results["articles"]) > 0
        return results

    def search_by_google(self, query: str = "Tibet site:globaltimes.cn") -> List[str]:
        """
        Alternative: Get URLs via site-specific Google search.
        This is a fallback if direct search is blocked.

        Note: For production, use Google Custom Search API.
        """
        # This is a placeholder - in production you'd use:
        # 1. Google Custom Search API
        # 2. SerpAPI
        # 3. Manual collection from Google
        print("  Note: Google site search requires API key")
        return []

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
            print(f"    Error fetching: {e}")
            return None

    def _parse_article(self, html: str, url: str) -> Optional[Dict]:
        """Parse article content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')

        try:
            # Title
            title_tag = soup.find('h3', class_='article-title') or \
                       soup.find('h1', class_='article-title') or \
                       soup.find('div', class_='article-title') or \
                       soup.find('h1') or \
                       soup.find('title')

            headline = ""
            if title_tag:
                headline = title_tag.get_text(strip=True)
                headline = headline.replace(" - Global Times", "").strip()

            # Publication date
            date_str = ""

            # Try pub_time span
            pub_time = soup.find('span', class_='pub_time') or \
                      soup.find('span', class_='time') or \
                      soup.find('div', class_='pub_time')
            if pub_time:
                date_text = pub_time.get_text(strip=True)
                date_match = re.search(r'(\w+ \d+, \d{4})', date_text) or \
                            re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                if date_match:
                    date_str = date_match.group(1)

            # Try meta tag
            if not date_str:
                meta = soup.find('meta', {'property': 'article:published_time'}) or \
                      soup.find('meta', {'name': 'publishdate'})
                if meta:
                    date_str = meta.get('content', '')[:10]

            # Try URL pattern
            if not date_str:
                url_match = re.search(r'/(\d{4})/(\d{2})(\d{2})/', url)
                if url_match:
                    date_str = f"{url_match.group(1)}-{url_match.group(2)}-{url_match.group(3)}"

            # Body text
            body_text = ""

            article_div = soup.find('div', class_='article-content') or \
                         soup.find('div', class_='article_content') or \
                         soup.find('div', class_='article_right') or \
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

            # Author
            author = "Global Times"
            author_tag = soup.find('span', class_='author') or \
                        soup.find('div', class_='author')
            if author_tag:
                author_text = author_tag.get_text(strip=True)
                if author_text:
                    author = author_text

            # Section
            section = ""
            breadcrumb = soup.find('div', class_='breadcrumb') or \
                        soup.find('div', class_='nav-path')
            if breadcrumb:
                links = breadcrumb.find_all('a')
                if len(links) >= 2:
                    section = links[-1].get_text(strip=True)

            if not headline or not body_text or len(body_text) < 100:
                return None

            return {
                "article_id": url.split('/')[-1].replace('.shtml', ''),
                "headline": headline,
                "body_text": body_text,
                "publication_date": date_str,
                "source": "Global Times",
                "source_category": "Chinese State Media",
                "section": section or "China",
                "url": url,
                "author": author,
                "collected_at": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"    Parse error: {e}")
            return None

    def collect_articles(
        self,
        query: str = "Tibet",
        max_articles: int = 500,
        delay_range: tuple = (2, 5)
    ) -> pd.DataFrame:
        """
        Collect articles from Global Times.

        Args:
            query: Search term
            max_articles: Maximum articles to collect
            delay_range: Random delay between requests

        Returns:
            DataFrame with articles
        """
        all_articles = []
        page = 1
        max_pages = 50

        print(f"Starting Global Times collection for '{query}'...")
        print(f"Target: up to {max_articles} articles")
        print("=" * 50)

        while len(all_articles) < max_articles and page <= max_pages:
            print(f"\nPage {page}...")

            results = self.search_articles(query=query, page=page)

            if not results or not results["articles"]:
                print("  No more results")
                break

            for info in results["articles"]:
                if len(all_articles) >= max_articles:
                    break

                print(f"  Fetching: {info['title'][:45]}...")
                article = self.fetch_article(info["url"])

                if article:
                    all_articles.append(article)
                    print(f"    ✓ Collected")

                time.sleep(random.uniform(*delay_range))

            page += 1

            if len(all_articles) % 50 == 0 and all_articles:
                self._save_checkpoint(all_articles)

        print("\n" + "=" * 50)
        print(f"Collection complete! Total: {len(all_articles)} articles")

        return pd.DataFrame(all_articles)

    def _save_checkpoint(self, articles: list):
        """Save checkpoint."""
        df = pd.DataFrame(articles)
        df.to_csv("global_times_checkpoint.csv", index=False)
        print(f"\n  [Checkpoint: {len(articles)} articles]")

    def save_to_csv(self, df: pd.DataFrame, filename: str = "global_times_tibet_articles.csv"):
        """Save to CSV."""
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\nSaved to: {filename}")
        print(f"Total: {len(df)} articles")


def test_scraper():
    """Test the Global Times scraper."""
    print("=" * 60)
    print("GLOBAL TIMES SCRAPER - TEST MODE")
    print("=" * 60)

    scraper = GlobalTimesScraper()

    print("\n--- Testing Search ---")
    results = scraper.search_articles(query="Tibet", page=1)

    if results and results["articles"]:
        print(f"Found {len(results['articles'])} articles")

        print("\n--- Testing Article Fetch ---")
        first = results["articles"][0]
        print(f"Fetching: {first['url']}")

        article = scraper.fetch_article(first["url"])
        if article:
            print(f"  Title: {article['headline'][:50]}...")
            print(f"  Date: {article['publication_date']}")
            print(f"  Body: {len(article['body_text'])} chars")
            return True
        else:
            print("  Failed to parse")
    else:
        print("No results or blocked")

    return False


def main():
    """Main function."""
    success = test_scraper()

    if success:
        print("\n" + "=" * 60)
        print("Test successful! Ready for collection.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Global Times may be blocking requests.")
        print("Alternative: Use GDELT or manual collection.")
        print("=" * 60)


if __name__ == "__main__":
    main()
