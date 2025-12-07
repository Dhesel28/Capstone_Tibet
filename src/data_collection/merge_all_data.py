"""
Merge Historical and Recent Data for Complete 2008-2024 Coverage
Combines:
- Historical data (2008-2016) from Wayback Machine
- Recent data (2017-2024) from GDELT
"""

import pandas as pd
import os
from datetime import datetime


def merge_chinese_media():
    """Merge Chinese state media datasets."""
    print("=" * 70)
    print("MERGING CHINESE STATE MEDIA DATA")
    print("=" * 70)

    dfs = []

    # Historical data (2008-2016)
    historical_path = "data/raw/chinese_state_media/historical_chinese_2008_2016.csv"
    if os.path.exists(historical_path):
        historical_df = pd.read_csv(historical_path)
        historical_df['data_source'] = 'Wayback Machine'
        dfs.append(historical_df)
        print(f"Historical (2008-2016): {len(historical_df)} articles")
    else:
        print(f"Historical data not found: {historical_path}")

    # Recent data (2017-2024)
    recent_path = "data/raw/china_daily/chinese_state_media_with_text.csv"
    if os.path.exists(recent_path):
        recent_df = pd.read_csv(recent_path)
        recent_df['data_source'] = 'GDELT'
        dfs.append(recent_df)
        print(f"Recent (2017-2024): {len(recent_df)} articles")
    else:
        print(f"Recent data not found: {recent_path}")

    if dfs:
        # Combine
        combined = pd.concat(dfs, ignore_index=True)

        # Standardize columns
        standard_cols = ['url', 'headline', 'body_text', 'source', 'source_category',
                        'collection_year', 'data_source']
        for col in standard_cols:
            if col not in combined.columns:
                combined[col] = None

        # Remove duplicates by URL
        original_len = len(combined)
        combined = combined.drop_duplicates(subset=['url'], keep='first')
        print(f"Removed {original_len - len(combined)} duplicates")

        # Ensure source_category
        combined['source_category'] = 'Chinese State Media'

        # Save
        output_path = "data/processed/chinese_state_media_2008_2024.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        combined.to_csv(output_path, index=False)

        print(f"\nTotal: {len(combined)} articles")
        if 'collection_year' in combined.columns:
            print("\nBy year:")
            print(combined['collection_year'].value_counts().sort_index())

        print(f"\nSaved to: {output_path}")
        return combined

    return pd.DataFrame()


def merge_international_media():
    """Merge international media datasets."""
    print("\n" + "=" * 70)
    print("MERGING INTERNATIONAL MEDIA DATA")
    print("=" * 70)

    dfs = []

    # Historical data (2008-2016)
    historical_path = "data/raw/neutral_sources/historical_international_2008_2016.csv"
    if os.path.exists(historical_path):
        historical_df = pd.read_csv(historical_path)
        historical_df['data_source'] = 'Wayback Machine'
        dfs.append(historical_df)
        print(f"Historical (2008-2016): {len(historical_df)} articles")
    else:
        print(f"Historical data not found: {historical_path}")

    # Recent data (2017-2024)
    recent_path = "data/raw/neutral_sources/international_media_with_text.csv"
    if os.path.exists(recent_path):
        recent_df = pd.read_csv(recent_path)
        recent_df['data_source'] = 'GDELT'
        dfs.append(recent_df)
        print(f"Recent (2017-2024): {len(recent_df)} articles")
    else:
        print(f"Recent data not found: {recent_path}")

    if dfs:
        # Combine
        combined = pd.concat(dfs, ignore_index=True)

        # Remove duplicates
        original_len = len(combined)
        combined = combined.drop_duplicates(subset=['url'], keep='first')
        print(f"Removed {original_len - len(combined)} duplicates")

        # Ensure source_category
        combined['source_category'] = 'International/Neutral'

        # Save
        output_path = "data/processed/international_media_2008_2024.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        combined.to_csv(output_path, index=False)

        print(f"\nTotal: {len(combined)} articles")
        if 'collection_year' in combined.columns:
            print("\nBy year:")
            print(combined['collection_year'].value_counts().sort_index())

        if 'source_name' in combined.columns:
            print("\nBy source:")
            print(combined['source_name'].value_counts())

        print(f"\nSaved to: {output_path}")
        return combined

    return pd.DataFrame()


def copy_guardian_data():
    """Copy Guardian data to processed folder."""
    print("\n" + "=" * 70)
    print("WESTERN MEDIA (GUARDIAN) DATA")
    print("=" * 70)

    source_path = "data/raw/guardian/guardian_tibet_articles.csv"
    if os.path.exists(source_path):
        df = pd.read_csv(source_path)
        df['source_category'] = 'Western Media'
        df['data_source'] = 'Guardian API'

        output_path = "data/processed/western_media_2008_2024.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)

        print(f"Total: {len(df)} articles")
        if 'collection_year' in df.columns:
            print("\nBy year:")
            print(df['collection_year'].value_counts().sort_index())

        print(f"\nSaved to: {output_path}")
        return df

    print(f"Guardian data not found: {source_path}")
    return pd.DataFrame()


def create_combined_dataset():
    """Create a single combined dataset with all sources."""
    print("\n" + "=" * 70)
    print("CREATING COMBINED DATASET")
    print("=" * 70)

    dfs = []

    # Load all processed datasets
    paths = {
        'Chinese State Media': 'data/processed/chinese_state_media_2008_2024.csv',
        'Western Media': 'data/processed/western_media_2008_2024.csv',
        'International/Neutral': 'data/processed/international_media_2008_2024.csv'
    }

    for category, path in paths.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['source_category'] = category
            dfs.append(df)
            print(f"{category}: {len(df)} articles")

    if dfs:
        combined = pd.concat(dfs, ignore_index=True)

        # Save combined
        output_path = "data/processed/all_sources_2008_2024.csv"
        combined.to_csv(output_path, index=False)

        print(f"\n{'=' * 70}")
        print(f"COMBINED DATASET: {len(combined)} total articles")
        print(f"{'=' * 70}")
        print("\nBy source category:")
        print(combined['source_category'].value_counts())

        if 'collection_year' in combined.columns:
            print("\nBy year:")
            print(combined['collection_year'].value_counts().sort_index())

        print(f"\nSaved to: {output_path}")
        return combined

    return pd.DataFrame()


if __name__ == "__main__":
    print("MERGING ALL DATA SOURCES FOR 2008-2024 COVERAGE")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    # Merge each category
    chinese_df = merge_chinese_media()
    international_df = merge_international_media()
    guardian_df = copy_guardian_data()

    # Create combined dataset
    combined_df = create_combined_dataset()

    print("\n" + "=" * 70)
    print("MERGE COMPLETE!")
    print("=" * 70)
