#!/usr/bin/env python3
"""
Create Balanced Preprocessed Dataset for Tibet Media Framing Analysis

This script:
1. Loads all raw data from both source categories
2. Preprocesses text (cleaning, tokenization)
3. Filters out short articles (< 20 tokens) BEFORE balancing
4. Creates year-stratified balanced dataset (50/50 split)
5. Saves the final dataset ready for analysis

This ensures no articles are lost during the analysis phase.
"""

import pandas as pd
import numpy as np
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import warnings
import os
from datetime import datetime

warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

BASE_PATH = '/Users/dhekha/Desktop/Capstone_Tibet'
MIN_TOKENS = 20  # Minimum tokens required for an article

def clean_text(text):
    """Clean and normalize text."""
    if pd.isna(text) or not isinstance(text, str):
        return ""

    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\'\"\-]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def tokenize_text(text):
    """Tokenize and filter text."""
    if not text:
        return []

    stop_words = set(stopwords.words('english'))

    # Tokenize
    tokens = word_tokenize(text.lower())

    # Filter: keep only alphabetic tokens, remove stopwords and short words
    tokens = [
        token for token in tokens
        if token.isalpha()
        and token not in stop_words
        and len(token) > 2
    ]

    return tokens

def load_chinese_state_media():
    """Load all Chinese State Media articles."""
    print("\nLoading Chinese State Media...")

    all_articles = []

    # China Daily
    china_daily_path = f'{BASE_PATH}/data/raw/china_daily'
    if os.path.exists(china_daily_path):
        for file in os.listdir(china_daily_path):
            if file.endswith('.csv'):
                try:
                    df = pd.read_csv(f'{china_daily_path}/{file}')
                    df['source'] = 'China Daily'
                    all_articles.append(df)
                    print(f"  China Daily: {len(df)} articles from {file}")
                except Exception as e:
                    print(f"  Error loading {file}: {e}")

    # Xinhua
    xinhua_path = f'{BASE_PATH}/data/raw/xinhua'
    if os.path.exists(xinhua_path):
        for file in os.listdir(xinhua_path):
            if file.endswith('.csv'):
                try:
                    df = pd.read_csv(f'{xinhua_path}/{file}')
                    df['source'] = 'Xinhua'
                    all_articles.append(df)
                    print(f"  Xinhua: {len(df)} articles from {file}")
                except Exception as e:
                    print(f"  Error loading {file}: {e}")

    # ECNS
    ecns_path = f'{BASE_PATH}/data/raw/ecns'
    if os.path.exists(ecns_path):
        for file in os.listdir(ecns_path):
            if file.endswith('.csv'):
                try:
                    df = pd.read_csv(f'{ecns_path}/{file}')
                    df['source'] = 'ECNS'
                    all_articles.append(df)
                    print(f"  ECNS: {len(df)} articles from {file}")
                except Exception as e:
                    print(f"  Error loading {file}: {e}")

    # Global Times
    global_times_path = f'{BASE_PATH}/data/raw/global_times'
    if os.path.exists(global_times_path):
        for file in os.listdir(global_times_path):
            if file.endswith('.csv'):
                try:
                    df = pd.read_csv(f'{global_times_path}/{file}')
                    df['source'] = 'Global Times'
                    all_articles.append(df)
                    print(f"  Global Times: {len(df)} articles from {file}")
                except Exception as e:
                    print(f"  Error loading {file}: {e}")

    if all_articles:
        combined = pd.concat(all_articles, ignore_index=True)
        combined['source_category'] = 'Chinese State Media'
        return combined
    return pd.DataFrame()

