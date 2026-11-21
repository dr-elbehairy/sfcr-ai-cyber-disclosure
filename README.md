# Cyber and AI disclosure in European insurers' SFCRs, 2016–2025

Replication code and data for:

> Elbehairy, M. (2026). *Talking About AI and Cyber Risk: Disclosure and Governance Signals in European Insurers' Solvency and Financial Condition Reports, 2016–2025.* Manuscript under review.

The study text-mines 186 group Solvency and Financial Condition Reports (SFCRs) of 20 insurance groups in the STOXX Europe 600 Insurance index for financial years 2016 to 2025. It measures the volume, location, specificity, year-to-year stickiness and boilerplate of sentences about cyber risk and artificial intelligence, and how they respond to DORA and the EU AI Act.

## Contents

| Path | What it is |
|---|---|
| `00_download_sfcr.py` | Downloads the SFCRs listed in `data_raw/sfcr_inventory.csv` (plain HTTP client, 2 s pause) and logs status and SHA-256 to `data_raw/sfcr_downloads.csv` |
| `01_extract.py` | PDF text extraction (PyMuPDF), removal of tables of contents, template pages and running headers, sentence splitting, section detection by the Annex XX headings, cyber and AI dictionaries |
| `02_measures.py` | Volume, location, specificity, stickiness, boilerplate, DORA and AI Act counts, Poisson regressions with group and year effects |
| `03_validation.py` | Dictionary precision and miss rate from two independent coders, Cohen's kappa |
| `04_inference.py` | Group cluster bootstrap (5,000 resamples) for period contrasts and shares; robustness without Hannover Re |
| `05_figures.py` | Figures 1 to 4 |
| `06_groups.py` | Group table (Table 4), cross-referencing intensity and illustrative sentences |
| `run_all.py` | Runs everything in order |
| `data_raw/` | Sample frame (`SAMPLE_FRAME.md`), report inventory with URLs, download log with SHA-256 of every file used |
| `validation/` | Validation sample (`to_code.csv`), sampling strata (`validation_key.csv`), the codebook given to both coders (`CODEBOOK.md`) and both coders' answers |
| `derived/` | Report-level and group-year measures produced by the pipeline |
| `results/` | All numbers reported in the paper, as JSON |
| `figures/` | Figures as used in the paper |

## Reproducing

```
pip install -r requirements.txt
python run_all.py
```

Python 3.11 and scikit-learn 1.3 were used. The SFCRs themselves are not redistributed: they are the groups' publications. `00_download_sfcr.py` fetches them again from the groups' websites. Websites change and some refuse automated access, so a re-download may differ; compare the SHA-256 values in `data_raw/sfcr_downloads.csv` with your files. Allianz, Admiral and Aegon were excluded because their websites refused automated downloads; access controls were not circumvented.

## Note on the validation coders

The two coders whose judgements are in `validation/coder_A.csv` and `validation/coder_B.csv` were two independent instances of a large language model (Claude, Anthropic) given the same written codebook. No human coder was used. This is disclosed in the paper as a limitation.

## Licence

Code: MIT (see `LICENSE`). Validation sentences are short quotations from public reports, included for verification only.
