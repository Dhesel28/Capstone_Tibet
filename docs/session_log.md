# Tibet Media Framing Analysis - Session Log

## Project Overview
- **Author:** Dhesel Khando
- **Course:** DS-5999 Data Science Capstone
- **Institution:** Vanderbilt University
- **Session Date:** December 2024

---

## Session Summary

This document captures the complete development history of the Tibet Media Framing Analysis project across multiple Claude Code sessions.

---

## 1. Project Description

A computational analysis comparing media framing of Tibet between Chinese State Media and Western Media (The Guardian) from 2017-2024. The study uses NLP techniques including:
- VADER Sentiment Analysis (lexicon-based)
- BERT Sentiment Analysis (transformer-based, cardiffnlp/twitter-roberta-base-sentiment-latest)
- LDA Topic Modeling (Gensim, 6 optimal topics)
- Terminology/Framing Analysis
- Temporal Analysis

### Research Hypotheses
- **H1:** Chinese State Media exhibits more positive sentiment than Western Media
- **H2:** Each media category uses distinctive terminology aligned with political framing
- **H3:** Topic distributions differ significantly between source categories

---

## 2. Dataset

### Current Balanced Dataset (Updated December 2024)

| Source Category | Articles | Percentage |
|-----------------|----------|------------|
| Chinese State Media | 1,042 | 50.0% |
| Western Media | 1,042 | 50.0% |
| **TOTAL** | 2,084 | 100% |

### Year-Stratified Distribution:

| Year | Western | Chinese | Total |
|------|---------|---------|-------|
| 2017 | 152 | 152 | 304 |
| 2018 | 168 | 168 | 336 |
| 2019 | 159 | 159 | 318 |
| 2020 | 125 | 125 | 250 |
| 2021 | 225 | 225 | 450 |
| 2022 | 142 | 142 | 284 |
| 2023 | 57 | 57 | 114 |
| 2024 | 14 | 14 | 28 |

### Western Media Sources:
- The Guardian: 536 articles
- BBC: 298 articles
- Washington Post: 187 articles
- CNN: 156 articles
- The Telegraph: 134 articles
- NPR: 89 articles
- The Independent: 76 articles

### Chinese State Media Sources:
- China Daily: 996 articles (53.7%)
- Xinhua: 386 articles (20.8%)
- ECNS: 341 articles (18.4%)
- Global Times: 130 articles (7.0%)

### Previous Unbalanced Dataset (for reference):

| Source Category | Articles | Percentage |
|-----------------|----------|------------|
| Chinese State Media | 1,827 | 77.3% |
| Western Media (Guardian only) | 536 | 22.7% |
| **TOTAL** | 2,363 | 100% |

---

## 3. Key Files Modified

### Primary Notebook
`/Users/dhekha/Desktop/Capstone_Tibet/notebooks/Tibet_Media_Framing_Analysis_Local.ipynb`

### Data Collection Scripts
- `data_collection/china_daily_scraper.py`
- `data_collection/guardian_api_collector.py`

### Generated Data Files (in notebooks/)
- `temp_combined_data.pkl` - Raw combined dataset
- `temp_preprocessed_data.pkl` - Preprocessed with tokens
- `temp_sentiment_data.pkl` - With VADER sentiment scores
- `temp_topics_data.pkl` - With topic distributions
- `temp_dictionary.dict` - Gensim dictionary
- `temp_corpus.pkl` - Bag-of-words corpus
- `temp_lda_model` - Trained LDA model

### Results
- `results/analysis_results.txt` - Complete analysis results

---

## 4. Development History

### Phase 1: Initial Setup and Bug Fixes
- Fixed critical date column ordering bug where `seendate` needed to come before `publication_date`
- This bug was causing data loss (3270 → 664 articles)
- Migrated from Google Colab to local execution

### Phase 2: Formal Research Paper Formatting
User requested: *"Write analysis on Tibet media framing analysis local in formal tone and chose output that makes sense and make sure that all graphs has title and labels are consistent. Make it cohesive and research based project"*

Changes made:
- Updated notebook structure with formal academic sections
- Standardized all visualizations with consistent figure numbering (1-8)
- Added hypothesis tables, abstracts, references
- Added proper section headers (Introduction, Data, Methodology, Results, Discussion, Conclusion)

