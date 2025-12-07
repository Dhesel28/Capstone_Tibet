"""
Run full text fetch for Chinese state media articles.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
import time
import random
from datetime import datetime
from src.data_collection.fetch_article_text import ArticleTextFetcher


def main():
    # Load data
    input_file = "data/raw/china_daily/chinese_state_media_tibet_2008_2024.csv"
    df = pd.read_csv(input_file)

    # Focus on sources with working parsers
    working_sources = ['globaltimes.cn', 'chinadaily.com.cn', 'xinhuanet.com', 'ecns.cn']
    df = df[df['source_domain'].isin(working_sources)]

    print("=" * 70)
    print("FETCHING FULL ARTICLE TEXT")
    print("=" * 70)
    print(f"Total articles: {len(df)}")
    print(f"Sources: {', '.join(working_sources)}")
    print("=" * 70)

    fetcher = ArticleTextFetcher()
    results = []
    failed = []

    total = len(df)
    start_time = datetime.now()

    for i, (_, row) in enumerate(df.iterrows()):
        url = row['url']
        domain = row['source_domain']

        # Progress
        if (i + 1) % 50 == 0:
            elapsed = (datetime.now() - start_time).seconds
            rate = (i + 1) / max(elapsed, 1) * 60  # articles per minute
            eta = (total - i - 1) / max(rate, 0.1)  # minutes remaining
            print(f"\nProgress: {i + 1}/{total} ({100*(i+1)//total}%)")
            print(f"  Success: {len(results)}, Failed: {len(failed)}")
            print(f"  Rate: {rate:.1f} articles/min, ETA: {eta:.0f} min")

        try:
            result = fetcher.fetch_article(url, domain)

            if result and result.get('body_text') and len(result.get('body_text', '')) > 100:
                # Add original metadata
                result['original_title'] = row.get('title', '')
                result['seendate'] = row.get('seendate', '')
                result['source_domain'] = domain
                result['source_category'] = 'Chinese State Media'
                result['collection_year'] = row.get('collection_year', '')
                results.append(result)
            else:
                failed.append({'url': url, 'domain': domain, 'reason': 'No text'})

        except Exception as e:
            failed.append({'url': url, 'domain': domain, 'reason': str(e)})

        # Rate limiting
        time.sleep(random.uniform(0.5, 1.5))

        # Checkpoint every 200 articles
        if (i + 1) % 200 == 0:
            checkpoint_df = pd.DataFrame(results)
            checkpoint_df.to_csv("data/raw/china_daily/fetch_checkpoint.csv", index=False)
            print(f"  [Checkpoint saved: {len(results)} articles]")

    # Final save
    print("\n" + "=" * 70)
    print("FETCH COMPLETE")
    print("=" * 70)
    print(f"Total processed: {total}")
    print(f"Successfully fetched: {len(results)}")
    print(f"Failed: {len(failed)}")
    print(f"Success rate: {100*len(results)//total}%")

    if results:
        results_df = pd.DataFrame(results)

        # Summary by source
        print("\nBy source:")
        print(results_df['source_domain'].value_counts().to_string())

        # Average text length
        avg_len = results_df['body_text'].str.len().mean()
        print(f"\nAverage article length: {avg_len:.0f} chars")

        # Save
        output_file = "data/raw/china_daily/chinese_state_media_with_text.csv"
        results_df.to_csv(output_file, index=False)
        print(f"\nSaved to: {output_file}")

    # Save failed URLs for retry
    if failed:
        failed_df = pd.DataFrame(failed)
        failed_df.to_csv("data/raw/china_daily/failed_urls.csv", index=False)
        print(f"Failed URLs saved to: data/raw/china_daily/failed_urls.csv")

    return results_df if results else None


if __name__ == "__main__":
    main()
