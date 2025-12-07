"""
Guardian API Data Collector for Tibet News Analysis
Capstone Project - Dhesel Khando
Advisor: Professor Scott Crossley

This script collects news articles containing "Tibet" from The Guardian API
for the period 2008-2024 (100 articles per year target).

Guardian API Documentation: https://open-platform.theguardian.com/documentation/
"""

import requests
import pandas as pd
import time
import os
from datetime import datetime
from typing import Optional

class GuardianAPICollector:
    """Collector for Guardian API news articles."""

    BASE_URL = "https://content.guardianapis.com/search"

    def __init__(self, api_key: str):
        """
        Initialize the collector with API key.

        Args:
            api_key: Guardian API key (get free key at https://bonobo.capi.gutools.co.uk/register/developer)
        """
        self.api_key = api_key
        self.collected_articles = []

    def search_articles(
        self,
        query: str = "Tibet",
        from_date: str = None,
        to_date: str = None,
        page: int = 1,
        page_size: int = 50,
        order_by: str = "relevance"
    ) -> dict:
        """
        Search for articles using the Guardian API.

        Args:
            query: Search term (default: "Tibet")
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            page: Page number for pagination
            page_size: Number of results per page (max 200)
            order_by: Sort order - "relevance", "newest", or "oldest"

        Returns:
            API response as dictionary
        """
        params = {
            "api-key": self.api_key,
            "q": query,
            "page": page,
            "page-size": page_size,
            "order-by": order_by,
            "show-fields": "headline,body,bodyText,byline,publication,shortUrl,trailText",
            "show-tags": "keyword,contributor",
            "format": "json"
        }

        if from_date:
            params["from-date"] = from_date
        if to_date:
            params["to-date"] = to_date

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def collect_year_articles(
        self,
        year: int,
        query: str = "Tibet",
        target_count: int = 100
    ) -> list:
        """
        Collect articles for a specific year.

        Args:
            year: Year to collect articles from
            query: Search term
            target_count: Target number of articles to collect

        Returns:
            List of article dictionaries
        """
        from_date = f"{year}-01-01"
        to_date = f"{year}-12-31"

        articles = []
        page = 1

        print(f"\nCollecting articles for {year}...")

        while len(articles) < target_count:
            response = self.search_articles(
                query=query,
                from_date=from_date,
                to_date=to_date,
                page=page,
                page_size=50,
                order_by="relevance"
            )

            if not response or "response" not in response:
                print(f"  Error: No response for page {page}")
                break

            results = response["response"].get("results", [])

            if not results:
                print(f"  No more results after page {page}")
                break

            for item in results:
                if len(articles) >= target_count:
                    break

                article = self._parse_article(item, year)
                if article:
                    articles.append(article)

            total_pages = response["response"].get("pages", 0)
            print(f"  Page {page}/{total_pages}: Collected {len(articles)} articles")

            if page >= total_pages:
                break

            page += 1
            time.sleep(0.5)  # Rate limiting - be respectful to the API

        print(f"  Year {year}: Collected {len(articles)} articles total")
        return articles

    def _parse_article(self, item: dict, year: int) -> Optional[dict]:
        """
        Parse a single article from API response.

        Args:
            item: Raw article data from API
            year: Collection year

        Returns:
            Parsed article dictionary or None
        """
        try:
            fields = item.get("fields", {})
            tags = item.get("tags", [])

            # Extract author from tags or byline
            author = fields.get("byline", "")
            if not author:
                contributors = [t["webTitle"] for t in tags if t.get("type") == "contributor"]
                author = ", ".join(contributors) if contributors else "Unknown"

            # Extract keywords
            keywords = [t["webTitle"] for t in tags if t.get("type") == "keyword"]

            article = {
                "article_id": item.get("id", ""),
                "headline": fields.get("headline", item.get("webTitle", "")),
                "body_text": fields.get("bodyText", ""),  # Plain text version
                "body_html": fields.get("body", ""),      # HTML version (for backup)
                "trail_text": fields.get("trailText", ""),  # Summary/lead
                "publication_date": item.get("webPublicationDate", ""),
                "source": "The Guardian",
                "source_category": "Western Media",
                "section": item.get("sectionName", ""),
                "section_id": item.get("sectionId", ""),
                "url": item.get("webUrl", ""),
                "short_url": fields.get("shortUrl", ""),
                "author": author,
                "keywords": "|".join(keywords),  # Pipe-separated for CSV
                "publication": fields.get("publication", "The Guardian"),
                "type": item.get("type", ""),
                "collection_year": year,
                "collected_at": datetime.now().isoformat()
            }

            # Only include articles with actual body text
            if article["body_text"] and len(article["body_text"]) > 100:
                return article
            return None

        except Exception as e:
            print(f"  Error parsing article: {e}")
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

        Args:
            start_year: First year to collect
            end_year: Last year to collect
            query: Search term
            target_per_year: Target articles per year

        Returns:
            DataFrame with all collected articles
        """
        all_articles = []

        print(f"Starting collection: {start_year}-{end_year}")
        print(f"Target: {target_per_year} articles per year")
        print(f"Search term: '{query}'")
        print("=" * 50)

        for year in range(start_year, end_year + 1):
            year_articles = self.collect_year_articles(
                year=year,
                query=query,
                target_count=target_per_year
            )
            all_articles.extend(year_articles)

            # Save intermediate results every 3 years
            if (year - start_year + 1) % 3 == 0:
                self._save_checkpoint(all_articles, year)

        print("\n" + "=" * 50)
        print(f"Collection complete! Total articles: {len(all_articles)}")

        return pd.DataFrame(all_articles)

    def _save_checkpoint(self, articles: list, year: int):
        """Save intermediate checkpoint during collection."""
        df = pd.DataFrame(articles)
        checkpoint_path = f"guardian_checkpoint_through_{year}.csv"
        df.to_csv(checkpoint_path, index=False)
        print(f"\n  [Checkpoint saved: {checkpoint_path}]")

    def save_to_csv(self, df: pd.DataFrame, filename: str = "guardian_tibet_articles.csv"):
        """
        Save collected articles to CSV.

        Args:
            df: DataFrame with articles
            filename: Output filename
        """
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\nData saved to: {filename}")
        print(f"Total rows: {len(df)}")

        # Print summary statistics
        if not df.empty:
            print("\n--- Collection Summary ---")
            print(f"Date range: {df['publication_date'].min()} to {df['publication_date'].max()}")
            print(f"\nArticles per year:")
            year_counts = df['collection_year'].value_counts().sort_index()
            for year, count in year_counts.items():
                print(f"  {year}: {count}")


def main():
    """Main function to run the data collection."""

    # ========================================
    # IMPORTANT: Get your free API key at:
    # https://bonobo.capi.gutools.co.uk/register/developer
    # ========================================

    API_KEY = os.environ.get("GUARDIAN_API_KEY", "test")  # Use 'test' for limited testing

    if API_KEY == "test":
        print("=" * 60)
        print("NOTE: Using 'test' API key (limited to 1 request/second)")
        print("For production use, get a free key at:")
        print("https://bonobo.capi.gutools.co.uk/register/developer")
        print("=" * 60)

    # Initialize collector
    collector = GuardianAPICollector(api_key=API_KEY)

    # Test with a small sample first
    print("\n--- Testing API Connection ---")
    test_response = collector.search_articles(
        query="Tibet",
        from_date="2020-01-01",
        to_date="2020-12-31",
        page_size=5
    )

    if test_response and "response" in test_response:
        total = test_response["response"].get("total", 0)
        print(f"API test successful! Found {total} articles for 'Tibet' in 2020")

        # Show sample article
        results = test_response["response"].get("results", [])
        if results:
            print(f"\nSample article: {results[0].get('webTitle', 'N/A')}")
    else:
        print("API test failed. Please check your API key.")
        return

    # Collect full dataset
    print("\n--- Starting Full Collection ---")
    df = collector.collect_all_years(
        start_year=2008,
        end_year=2024,
        query="Tibet",
        target_per_year=100
    )

    # Save results
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "guardian_tibet_articles.csv")
    collector.save_to_csv(df, output_path)

    return df


if __name__ == "__main__":
    df = main()
