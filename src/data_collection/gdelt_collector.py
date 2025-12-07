"""
GDELT Data Collector for Tibet News Analysis
Capstone Project - Dhesel Khando

GDELT (Global Database of Events, Language, and Tone) provides:
- Structured event data since 1979
- News article metadata and URLs
- Sentiment/tone analysis
- Source country identification

This is the MOST RELIABLE source for historical Chinese state media articles.

Documentation: https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from io import StringIO
import zipfile
import io


class GDELTCollector:
    """
    Collector for GDELT news data.

    GDELT provides article URLs which we can then scrape for full text.
    This is more reliable than directly scraping Chinese state media.
    """

    # GDELT 2.0 API endpoints
    DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
    GEO_API = "https://api.gdeltproject.org/api/v2/geo/geo"

    # Chinese state media domains
    CHINESE_STATE_MEDIA = [
        "chinadaily.com.cn",
        "globaltimes.cn",
        "xinhuanet.com",
        "english.news.cn",
        "news.cn",
        "cgtn.com",
        "china.org.cn",
        "ecns.cn",
        "cctv.com",
        "cri.cn"
    ]

    def __init__(self):
        """Initialize the collector."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Research Project)"
        })

    def search_articles(
        self,
        query: str = "Tibet",
        source_domain: str = None,
        source_country: str = None,
        language: str = "eng",
        start_date: str = None,
        end_date: str = None,
        max_records: int = 250,
        mode: str = "artlist"
    ) -> Optional[pd.DataFrame]:
        """
        Search GDELT for news articles.

        Args:
            query: Search term (e.g., "Tibet", "Dalai Lama")
            source_domain: Filter by domain (e.g., "globaltimes.cn")
            source_country: Filter by source country (e.g., "China")
            language: Language filter (e.g., "eng" for English)
            start_date: Start date (YYYYMMDD or YYYYMMDDHHMMSS)
            end_date: End date
            max_records: Maximum records (max 250 per request)
            mode: Output mode

        Returns:
            DataFrame with article metadata
        """
        # Build query string with filters
        full_query = query

        if language:
            full_query += f" sourcelang:{language}"

        if source_domain:
            full_query += f" domain:{source_domain}"

        if source_country:
            full_query += f" sourcecountry:{source_country}"

        params = {
            "query": full_query,
            "mode": mode,
            "maxrecords": max_records,
            "format": "json"  # Use JSON for reliability
        }

        if start_date:
            params["startdatetime"] = start_date

        if end_date:
            params["enddatetime"] = end_date

        try:
            response = self.session.get(self.DOC_API, params=params, timeout=60)
            response.raise_for_status()

            # Parse JSON response
            data = response.json()
            articles = data.get("articles", [])

            if articles:
                df = pd.DataFrame(articles)
                return df
            return pd.DataFrame()

        except Exception as e:
            print(f"  GDELT API error: {e}")
            return None

    def get_chinese_media_articles(
        self,
        query: str = "Tibet",
        start_year: int = 2008,
        end_year: int = 2024,
        domains: List[str] = None
    ) -> pd.DataFrame:
        """
        Get Tibet articles from Chinese state media sources.

        Args:
            query: Search term
            start_year: Start year
            end_year: End year
            domains: List of domains to search (default: Chinese state media)

        Returns:
            DataFrame with all articles
        """
        if domains is None:
            domains = self.CHINESE_STATE_MEDIA

        all_articles = []

        print(f"Collecting from GDELT: '{query}' in Chinese state media")
        print(f"Years: {start_year}-{end_year}")
        print(f"Domains: {', '.join(domains[:3])}...")
        print("=" * 60)

        for year in range(start_year, end_year + 1):
            print(f"\nYear {year}...")

            for domain in domains:
                print(f"  Searching {domain}...")

                # GDELT date format: YYYYMMDDHHMMSS
                start_date = f"{year}0101000000"
                end_date = f"{year}1231235959"

                df = self.search_articles(
                    query=query,
                    source_domain=domain,
                    start_date=start_date,
                    end_date=end_date,
                    max_records=250
                )

                if df is not None and not df.empty:
                    df['source_domain'] = domain
                    df['collection_year'] = year
                    all_articles.append(df)
                    print(f"    Found {len(df)} articles")
                else:
                    print(f"    No articles found")

                time.sleep(1)  # Rate limiting

            # Save checkpoint each year
            if all_articles:
                checkpoint_df = pd.concat(all_articles, ignore_index=True)
                checkpoint_df.to_csv(f"gdelt_checkpoint_{year}.csv", index=False)
                print(f"  [Checkpoint: {len(checkpoint_df)} total articles]")

        if all_articles:
            final_df = pd.concat(all_articles, ignore_index=True)
            print("\n" + "=" * 60)
            print(f"Collection complete! Total: {len(final_df)} articles")
            return final_df
        else:
            print("\nNo articles found.")
            return pd.DataFrame()

    def get_article_urls(self, df: pd.DataFrame) -> List[str]:
        """
        Extract unique article URLs from GDELT results.

        Args:
            df: GDELT results DataFrame

        Returns:
            List of unique URLs
        """
        if 'url' in df.columns:
            return df['url'].dropna().unique().tolist()
        elif 'DocumentIdentifier' in df.columns:
            return df['DocumentIdentifier'].dropna().unique().tolist()
        return []

    def get_tone_analysis(
        self,
        query: str = "Tibet",
        source_country: str = "China",
        start_date: str = None,
        end_date: str = None
    ) -> Optional[pd.DataFrame]:
        """
        Get sentiment/tone timeline from GDELT.

        This provides aggregate tone analysis without needing full text.
        Useful for comparing sentiment across sources.

        Args:
            query: Search term
            source_country: Filter by country
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with daily tone scores
        """
        params = {
            "query": query,
            "mode": "timelinetone",
            "format": "csv"
        }

        if source_country:
            params["query"] += f" sourcecountry:{source_country}"

        if start_date:
            params["startdatetime"] = start_date
        if end_date:
            params["enddatetime"] = end_date

        try:
            response = self.session.get(self.DOC_API, params=params, timeout=60)
            response.raise_for_status()
            return pd.read_csv(StringIO(response.text))
        except Exception as e:
            print(f"  Tone API error: {e}")
            return None

    def compare_source_tone(
        self,
        query: str = "Tibet",
        start_year: int = 2020,
        end_year: int = 2024
    ) -> pd.DataFrame:
        """
        Compare tone/sentiment between Chinese and Western media.

        Returns:
            DataFrame with comparative tone analysis
        """
        results = []

        start_date = f"{start_year}0101000000"
        end_date = f"{end_year}1231235959"

        sources = [
            ("China", "Chinese State Media"),
            ("United States", "Western Media"),
            ("United Kingdom", "Western Media"),
        ]

        print(f"Comparing tone for '{query}' across sources...")
        print("=" * 50)

        for country, category in sources:
            print(f"\nAnalyzing {country}...")

            df = self.get_tone_analysis(
                query=query,
                source_country=country,
                start_date=start_date,
                end_date=end_date
            )

            if df is not None and not df.empty:
                df['source_country'] = country
                df['source_category'] = category
                results.append(df)
                print(f"  Got tone data: {len(df)} data points")

            time.sleep(1)

        if results:
            return pd.concat(results, ignore_index=True)
        return pd.DataFrame()

    def save_to_csv(self, df: pd.DataFrame, filename: str):
        """Save to CSV."""
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\nSaved to: {filename}")
        print(f"Total rows: {len(df)}")


