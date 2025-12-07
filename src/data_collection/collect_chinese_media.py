"""
Full Collection Script for Chinese State Media Articles on Tibet
Capstone Project - Dhesel Khando

This script collects Tibet-related articles from Chinese state media
using GDELT API for the period 2008-2024.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_collection.gdelt_collector import GDELTCollector
import pandas as pd
import time
from datetime import datetime


def collect_full_dataset():
    """Collect full Chinese state media dataset."""

    collector = GDELTCollector()

    # Chinese state media domains
    domains = [
        "globaltimes.cn",
        "chinadaily.com.cn",
        "news.cn",
        "xinhuanet.com",
        "ecns.cn",
        "cgtn.com",
        "china.org.cn",
        "cri.cn"
    ]

    # Years to collect
    start_year = 2008
    end_year = 2024

    all_articles = []

    print("=" * 70)
    print("CHINESE STATE MEDIA COLLECTION - Tibet Articles")
    print(f"Period: {start_year}-{end_year}")
    print(f"Sources: {len(domains)} domains")
    print("=" * 70)

    for year in range(start_year, end_year + 1):
        print(f"\n{'='*70}")
        print(f"YEAR {year}")
        print("=" * 70)

        year_articles = []

        # GDELT date format
        start_date = f"{year}0101000000"
        end_date = f"{year}1231235959"

        for domain in domains:
            print(f"\n  {domain}...")

            try:
                df = collector.search_articles(
                    query="Tibet",
                    source_domain=domain,
                    start_date=start_date,
                    end_date=end_date,
                    max_records=250  # Max per request
                )

                if df is not None and not df.empty:
                    df['source_domain'] = domain
                    df['source_category'] = 'Chinese State Media'
                    df['collection_year'] = year
                    year_articles.append(df)
                    print(f"    Found {len(df)} articles")
                else:
                    print(f"    No articles")

            except Exception as e:
                print(f"    Error: {e}")

            time.sleep(1)  # Rate limiting

        # Combine year's articles
        if year_articles:
            year_df = pd.concat(year_articles, ignore_index=True)
            all_articles.append(year_df)
            print(f"\n  Year {year} total: {len(year_df)} articles")

            # Save checkpoint
            checkpoint_df = pd.concat(all_articles, ignore_index=True)
            checkpoint_path = f"data/raw/china_daily/checkpoint_{year}.csv"
            checkpoint_df.to_csv(checkpoint_path, index=False)
            print(f"  [Checkpoint saved: {len(checkpoint_df)} total articles]")

    # Final save
    if all_articles:
        final_df = pd.concat(all_articles, ignore_index=True)

        # Remove duplicates based on URL
        original_len = len(final_df)
        final_df = final_df.drop_duplicates(subset=['url'], keep='first')

        print("\n" + "=" * 70)
        print("COLLECTION COMPLETE")
        print("=" * 70)
        print(f"Total articles: {len(final_df)}")
        print(f"Duplicates removed: {original_len - len(final_df)}")

        # Summary by source
        print("\nBy source:")
        print(final_df['source_domain'].value_counts().to_string())

        print("\nBy year:")
        print(final_df['collection_year'].value_counts().sort_index().to_string())

        # Save final file
        output_path = "data/raw/china_daily/chinese_state_media_tibet_2008_2024.csv"
        final_df.to_csv(output_path, index=False)
        print(f"\nSaved to: {output_path}")

        return final_df
    else:
        print("No articles collected!")
        return pd.DataFrame()


if __name__ == "__main__":
    df = collect_full_dataset()
