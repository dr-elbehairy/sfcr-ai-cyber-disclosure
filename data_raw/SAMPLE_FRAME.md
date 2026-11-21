# Sample frame: group SFCRs, FY2016–FY2025

Paper 6: *Talking About AI and Cyber Risk: Disclosure and Governance Signals in European Insurers' Solvency and Financial Condition Reports, 2016–2025*
Inventory built 2026-11-21. Files: `sfcr_inventory.csv` (240 rows = 24 groups × 10 financial years), `pdf_checks/` (42 verification PDFs, at most two per group), `sources/` (HTML snapshots of the sample-frame sources).

## 1. Sample rule

**Rule:** the frame takes every company that STOXX assigns to the **Insurance supersector of the STOXX Europe 600** index as at 30 October 2026 (28 companies). From these it keeps the 24 companies domiciled or listed in the EEA or the UK, the jurisdictions where Solvency II applies (and Solvency UK in the UK from 31 Dec 2024). It drops the four Swiss constituents (Zurich, Swiss Re, Swiss Life, Helvetia), which report under the Swiss Solvency Test and publish no SFCR. A group stays in the frame even if it has no group SFCR for some or all years, and each such gap is recorded in the CSV with its reason, so the drop-outs can be traced.

We did not use EIOPA insurance statistics as the frame because they are country-level aggregates that do not name groups (https://www.eiopa.europa.eu/tools-and-data/insurance-statistics_en, HTTP 200 on 2026-11-21). We found no official, freely readable ranking of European groups by gross written premium.

## 2. Source and verbatim record

**Primary list:** Wikipedia, "STOXX Europe 600", revision 1385211866 ("This page was last edited on 12 November 2026, at 10:17"). URL https://en.wikipedia.org/wiki/STOXX_Europe_600, retrieved 2026-11-21. Snapshot: `sources/wikipedia_STOXX_Europe_600_rev1385211866_retrieved_2026-11-21.html`.

Verbatim from the section "Index components":

> "The following table lists the companies in the index as of 30 October 2026. With the quarterly review effective 21 September 2026, 14 companies were added, nine of them Greek, and 14 were removed. The list also reflects replacements following corporate actions up to 30 October 2026: Schroders, acquired by Nuveen, and Beazley, acquired by Zurich Insurance Group, both on 1 October 2026, left the index. … Country and supersector are as assigned by STOXX; ISINs are taken from the holdings of a fund tracking the index."

The table's own sources are "STOXX Europe 600 – Components", stoxx.com, retrieved 30 October 2026, and the holdings of an Xtrackers STOXX Europe 600 ETF. The section "Components by country and supersector" counts **Insurance = 28** companies.

**Cross-check against the index provider:** STOXX, "STOXX Europe 600 Insurance" (SXIP), https://www.stoxx.com/index-details?symbol=SXIP, retrieved 2026-11-21. Snapshot: `sources/stoxx_SXIP_index-details_retrieved_2026-11-21.html`. Without a login, the page shows only its "Top 10 Components": ALLIANZ (DE), ZURICH INSURANCE GROUP (CH), AXA (FR), MUENCHENER RUECK (DE), SWISS REINSURANCE COMPANY (CH), ASSICURAZIONI GENERALI (IT), SWISS LIFE HLDG (CH), PRUDENTIAL (GB), AVIVA (GB), SAMPO (FI). All ten appear in the Wikipedia list of 28. The full constituent list on stoxx.com could not be read without an account. **For citation in the paper:** cite STOXX as the index owner and the dated Wikipedia revision as the readable transcription. Before submission, replace the Wikipedia citation with a STOXX or ETF-issuer holdings file if one can be obtained.

**The 28 Insurance constituents (STOXX country):** Admiral Group (GB), Aegon (NL), Ageas (BE), Allianz (DE), ASR Nederland (NL), Assicurazioni Generali (IT), Aviva (GB), Axa (FR), Gjensidige (NO), Hannover Re (DE), *Helvetia (CH)*, Hiscox (GB), Legal & General (GB), Mapfre (ES), Munich Re (DE), NN Group (NL), PZU (PL), Prudential plc (GB), Sampo Group (FI), SCOR SE (FR), Standard Life plc (GB), Storebrand (NO), *Swiss Life (CH)*, *Swiss Re (CH)*, Talanx (DE), Tryg (DK), Unipol (IT), *Zurich Insurance Group (CH)*. The four in italics are excluded.

## 3. Coverage

| Measure | Count |
|---|---|
| Group-years in frame (24 × 10) | 240 |
| **ok** (official URL, HTTP 200/206 and `%PDF` header; all 196 re-checked independently on 2026-11-21) | **196** |
| blocked (403 / bot check; not worked around) | 18 (Admiral 10, Aegon 7, Ageas 1) |
| not_found | 26 |
| … of which no group SFCR exists by regime/structure | 25 (Hiscox 10, Prudential FY2019–25 7, Tryg FY2021–25 5, Aegon FY2023–25 3) |
| … of which a report probably exists but was not located | 1 (Mapfre FY2016) |
| Group-years where a group SFCR should exist | 215 |
| Retrieval rate on that base | 196 / 215 = 91.2% |
| Groups with a complete FY2016–FY2025 run (balanced panel) | 17 |

Countries with at least one ok group-year: DE 4, FR 2, IT 2, NL 2 (+Aegon blocked), BE 1, ES 1, PL 1, FI 1, DK 1, NO 2, UK 4 (Aviva, L&G, Prudential FY2016–18, Standard Life; +Admiral blocked; Hiscox none). Total 21 groups with at least one ok year.

**Language:** all 196 ok URLs point to English documents. A parallel local-language version exists for AXA, SCOR (FR), Generali, Unipol (IT; English is a convenience translation of the Italian original), Mapfre (ES prevails), PZU (PL), Talanx/HDI and Munich Re FY2020 (DE), Gjensidige and Storebrand (NO, most years), and Tryg (DA, 2017–2020). These local-language URLs are given in the notes. No group in the frame publishes only in a local language.

## 4. Points that affect the analysis

- **Survivorship and selection.** Index membership is fixed at 2026, so groups that left the index or were acquired before then are not in the frame (e.g. Beazley, Direct Line, CNP, Topdanmark). Austria, Ireland, Sweden and the large mutuals (e.g. Achmea, Groupama) are absent. A robustness extension could add the largest unlisted or non-index groups under a separate, stated rule.
- **Overlap.** Hannover Re's group SFCR is a *voluntary* publication. Hannover Re is a sub-group of the HDI Group, and Talanx's group SFCR is published as the **HDI Group** SFCR, with Talanx as its "risk kernel". Treat the two as nested, or drop one in pooled tests.
- **Single SFCRs** (a group report combined with solo entities): SCOR (Group + SCOR SE; FY2016–18 also two other solo entities), Ageas, Gjensidige, Aviva from FY2023, Legal & General from about FY2022, Standard Life/Phoenix FY2025. Document length and scope change at these switches.
- **Naming and regime changes.** UK groups are under Solvency UK from 31 Dec 2024 (FY2024 onward). The FY2025 covers checked for Aviva, L&G and Standard Life name no regime, and the text uses "Solvency UK". Phoenix Group Holdings plc became **Standard Life plc** on 24 Feb 2026 (stated in its FY2025 SFCR). Its FY2016 report is the Phoenix Life Holdings Ltd group SFCR, because the parent was then Cayman-registered. UnipolSai was merged into Unipol effective 31 Dec 2024 (parent renamed Unipol Assicurazioni). Aegon redomiciled to Bermuda on 30 Sep 2023, so its last Solvency II SFCR is FY2022 and it has published a BMA Group FCR since. Prudential plc's last group SFCR is FY2018; after the October 2019 M&G demerger the Hong Kong IA became group supervisor (this rests on search snippets of AR2019, not a full reading). Tryg lost group-SFCR approval after its 2021 rights issue, and from FY2021 it reports solo for Tryg Forsikring A/S. Hiscox is BMA-supervised and publishes a Bermuda FCR, not an SFCR.
- **First reports are thin.** Sampo FY2016 (25 pp) mainly refers readers to other disclosures. When building text measures, normalise by length.

## 5. Blockers (recorded, not circumvented)

- **Admiral Group:** Akamai returns 403 "Access Denied" on the IR page and the PDFs. No year could be verified.
- **Aegon:** an Incapsula bot-check page is served for every aegon.com page and PDF, and sec.gov refuses the generic user agent.
- **Ageas:** ageas.com HTML pages are behind a Cloudflare challenge. The FY2017–25 PDFs (ageas.com / img.ageas.com / Ageas's Contentful asset host) load, but the FY2016 PDF URL could not be found.
- **Allianz:** the SFCR listing page returns 403 to curl. Its links were read through a fetch tool, and the PDFs themselves download normally.
- **Tryg:** the FY2018 Danish PDF returns 403 (the English version is ok).

Resolving the Admiral and Aegon blocks needs a manual browser download by the author, or a request to IR.

## 6. Reproducibility

URLs were checked with plain `curl` (generic UA `Mozilla/5.0 (compatible; research-client/1.0)`, normal TLS verification). Each row's `notes` gives the listing page the URL came from, any alternate-language URL, and how the row was verified. Page counts are from pypdf and pdfinfo. Some URLs were found through search engines or the Wayback CDX index and then confirmed live on the official domain (no archived copies were used); these are flagged in the notes. For most groups, document *content* was read only for the two downloaded years, so scope and language for the other years rest on titles and listings.