def test_gdelt():
    """Test GDELT API."""
    print("=" * 60)
    print("GDELT COLLECTOR - TEST MODE")
    print("=" * 60)

    collector = GDELTCollector()

    print("\n--- Testing Article Search ---")
    df = collector.search_articles(
        query="Tibet",
        source_domain="globaltimes.cn",
        start_date="20230101000000",
        end_date="20231231235959",
        max_records=10
    )

    if df is not None and not df.empty:
        print(f"Found {len(df)} articles")
        print(f"Columns: {list(df.columns)[:5]}...")

        if 'url' in df.columns or 'DocumentIdentifier' in df.columns:
            urls = collector.get_article_urls(df)
            print(f"Sample URL: {urls[0][:60]}..." if urls else "No URLs")
        return True
    else:
        print("No results from GDELT")
        return False


def main():
    """Main function."""
    success = test_gdelt()

    if success:
        print("\n" + "=" * 60)
        print("GDELT test successful!")
        print("=" * 60)
        print("\nTo collect full dataset, run:")
        print("  collector = GDELTCollector()")
        print("  df = collector.get_chinese_media_articles()")
        print("  collector.save_to_csv(df, 'gdelt_chinese_media.csv')")
    else:
        print("\n" + "=" * 60)
        print("GDELT may be temporarily unavailable.")
        print("Try again later or check: https://blog.gdeltproject.org/")
        print("=" * 60)


if __name__ == "__main__":
    main()
