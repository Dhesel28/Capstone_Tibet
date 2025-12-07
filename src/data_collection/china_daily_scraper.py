"""
China Daily Scraper for Tibet News Analysis
Capstone Project - Dhesel Khando

This script scrapes news articles containing "Tibet" from China Daily
for the period 2008-2024.

China Daily is Chinese state media - important for comparative analysis.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json
from datetime import datetime
from typing import Optional, List, Dict
from urllib.parse import urljoin, quote
import random

class ChinaDailyScraper:
    """Scraper for China Daily news articles."""

    SEARCH_URL = "https://newssearch.chinadaily.com.cn/en/search"
    BASE_URL = "https://www.chinadaily.com.cn"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
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
        page: int = 0,
        sort: str = "dp"  # dp = date descending, da = date ascending, rel = relevance
    ) -> Optional[Dict]:
        """
        Search for articles using China Daily search.

        Args:
            query: Search term
            page: Page number (0-indexed)
            sort: Sort order (dp=newest, da=oldest, rel=relevance)

        Returns:
            Dictionary with search results or None
        """
        params = {
            "query": query,
            "page": page,
            "sort": sort,
            "type": "article"  # Only articles, not blogs/comments
        }

        try:
            response = self.session.get(self.SEARCH_URL, params=params, timeout=30)
            response.raise_for_status()
            return self._parse_search_results(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error searching: {e}")
            return None

    def _parse_search_results(self, html: str) -> Dict:
        """Parse search results from HTML."""
        soup = BeautifulSoup(html, 'html.parser')

        results = {
            "articles": [],
            "total": 0,
            "has_more": False
        }

        # Try to find result items
        # China Daily uses JavaScript to render results, so we need to find the data

        # Look for article links in the page
        article_links = soup.find_all('a', href=re.compile(r'/a/\d+/\d+/'))

        seen_urls = set()
        for link in article_links:
            href = link.get('href', '')
            if href and href not in seen_urls:
                seen_urls.add(href)

                # Extract basic info
                title = link.get_text(strip=True)
                if title and len(title) > 10:  # Filter out navigation links
                    results["articles"].append({
                        "url": urljoin(self.BASE_URL, href),
                        "title": title
                    })

        results["has_more"] = len(results["articles"]) > 0
        return results

    def search_by_year(
        self,
        query: str = "Tibet",
        year: int = 2020,
        target_count: int = 100
    ) -> List[Dict]:
        """
        Search for articles from a specific year.

        Note: China Daily search doesn't have date filtering in URL,
        so we'll collect articles and filter by date from article pages.
        """
        print(f"\nSearching China Daily for '{query}' articles from {year}...")

        articles = []
        page = 0
        max_pages = 50  # Safety limit

        while len(articles) < target_count and page < max_pages:
            print(f"  Fetching page {page + 1}...")

            results = self.search_articles(query=query, page=page)

            if not results or not results["articles"]:
                print(f"  No more results at page {page + 1}")
                break

            for article_info in results["articles"]:
                if len(articles) >= target_count:
                    break

                # Fetch full article to get date and content
                article = self.fetch_article(article_info["url"])

                if article:
                    # Check if article is from target year
                    pub_date = article.get("publication_date", "")
                    if pub_date and str(year) in pub_date[:4]:
                        articles.append(article)
                        print(f"    Found: {article['headline'][:50]}... ({pub_date[:10]})")

                time.sleep(random.uniform(1, 2))  # Be respectful

            page += 1
            time.sleep(random.uniform(2, 4))

        print(f"  Year {year}: Collected {len(articles)} articles")
        return articles

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
            title_tag = soup.find('h1') or soup.find('title')
            headline = title_tag.get_text(strip=True) if title_tag else ""

            # Clean up title
            headline = headline.replace(" - Chinadaily.com.cn", "").strip()
            headline = headline.replace(" - China Daily", "").strip()

            # Publication date - look for common patterns
            date_str = ""

            # Try meta tag
            meta_date = soup.find('meta', {'name': 'publishdate'})
            if meta_date:
                date_str = meta_date.get('content', '')

            # Try info div
            if not date_str:
                info_div = soup.find('div', class_=re.compile(r'info|date|time|meta'))
                if info_div:
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', info_div.get_text())
                    if date_match:
                        date_str = date_match.group(1)

            # Try URL pattern (e.g., /a/202312/15/...)
            if not date_str:
                url_match = re.search(r'/a/(\d{4})(\d{2})/(\d{2})/', url)
                if url_match:
                    date_str = f"{url_match.group(1)}-{url_match.group(2)}-{url_match.group(3)}"

            # Body text
            body_text = ""

            # Try article div
            article_div = soup.find('div', id='Content') or \
                         soup.find('div', class_='article') or \
                         soup.find('article') or \
                         soup.find('div', class_=re.compile(r'content|text|body'))

            if article_div:
                # Get all paragraphs
                paragraphs = article_div.find_all('p')
                body_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

            # Fallback: get all paragraphs from page
            if not body_text:
                paragraphs = soup.find_all('p')
                body_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50)

            # Author
            author = ""
            author_tag = soup.find('span', class_=re.compile(r'author|byline')) or \
                        soup.find('div', class_=re.compile(r'author|byline'))
            if author_tag:
                author = author_tag.get_text(strip=True)

            # Try to find "By ..." pattern
            if not author:
                by_match = re.search(r'By\s+([A-Za-z\s]+)', html[:2000])
                if by_match:
                    author = by_match.group(1).strip()

            # Section/Category
            section = ""
            breadcrumb = soup.find('div', class_=re.compile(r'bread|nav|path'))
            if breadcrumb:
                links = breadcrumb.find_all('a')
                if len(links) >= 2:
                    section = links[-1].get_text(strip=True)

            if not headline or not body_text or len(body_text) < 100:
                return None

            return {
                "article_id": url.split('/')[-1].replace('.html', ''),
                "headline": headline,
                "body_text": body_text,
                "publication_date": date_str,
                "source": "China Daily",
                "source_category": "Chinese State Media",
                "section": section,
                "url": url,
                "author": author,
                "collected_at": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"    Error parsing article: {e}")
            return None

    def collect_all_years(
        self,
        start_year: int = 2008,
        end_year: int = 2024,
        query: str = "Tibet",
        target_per_year: int = 100
    ) -> pd.DataFrame:
        """
        Collect articles across all years.

        Note: This is a simplified approach. China Daily's search
        doesn't easily filter by year, so we collect recent articles
        and use alternative methods for historical data.
        """
        all_articles = []

        print(f"Starting China Daily collection: {start_year}-{end_year}")
        print(f"Target: {target_per_year} articles per year")
        print("=" * 50)

        # Collect from search (mostly recent articles)
        for year in range(end_year, start_year - 1, -1):  # Start from recent
            year_articles = self.search_by_year(
                query=query,
                year=year,
                target_count=target_per_year
            )
            all_articles.extend(year_articles)

            # Save checkpoint
            if len(all_articles) > 0 and len(all_articles) % 200 == 0:
                self._save_checkpoint(all_articles)

        print("\n" + "=" * 50)
        print(f"Collection complete! Total articles: {len(all_articles)}")

        return pd.DataFrame(all_articles)

    def _save_checkpoint(self, articles: list):
        """Save intermediate checkpoint."""
        df = pd.DataFrame(articles)
        checkpoint_path = "china_daily_checkpoint.csv"
        df.to_csv(checkpoint_path, index=False)
        print(f"\n  [Checkpoint saved: {checkpoint_path}]")

    def save_to_csv(self, df: pd.DataFrame, filename: str = "china_daily_tibet_articles.csv"):
        """Save collected articles to CSV."""
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\nData saved to: {filename}")
        print(f"Total rows: {len(df)}")


def test_scraper():
    """Test the scraper with a few articles."""
    print("=" * 60)
    print("CHINA DAILY SCRAPER - TEST MODE")
    print("=" * 60)

    scraper = ChinaDailyScraper()

    # Test search
    print("\n--- Testing Search ---")
    results = scraper.search_articles(query="Tibet", page=0)

    if results and results["articles"]:
        print(f"Found {len(results['articles'])} article links")

        # Test fetching first article
        print("\n--- Testing Article Fetch ---")
        if results["articles"]:
            first_url = results["articles"][0]["url"]
            print(f"Fetching: {first_url}")

            article = scraper.fetch_article(first_url)
            if article:
                print(f"  Title: {article['headline'][:60]}...")
                print(f"  Date: {article['publication_date']}")
                print(f"  Body length: {len(article['body_text'])} chars")
                print(f"  Source: {article['source']}")
            else:
                print("  Failed to parse article")
    else:
        print("No results found or search failed")
        print("\nNote: China Daily may block automated requests.")
        print("Consider using alternative methods for data collection.")


def main():
    """Main function to run the scraper."""

    # First run a test
    test_scraper()

    print("\n" + "=" * 60)
    print("NOTE: China Daily web scraping may be limited.")
    print("For comprehensive historical data, consider:")
    print("1. GDELT database for article links")
    print("2. Academic database access (LexisNexis)")
    print("3. Archive.org Wayback Machine")
    print("=" * 60)

    # Uncomment below to run full collection
    # scraper = ChinaDailyScraper()
    # df = scraper.collect_all_years(
    #     start_year=2008,
    #     end_year=2024,
    #     query="Tibet",
    #     target_per_year=100
    # )
    # scraper.save_to_csv(df)


if __name__ == "__main__":
    main()
