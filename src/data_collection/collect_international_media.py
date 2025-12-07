"""
International/Neutral Media Collection for Tibet News Analysis
Capstone Project - Dhesel Khando

Collects Tibet-related articles from neutral/international sources:
- Al Jazeera (Qatar - Middle Eastern perspective)
- Deutsche Welle (Germany - European perspective)
- South China Morning Post (Hong Kong - nuanced China coverage)
- Reuters (International wire service)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_collection.gdelt_collector import GDELTCollector
import pandas as pd
import time
from datetime import datetime


def collect_international_sources():
    """Collect articles from international/neutral news sources."""

    collector = GDELTCollector()

    # International/neutral media domains
    sources = {
        # Al Jazeera - Qatar-based, Middle Eastern perspective
        'aljazeera.com': 'Al Jazeera',

        # Deutsche Welle - German international broadcaster
        'dw.com': 'Deutsche Welle',

        # South China Morning Post - Hong Kong, nuanced China coverage
        'scmp.com': 'South China Morning Post',

        # Reuters - International wire service
        'reuters.com': 'Reuters',

        # Additional international sources
        'bbc.com': 'BBC',
        'france24.com': 'France 24',
    }

    # Years to collect (GDELT has better coverage from 2017+)
    start_year = 2017
    end_year = 2024

    all_articles = []

    print("=" * 70)
    print("INTERNATIONAL/NEUTRAL MEDIA COLLECTION - Tibet Articles")
    print("=" * 70)
    print(f"Period: {start_year}-{end_year}")
    print(f"Sources: {', '.join(sources.values())}")
    print("=" * 70)

    for domain, source_name in sources.items():
        print(f"\n{'='*70}")
        print(f"SOURCE: {source_name} ({domain})")
        print("=" * 70)

        source_articles = []

        for year in range(start_year, end_year + 1):
            print(f"\n  Year {year}...")

            # GDELT date format
            start_date = f"{year}0101000000"
            end_date = f"{year}1231235959"

            try:
                df = collector.search_articles(
                    query="Tibet",
                    source_domain=domain,
                    start_date=start_date,
                    end_date=end_date,
                    max_records=250
                )

                if df is not None and not df.empty:
                    df['source_domain'] = domain
                    df['source_name'] = source_name
                    df['source_category'] = 'International/Neutral'
                    df['collection_year'] = year
                    source_articles.append(df)
                    print(f"    Found {len(df)} articles")
                else:
                    print(f"    No articles")

            except Exception as e:
                print(f"    Error: {e}")

            time.sleep(1)  # Rate limiting

        # Combine source articles
        if source_articles:
            source_df = pd.concat(source_articles, ignore_index=True)
            all_articles.append(source_df)
            print(f"\n  {source_name} total: {len(source_df)} articles")

    # Final save
    if all_articles:
        final_df = pd.concat(all_articles, ignore_index=True)

        # Remove duplicates
        original_len = len(final_df)
        final_df = final_df.drop_duplicates(subset=['url'], keep='first')

        print("\n" + "=" * 70)
        print("COLLECTION COMPLETE")
        print("=" * 70)
        print(f"Total articles: {len(final_df)}")
        print(f"Duplicates removed: {original_len - len(final_df)}")

        # Summary by source
        print("\nBy source:")
        print(final_df['source_name'].value_counts().to_string())

        print("\nBy year:")
        print(final_df['collection_year'].value_counts().sort_index().to_string())

        # Save
        output_path = "data/raw/neutral_sources/international_media_tibet.csv"
        final_df.to_csv(output_path, index=False)
        print(f"\nSaved to: {output_path}")

        return final_df
    else:
        print("No articles collected!")
        return pd.DataFrame()


if __name__ == "__main__":
    df = collect_international_sources()