### Phase 3: Graph Analysis and Redundancy Removal
User requested: *"Make sure that code chunks has description that cohesive and follows through research and graph has analysis, so make sure that if graph does not make sense and it is redundant, get rid of it"*

Changes made:
- Consolidated redundant visualizations (temporal topic plots merged into single Figure 7)
- Added analysis markdown cells after each figure (8 interpretation cells)
- Updated visualizations with better panel labels (A, B, C, D)
- Reduced redundancy while maintaining comprehensive coverage

### Phase 4: Flowing Prose Conversion
User requested: *"Right now it is written in points, make it flows and every output of the cell should have explanation that also flows through the project"*

Changes made:
- Converted all bullet-point sections to flowing prose paragraphs
- Updated Introduction with connected narrative (background, motivation, significance)
- Rewrote all 8 figure interpretation cells as connected prose
- Updated Preprocessing and Methodology sections
- Rewrote Discussion section with synthesis, theoretical implications, limitations
- Updated Conclusion with flowing narrative
- Ensured all sections connect naturally to create cohesive research paper

### Phase 5: Data Expansion and Balanced Sampling (December 2024)
User requested exploration of additional Western media sources and balanced sampling approach.

**Data Exploration:**
- Discovered GDELT Western Media data (BBC, Washington Post, CNN, Telegraph, NPR, Independent)
- Found additional International Media sources (SCMP, Deutsche Welle)
- Analyzed article availability by year for each source

**Balanced Dataset Creation:**
User requested: *"How about 100 each news paper every year from both side and do random sampling"*

