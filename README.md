# Tibet Media Framing Analysis

**A Computational Comparison of Chinese State Media and Western Media Coverage (2017-2024)**

**Vanderbilt University Data Science Capstone (DS-5999)**
**Author:** Dhesel Khando
**Advisor:** Professor Scott Crossley
**Date:** December 2024

## Overview

This project applies Natural Language Processing (NLP) techniques to analyze how Chinese State Media and Western Media frame Tibet-related coverage. The analysis reveals systematic differences in sentiment, terminology, and thematic emphasis between these two media categories.

## Key Findings

All three hypotheses were supported by the data:

| Hypothesis | Result | Key Statistics |
|------------|--------|----------------|
| **H1: Sentiment** | Supported | Chinese media significantly more positive (mean: 0.577 vs 0.106, t=15.00, p<0.001, Cohen's d=0.66) |
| **H2: Terminology** | Supported | Western media uses 7.1x more "Western framing" terms; Chinese media uses 2.2x more "development" terms |
| **H3: Topics** | Supported | 6 of 7 topics show statistically significant differences (p<0.001) |

## Dataset

| Category | Articles | Sources |
|----------|----------|---------|
| Chinese State Media | 1,027 | China Daily, Xinhua, ECNS, Global Times |
| Western Media | 1,027 | The Guardian, BBC, Washington Post, CNN, Telegraph, NPR, The Independent |
| **Total** | 2,054 | Year-stratified balanced sample (2017-2024) |

## Methodology

- **Sentiment Analysis:** VADER (lexicon-based) and BERT (transformer-based, cardiffnlp/twitter-roberta-base-sentiment-latest)
- **Topic Modeling:** LDA with Gensim (7 optimal topics via coherence score optimization)
- **Terminology Analysis:** Framing term frequency comparison
- **Statistical Testing:** Welch's t-test, Cohen's d effect size

## Project Structure

```
Capstone_Tibet/
├── data/
│   ├── raw/                    # Original collected data by source
│   └── processed/
│       ├── balanced_dataset.csv         # Final balanced dataset
│       └── balanced_preprocessed.pkl    # Preprocessed with tokens
├── notebooks/
│   ├── Tibet_Media_Framing_Analysis_Colab.ipynb  # Main analysis notebook
│   └── Tibet_Media_Framing_Analysis_Colab.pdf    # PDF export
├── src/
│   ├── data_collection/        # Scrapers and API collectors
│   │   ├── guardian_api_collector.py
│   │   ├── china_daily_scraper.py
│   │   ├── xinhua_scraper.py
│   │   ├── global_times_scraper.py
│   │   ├── gdelt_collector.py
│   │   └── ...
│   ├── create_balanced_preprocessed_dataset.py
│   ├── preprocessing/
│   ├── models/
│   └── visualization/
├── results/
│   ├── analysis_results.txt
│   └── Tibet_Media_Framing_Analysis_Colab.pdf
├── docs/
│   └── session_log.md          # Development history
└── requirements.txt
```

## Data Collection Scripts

| Script | Purpose |
|--------|---------|
| `guardian_api_collector.py` | Collects articles from The Guardian API |
| `china_daily_scraper.py` | Scrapes China Daily Tibet coverage |
| `xinhua_scraper.py` | Scrapes Xinhua News Agency |
| `global_times_scraper.py` | Scrapes Global Times |
| `gdelt_collector.py` | Collects Western media via GDELT database |
| `collect_western_media.py` | Aggregates Western sources |
| `fetch_article_text.py` | Fetches full article text from URLs |

## Setup

```bash
# Clone the repository
git clone https://github.com/Dhesel28/Capstone_Tibet.git
cd Capstone_Tibet

# Install dependencies
pip install -r requirements.txt

# Run the analysis notebook
jupyter notebook notebooks/Tibet_Media_Framing_Analysis_Colab.ipynb
```

## Requirements

- Python 3.9+
- pandas, numpy, scipy
- nltk, gensim
- transformers, torch
- matplotlib, seaborn
- wordcloud

## Visualizations

The analysis includes 7 figures:
1. Dataset Distribution Analysis
2. VADER Sentiment Distribution
3. BERT Sentiment Analysis
4. Temporal Sentiment Dynamics
5. Topic Model Selection (Coherence Scores)
6. Topic Distribution by Source
7. Temporal Topic Evolution

## References

Key literature informing this study:
- Entman, R. M. (1993). Framing: Toward clarification of a fractured paradigm. *Journal of Communication*
- Herman, E. S., & Chomsky, N. (1988). *Manufacturing Consent*
- Brady, A. M. (2008). *Marketing Dictatorship*
- Yeh, E. T. (2013). *Taming Tibet: Landscape Transformation and the Gift of Chinese Development*
- Barnett, R. (2009). The Tibet protests of spring 2008

## Acknowledgements

This paper's grammar and language were refined with the assistance of the Claude language model (Anthropic, 2024).

I sincerely thank Professor Scott Crossley for his invaluable guidance in refining my research question and providing insightful feedback on my paper.

## License

This project is for academic purposes as part of the Vanderbilt University Data Science Capstone.