def load_western_media():
    """Load all Western Media articles."""
    print("\nLoading Western Media...")

    all_articles = []

    # Guardian
    guardian_path = f'{BASE_PATH}/data/raw/guardian'
    if os.path.exists(guardian_path):
        for file in os.listdir(guardian_path):
            if file.endswith('.csv'):
                try:
                    df = pd.read_csv(f'{guardian_path}/{file}')
                    df['source'] = 'The Guardian'
                    all_articles.append(df)
                    print(f"  Guardian: {len(df)} articles from {file}")
                except Exception as e:
                    print(f"  Error loading {file}: {e}")

    # GDELT Western Media
    gdelt_path = f'{BASE_PATH}/data/raw/gdelt_western'
    if os.path.exists(gdelt_path):
        for file in os.listdir(gdelt_path):
            if file.endswith('.csv'):
                try:
                    df = pd.read_csv(f'{gdelt_path}/{file}')
                    # GDELT has 'source_name' column
                    if 'source_name' in df.columns:
                        df['source'] = df['source_name']
                    elif 'source' not in df.columns:
                        df['source'] = 'Western Media'
                    all_articles.append(df)
                    print(f"  GDELT Western: {len(df)} articles from {file}")
                except Exception as e:
                    print(f"  Error loading {file}: {e}")

    if all_articles:
        combined = pd.concat(all_articles, ignore_index=True)
        combined['source_category'] = 'Western Media'
        return combined
    return pd.DataFrame()

def standardize_columns(df):
    """Standardize column names across different sources."""
    # Map various column names to standard names
    column_mapping = {
        'title': 'headline',
        'Title': 'headline',
        'headline': 'headline',
        'Headline': 'headline',
        'body': 'body_text',
        'Body': 'body_text',
        'body_text': 'body_text',
        'text': 'body_text',
        'content': 'body_text',
        'article_text': 'body_text',
        'date': 'publication_date',
        'Date': 'publication_date',
        'publication_date': 'publication_date',
        'pub_date': 'publication_date',
        'seendate': 'publication_date',
    }

    # Rename columns
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns and new_name not in df.columns:
            df = df.rename(columns={old_name: new_name})

    return df

def extract_year(df):
    """Extract year from publication date."""
    if 'year' in df.columns:
        return df

    if 'publication_date' in df.columns:
        # Try multiple date formats
        for date_col in ['publication_date', 'seendate', 'date']:
            if date_col in df.columns:
                try:
                    df['year'] = pd.to_datetime(df[date_col], errors='coerce').dt.year
                    break
                except:
                    continue

    return df

def preprocess_articles(df):
    """Preprocess all articles: clean text and tokenize."""
    print("\nPreprocessing articles...")

    # Get text column
    text_col = None
    for col in ['body_text', 'text', 'content', 'body']:
        if col in df.columns:
            text_col = col
            break

    if text_col is None:
        print("  ERROR: No text column found!")
        return df

    print(f"  Using text column: {text_col}")

    # Clean text
    print("  Cleaning text...")
    df['clean_text'] = df[text_col].apply(clean_text)

    # Tokenize
    print("  Tokenizing...")
    df['tokens'] = df['clean_text'].apply(tokenize_text)

    # Count tokens
    df['token_count'] = df['tokens'].apply(len)

    return df

def filter_short_articles(df, min_tokens=MIN_TOKENS):
    """Remove articles with fewer than min_tokens tokens."""
    original_count = len(df)
    df_filtered = df[df['token_count'] >= min_tokens].copy()
    removed = original_count - len(df_filtered)

    print(f"\nFiltered short articles (< {min_tokens} tokens):")
    print(f"  Original: {original_count}")
    print(f"  Removed: {removed}")
    print(f"  Remaining: {len(df_filtered)}")

    # Show breakdown by category
    if 'source_category' in df.columns:
        print("\n  Removed by category:")
        for cat in df['source_category'].unique():
            orig = len(df[df['source_category'] == cat])
            filt = len(df_filtered[df_filtered['source_category'] == cat])
            print(f"    {cat}: {orig - filt} removed ({orig} -> {filt})")

    return df_filtered