Analysis revealed:
- 100 articles per source per year was not feasible (most sources don't have that many Tibet articles)
- Chinese State Media has limited 2023-2024 coverage (57 in 2023, 14 in 2024)

Solution implemented:
- Year-stratified random sampling approach
- Take minimum available from each category per year to ensure balance
- Created balanced dataset: 2,084 articles (1,042 per category, 50/50 split)
- Random seed=42 for reproducibility

**Notebook Updates:**
User requested: *"Can you now update my notebook and updating everything you did with code also"*

Cells updated:
- Cell 7: Data Sources description with new balanced methodology
- Cell 12: New `load_balanced_data()` function for data loading
- Cell 13: Data validation code
- Cell 14: Dataset summary statistics
- Cell 15: Figure 1 visualization updated for multiple sources
- Cell 16: Figure 1 interpretation with new statistics
- Cell 64: Summary of Empirical Findings
- Cell 66: Discussion Synthesis
- Cell 68: Conclusion

**New Files Created:**
- `data/processed/balanced_dataset.csv` - Balanced dataset (2,084 articles)
- `notebooks/balanced_dataset.pkl` - Pickle version for faster loading
- `data_collection/scrape_chinese_2023_2024.py` - Scraper for additional Chinese media

---

## 5. Final Notebook Structure (71 cells)

| Cell Range | Section | Content |
|------------|---------|---------|
| 0-1 | Header | Author info, title |
| 2-3 | Introduction | Background, motivation, significance |
| 4-5 | Hypotheses | Research questions, theoretical framework |
| 6-14 | Data | Sources, collection methodology, loading |
| 15-16 | Figure 1 | Dataset distribution + interpretation |
| 17-24 | Preprocessing | Text cleaning, tokenization, dictionary |
| 25-31 | Sentiment (VADER) | Figure 2 + analysis |
| 32-37 | Sentiment (BERT) | Figure 3 + analysis |
| 38-44 | Temporal Sentiment | Figure 4 + analysis |
| 45-48 | Topic Selection | Figure 5 + analysis |
| 49-55 | Topic Distribution | Figure 6 + analysis |
| 56-58 | Temporal Topics | Figure 7 + analysis |
| 59-63 | Terminology | Figure 8 + analysis |
| 64 | Summary | Synthesis of H1, H2, H3 |
| 65-66 | Discussion | Interpretation, implications, limitations |
| 67-68 | Conclusion | Key contributions, future directions |
| 69-70 | References | Bibliography |

---

## 6. Key Findings (from analysis_results.txt)

### H1: Sentiment Differences - SUPPORTED
- Chinese State Media mean sentiment: 0.58 (SD: 0.60)
- Western Media mean sentiment: 0.19 (SD: 0.92)
- t-statistic: 11.74, p < 0.001
- Cohen's d: 0.58 (medium effect)
- 80% of Chinese articles positive vs 60% Western

### H2: Terminology Patterns - SUPPORTED
- Western Media uses 7x more "Western framing" terms (protest, rights, freedom, exile, crackdown, dalai)
- Chinese Media uses 2.2x more "Chinese framing" terms (development, stability, prosperity, progress, harmony)

### H3: Topic Distributions - SUPPORTED
- All 6 topics show statistically significant differences (p < 0.001)
- Large effect sizes across all topics (mean |d| ≈ 1.08)
- Chinese-dominant: Regional development (Topic 0), Climate/economic (Topic 2)
- Western-dominant: Human rights (Topic 4), Personal narratives (Topic 1)

---

## 7. Visualizations Created

1. **Figure 1:** Dataset Distribution Analysis (bar chart + pie chart)
2. **Figure 2:** VADER Sentiment Distribution (4-panel: density, violin, box, bar)
3. **Figure 3:** BERT Sentiment Analysis (4-panel: density, comparison, violin, correlation)
4. **Figure 4:** Temporal Sentiment Dynamics (4-panel: trajectories, yearly bars, heatmap, article counts)
5. **Figure 5:** Topic Model Selection (coherence score curve)
6. **Figure 6:** Topic Distribution by Source (4-panel: grouped bars, difference bars, heatmap, effect sizes)
7. **Figure 7:** Temporal Topic Evolution (4-panel: Chinese topics, Western topics, divergence, correlation)
8. **Figure 8:** Lexical Frequency Analysis (word clouds for each source)

---

## 8. Technical Details

### Libraries Used
- pandas, numpy, scipy (data processing)
- matplotlib, seaborn (visualization)
- nltk, gensim (NLP/topic modeling)
- transformers, torch (BERT sentiment)
- wordcloud (lexical visualization)

### Statistical Methods
- Welch's t-test for group comparisons
- Cohen's d for effect size
- Pearson correlation for method validation
- Coherence scores (c_v) for topic model selection

---

## 9. Files in Project Directory

```
Capstone_Tibet/
├── data/
│   ├── raw/
│   │   ├── china_daily/
│   │   ├── xinhua/
│   │   ├── ecns/
│   │   ├── global_times/
│   │   ├── gdelt_western/
│   │   ├── guardian/
│   │   └── tibetan_media/
│   └── processed/
│       └── balanced_dataset.csv (NEW - 2,084 balanced articles)
├── data_collection/
│   ├── china_daily_scraper.py
│   ├── guardian_api_collector.py
│   ├── scrape_chinese_2023_2024.py (NEW - scraper for additional Chinese media)
│   └── guardian_checkpoint_*.csv
├── docs/
│   └── session_log.md (this file)
├── notebooks/
│   ├── Tibet_Media_Framing_Analysis_Local.ipynb (UPDATED)
│   ├── balanced_dataset.pkl (NEW - pickle version)
│   ├── temp_*.pkl (intermediate data)
│   └── temp_lda_model (trained model)
├── results/
│   └── analysis_results.txt
├── src/
├── README.md
└── requirements.txt
```

---

## 10. Next Steps / Future Work

1. ~~Expand to additional Western sources (NYT, BBC, Reuters)~~ **COMPLETED** - Added BBC, Washington Post, CNN, Telegraph, NPR, Independent
2. Include Tibetan-language sources (14 articles available, limited for statistical analysis)
3. Apply advanced transformer models (GPT, Claude) for deeper analysis
4. Conduct event-based analysis around specific incidents
5. Develop interactive visualization dashboard
6. Scrape additional Chinese State Media for 2023-2024 (currently limited coverage)
7. Re-run full analysis pipeline with balanced dataset to update all statistics

---

## 11. Notes on Data Limitations

### Chinese State Media 2023-2024 Gap
- 2023: Only 57 articles available
- 2024: Only 14 articles available
- This reflects genuine reduced English-language Tibet coverage, not a sampling issue
- Created scraper script (`scrape_chinese_2023_2024.py`) for future data collection

### Sampling Methodology
- Year-stratified random sampling ensures temporal balance
- 50/50 split between categories eliminates sample size bias
- Random seed (42) ensures reproducibility
- Trade-off: Reduced total sample size from 2,363 to 2,084 articles

---

---

## 12. Statistical Validity: Pre-filtering Before Balancing

### Question
Is it valid to filter short articles BEFORE creating the balanced dataset?

### Answer: YES - This is the correct approach

**Why pre-filtering is statistically valid:**
1. **Consistent exclusion criteria** - Both Chinese and Western media are filtered using the same rule (< 20 tokens)
2. **Maintains balance** - Filtering first, then balancing ensures equal sample sizes throughout analysis
3. **Avoids post-hoc imbalance** - If you balance first then filter, you lose the 50/50 split
4. **Standard practice** - Data cleaning/filtering should always precede sampling

**Dataset flow:**
```
Raw data (2,084 balanced)
    ↓
Filter short articles (< 20 tokens)
    - Removed 18 articles total
    - Chinese: 12 removed
    - Western: 6 removed
    ↓
Re-balance (year-stratified sampling)
    ↓
Final dataset (2,054 articles, 1,027 per category)
```

---

## 13. Known Issues and Fixes

### TOKENIZERS_PARALLELISM Warning
**Error:** `huggingface/tokenizers: The current process just got forked, after parallelism has already been used. Disabling parallelism to avoid deadlocks...`

**Fix:** Added to notebook imports cell:
```python
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
```

### Processing Time Estimates
| Analysis | Time | Notes |
|----------|------|-------|
| VADER Sentiment | 10-30 sec | Lexicon-based lookup |
| BERT Sentiment | 20-40 min | Neural network on CPU |
| LDA Topic Modeling | 5-15 min | Tests multiple topic counts |
| Text Preprocessing | Pre-done | Tokens in balanced_preprocessed.pkl |

---

## 14. Final Pre-processed Dataset

**File:** `data/processed/balanced_preprocessed.pkl`

| Metric | Value |
|--------|-------|
| Total articles | 2,054 |
| Chinese State Media | 1,027 (50%) |
| Western Media | 1,027 (50%) |
| Minimum tokens | 20 |
| Average tokens | 674 |
| Pre-filtered | Yes |
| Pre-tokenized | Yes |
| Balance maintained | Yes |

---

## 15. Final Notebook Revision (December 2024)

### Changes Made to Colab Notebook

**Removed:**
- Word cloud visualizations (Cells 62, 63) - replaced with quantitative terminology analysis

**Updated Interpretation Cells:**
- Cell 16: Figure 1 interpretation with balanced dataset details
- Cell 32: Figure 2 VADER sentiment interpretation
- Cell 38: Figure 3 BERT sentiment interpretation
- Cell 44: Figure 4 temporal analysis interpretation
- Cell 49: Figure 5 topic model selection interpretation
- Cell 56: Figure 6 topic distribution interpretation
- Cell 59: Figure 7 temporal topic evolution interpretation
- Cell 65: Summary of empirical findings
- Cell 67: Discussion synthesis
- Cell 69: Conclusion

**Updated Code Cell Comments:**
- All code cells now have explanatory comments describing the purpose
- Comments written from researcher perspective (not "I/we will...")
- Each output is explained in context of the analysis

### Key Results from Colab Run

| Metric | Value |
|--------|-------|
| Total articles | 2,054 |
| Balanced split | 1,027 per category |
| VADER mean (Chinese) | 0.577 |
| VADER mean (Western) | 0.106 |
| H1 t-statistic | 15.00 |
| H1 Cohen's d | 0.66 (medium effect) |
| Optimal topics | 7 |
| H3 significant topics | 6/7 |

### All Three Hypotheses Supported
- **H1:** Chinese media significantly more positive (p < 0.001)
- **H2:** Distinctive terminology patterns confirmed
- **H3:** 6 of 7 topics show significant differences

---

*Last Updated: December 6, 2024*
*Session managed by Claude Code*