def create_balanced_dataset(df, random_state=42):
    """Create year-stratified balanced dataset."""
    print("\nCreating balanced dataset...")

    np.random.seed(random_state)

    chinese_df = df[df['source_category'] == 'Chinese State Media']
    western_df = df[df['source_category'] == 'Western Media']

    print(f"  Available Chinese: {len(chinese_df)}")
    print(f"  Available Western: {len(western_df)}")

    # Get available years
    years = sorted(df['year'].dropna().unique())
    years = [int(y) for y in years if 2017 <= y <= 2024]

    balanced_samples = []

    print("\n  Year-stratified sampling:")
    for year in years:
        chinese_year = chinese_df[chinese_df['year'] == year]
        western_year = western_df[western_df['year'] == year]

        n_chinese = len(chinese_year)
        n_western = len(western_year)

        # Take minimum of the two
        n_sample = min(n_chinese, n_western)

        if n_sample > 0:
            chinese_sample = chinese_year.sample(n=n_sample, random_state=random_state)
            western_sample = western_year.sample(n=n_sample, random_state=random_state)

            balanced_samples.append(chinese_sample)
            balanced_samples.append(western_sample)

            print(f"    {year}: {n_sample} per category (Chinese had {n_chinese}, Western had {n_western})")

    balanced_df = pd.concat(balanced_samples, ignore_index=True)

    print(f"\n  Final balanced dataset: {len(balanced_df)} articles")
    print(f"    Chinese: {len(balanced_df[balanced_df['source_category'] == 'Chinese State Media'])}")
    print(f"    Western: {len(balanced_df[balanced_df['source_category'] == 'Western Media'])}")

    return balanced_df

def main():
    print("=" * 70)
    print("CREATING BALANCED PREPROCESSED DATASET")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Load all data
    chinese_df = load_chinese_state_media()
    western_df = load_western_media()

    if len(chinese_df) == 0 or len(western_df) == 0:
        print("\nERROR: Could not load data from one or both sources!")
        return

    # Combine
    print("\nCombining datasets...")
    combined_df = pd.concat([chinese_df, western_df], ignore_index=True)
    print(f"  Total raw articles: {len(combined_df)}")

    # Standardize columns
    combined_df = standardize_columns(combined_df)

    # Extract year
    combined_df = extract_year(combined_df)

    # Filter to 2017-2024
    combined_df = combined_df[combined_df['year'].between(2017, 2024)]
    print(f"  Articles 2017-2024: {len(combined_df)}")

    # Remove duplicates by URL if available
    if 'url' in combined_df.columns:
        original = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['url'], keep='first')
        print(f"  After deduplication: {len(combined_df)} (removed {original - len(combined_df)} duplicates)")

    # Preprocess (clean + tokenize)
    combined_df = preprocess_articles(combined_df)

    # Filter short articles BEFORE balancing
    filtered_df = filter_short_articles(combined_df, min_tokens=MIN_TOKENS)

    # Create balanced dataset
    balanced_df = create_balanced_dataset(filtered_df)

    # Save results
    output_dir = f'{BASE_PATH}/data/processed'
    os.makedirs(output_dir, exist_ok=True)

    # Save CSV (without tokens for smaller file)
    csv_cols = ['headline', 'body_text', 'clean_text', 'source', 'source_category',
                'publication_date', 'year', 'url', 'token_count']
    csv_cols = [c for c in csv_cols if c in balanced_df.columns]
    balanced_df[csv_cols].to_csv(f'{output_dir}/balanced_preprocessed.csv', index=False)

    # Save pickle (with tokens for analysis)
    balanced_df.to_pickle(f'{output_dir}/balanced_preprocessed.pkl')

    print("\n" + "=" * 70)
    print("OUTPUT FILES")
    print("=" * 70)
    print(f"  CSV: {output_dir}/balanced_preprocessed.csv")
    print(f"  PKL: {output_dir}/balanced_preprocessed.pkl")

    # Summary
    print("\n" + "=" * 70)
    print("FINAL DATASET SUMMARY")
    print("=" * 70)
    print(f"Total articles: {len(balanced_df)}")
    print(f"\nBy source category:")
    print(balanced_df['source_category'].value_counts())
    print(f"\nBy year:")
    print(balanced_df.groupby(['year', 'source_category']).size().unstack(fill_value=0))
    print(f"\nAverage token count: {balanced_df['token_count'].mean():.1f}")
    print(f"Min token count: {balanced_df['token_count'].min()}")

    return balanced_df

if __name__ == "__main__":
    main()
