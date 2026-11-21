"""Disclosure measures per group-year and their evolution, FY2016-FY2025.

Volume: cyber and AI sentences per 10,000 words; share of groups with at least one AI sentence.
Location: share of cyber (AI) sentences in each SFCR section; share inside C.5 Operational risk.
Specificity (own definition, per cyber or AI sentence): contains (i) a number other than a year or a section code,
  (ii) a named regulation or standard, (iii) a named function, role or body, (iv) a scenario, test or quantification
  term, (v) a named incident or event.
Stickiness: TF-IDF cosine similarity between a group's cyber (AI) text in year t and in t-1 (Brown & Tucker, 2011),
  raw and adjusted for length by subtracting the value predicted from the two log word counts.
Boilerplate: share of cyber (AI) words in sentences that contain a four-word phrase used by at least a quarter of the
  groups in the same year (adapted from Lang & Stice-Lawrence, 2015, whose threshold applies to a national sample).
Time profile: Poisson regression of cyber (AI) sentence counts on year effects with group effects and log words
  as offset; standard errors clustered by group.
Output: results_measures.json, data/group_year.csv
"""
import json, os, re, warnings, numpy as np, pandas as pd, statsmodels.api as sm
from sklearn.feature_extraction.text import TfidfVectorizer
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
S = pd.read_parquet(f"{HERE}/data/sentences.parquet"); R = pd.read_csv(f"{HERE}/data/reports.csv")
GROUPS = sorted(R.group.unique()); YEARS = list(range(2016, 2026))

NUM = re.compile(r"(?<![A-Za-z.])(?:€|EUR|USD|\$|£|GBP)?\s?\d[\d,.]*\s?(?:%|per cent|million|billion|bn|m)?(?![\d.])")
YEARLIKE = re.compile(r"^(?:19|20)\d{2}$")
REG = re.compile(r"\b(GDPR|DORA|NIS ?2?|AI Act|Solvency II|EIOPA|ISO ?27001|NIST|Regulation \(EU\)|Digital Operational Resilience Act|General Data Protection Regulation|Cyber Resilience Act)\b", re.I)
ROLE = re.compile(r"\b(CISO|Chief Information Security Officer|Chief Information Officer|Chief Technology Officer|Chief Data Officer|information security (?:officer|function|team)|security operations cent(?:er|re)|committee|board of directors|management board|supervisory board|audit committee|risk committee|second line|third line|internal audit)\b", re.I)
QUANT = re.compile(r"\b(scenario|stress test|stress-test|penetration test|red team|simulation|exercise|capital requirement|SCR|loss(?:es)? of|aggregate exposure|accumulation|probable maximum loss|PML|incidents? (?:in|during|occurred))\b", re.I)
EVENT = re.compile(r"\b(NotPetya|WannaCry|SolarWinds|Log4j|MOVEit|CrowdStrike|COVID|pandemic|Ukraine|Russia)\b", re.I)
def has_number(s):
    for m in NUM.finditer(s):
        t = re.sub(r"[^\d]", "", m.group(0))
        if t and not YEARLIKE.match(t) and not re.match(r"^[A-E]\.\d", s[max(0, m.start() - 2):m.end()]): return True
    return False

def spec(df):
    if not len(df): return {k: np.nan for k in ["number", "regulation", "role", "quant", "event", "any"]}
    f = pd.DataFrame({"number": df.sentence.apply(has_number), "regulation": df.sentence.str.contains(REG), "role": df.sentence.str.contains(ROLE),
                      "quant": df.sentence.str.contains(QUANT), "event": df.sentence.str.contains(EVENT)})
    f["any"] = f.any(axis=1); return f.mean().to_dict()

def four_grams(s): w = re.findall(r"[a-z]+", s.lower()); return {" ".join(w[i:i + 4]) for i in range(len(w) - 3)}

if __name__ == "__main__":
    out = {"n_reports": int(len(R)), "n_groups": int(R.group.nunique()), "sentences": int(len(S)), "words": int(S.words.sum()),
           "cyber_sentences": int(S.cyber.sum()), "ai_sentences": int(S.ai.sum())}
    gy = []
    for (g, y), d in S.groupby(["group", "year"]):
        row = {"group": g, "year": y, "words": int(d.words.sum()), "cyber": int(d.cyber.sum()), "ai": int(d.ai.sum())}
        row["cyber_per10k"] = 1e4 * row["cyber"] / row["words"]; row["ai_per10k"] = 1e4 * row["ai"] / row["words"]
        for k in ["cyber", "ai"]:
            dd = d[d[k]]; row[f"{k}_inC5"] = float((dd.subsection == "C.5").mean()) if len(dd) else np.nan
            row[f"{k}_inB"] = float((dd.section == "B").mean()) if len(dd) else np.nan
            row[f"{k}_text"] = " ".join(dd.sentence); row[f"{k}_textwords"] = int(dd.words.sum())
        gy.append(row)
    G = pd.DataFrame(gy)
    # stickiness
    for k in ["cyber", "ai"]:
        sims = []
        for g, d in G.sort_values("year").groupby("group"):
            d = d.reset_index(drop=True)
            for i in range(1, len(d)):
                a, b = d.loc[i - 1, f"{k}_text"], d.loc[i, f"{k}_text"]
                if d.loc[i - 1, "year"] != d.loc[i, "year"] - 1 or not a or not b: continue
                v = TfidfVectorizer(stop_words="english").fit([a, b]); X = v.transform([a, b])
                sims.append({"group": g, "year": int(d.loc[i, "year"]), "sim": float((X[0] @ X[1].T).toarray()[0, 0]),
                             "lw0": np.log(d.loc[i - 1, f"{k}_textwords"]), "lw1": np.log(d.loc[i, f"{k}_textwords"])})
        sm_ = pd.DataFrame(sims)
        if len(sm_) > 10:
            X = sm.add_constant(np.column_stack([sm_.lw0, sm_.lw1, sm_.lw0 ** 2, sm_.lw1 ** 2])); fit = sm.OLS(sm_.sim, X).fit()
            sm_["sim_adj"] = sm_.sim - fit.fittedvalues + sm_.sim.mean()
        G = G.merge(sm_[["group", "year", "sim"] + (["sim_adj"] if "sim_adj" in sm_ else [])].rename(columns={"sim": f"{k}_sticky", "sim_adj": f"{k}_sticky_adj"}), on=["group", "year"], how="left")
    # boilerplate
    for k in ["cyber", "ai"]:
        bp = {}
        for y, d in S[S[k]].groupby("year"):
            grams_by_group = d.groupby("group").sentence.apply(lambda ss: set().union(*[four_grams(s) for s in ss]))
            cnt = {}
            for gs in grams_by_group:
                for q in gs: cnt[q] = cnt.get(q, 0) + 1
            thr = max(2, int(np.ceil(0.25 * R[R.year == y].group.nunique()))); common = {q for q, c in cnt.items() if c >= thr}
            for g, dg in d.groupby("group"):
                flag = dg.sentence.apply(lambda s: bool(four_grams(s) & common)); bp[(g, y)] = float((dg.words * flag).sum() / dg.words.sum())
        G[f"{k}_boilerplate"] = [bp.get((g, y), np.nan) for g, y in zip(G.group, G.year)]
    # specificity by year
    out["specificity_by_year"] = {k: {int(y): spec(S[(S[k]) & (S.year == y)]) for y in YEARS} for k in ["cyber", "ai"]}
    out["specificity_all"] = {k: spec(S[S[k]]) for k in ["cyber", "ai"]}
    # yearly summaries
    yr = {}
    for y in YEARS:
        d = G[G.year == y]
        yr[y] = {"reports": int(len(d)), "groups_with_ai": int((d.ai > 0).sum()), "groups_with_cyber": int((d.cyber > 0).sum()),
                 "cyber_per10k_mean": float(d.cyber_per10k.mean()), "cyber_per10k_median": float(d.cyber_per10k.median()),
                 "ai_per10k_mean": float(d.ai_per10k.mean()), "cyber_sent_total": int(d.cyber.sum()), "ai_sent_total": int(d.ai.sum()),
                 "cyber_inC5": float(np.nanmean(d.cyber_inC5)), "cyber_inB": float(np.nanmean(d.cyber_inB)),
                 "ai_inC5": float(np.nanmean(d.ai_inC5)) if d.ai.sum() else None, "ai_inB": float(np.nanmean(d.ai_inB)) if d.ai.sum() else None,
                 "cyber_sticky": float(d.cyber_sticky.mean()) if "cyber_sticky" in d else None,
                 "cyber_sticky_adj": float(d.cyber_sticky_adj.mean()) if "cyber_sticky_adj" in d else None,
                 "cyber_boilerplate": float(d.cyber_boilerplate.mean()), "ai_boilerplate": float(d.ai_boilerplate.mean()) if d.ai.sum() else None,
                 "words_mean": float(d.words.mean())}
    out["by_year"] = yr
    # Poisson with group and year effects, offset log words, cluster by group
    for k in ["cyber", "ai"]:
        D = G.copy(); X = pd.get_dummies(D[["group"]].astype(str), drop_first=True).astype(float)
        Y = pd.get_dummies(D.year.astype(str), prefix="y").drop(columns="y_2016").astype(float)
        Xm = sm.add_constant(pd.concat([X, Y], axis=1))
        m = sm.GLM(D[k], Xm, family=sm.families.Poisson(), offset=np.log(D.words)).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(D.group)[0]})
        out[f"poisson_year_effects_{k}"] = {c[2:]: {"irr": float(np.exp(m.params[c])), "ci": [float(np.exp(m.conf_int().loc[c, 0])), float(np.exp(m.conf_int().loc[c, 1]))]} for c in Y.columns}
    # first year of AI disclosure per group and of generative-AI terms
    gen = S[S.sentence.str.contains(r"(?i:generative AI|large language model|ChatGPT)|\bGenAI\b|\bLLMs?\b", regex=True)]
    out["first_ai_year"] = {g: int(d[d.ai > 0].year.min()) if (d.ai > 0).any() else None for g, d in G.groupby("group")}
    out["first_genai_year"] = {g: int(d.year.min()) for g, d in gen.groupby("group")}
    out["ai_act_mentions_by_year"] = {int(y): int(S[(S.year == y) & S.sentence.str.contains(r"(?i:\bAI Act\b|Artificial Intelligence Act)", regex=True)].shape[0]) for y in YEARS}
    out["dora_mentions_by_year"] = {int(y): int(S[(S.year == y) & S.sentence.str.contains(r"(?i:\bDORA\b|Digital Operational Resilience)", regex=True)].shape[0]) for y in YEARS}
    out["reports_per_group"] = R.groupby("group").year.apply(lambda s: sorted(int(x) for x in s)).to_dict()
    # location shares, only from reports in which the C.5 heading was detected
    ok = set(map(tuple, R[R.c5_found][["group", "year"]].values)); Sx = S[[(g, y) in ok for g, y in zip(S.group, S.year)]]
    out["location_shares"] = {}; out["location_reports"] = int(len(ok))
    for k in ["cyber", "ai"]:
        d = Sx[Sx[k]].copy(); d["loc"] = d.section.where(d.subsection != "C.5", "C.5"); d.loc[(d.section == "C") & (d.subsection != "C.5"), "loc"] = "C other"
        out["location_shares"][k] = d["loc"].value_counts(normalize=True).round(4).to_dict()
        out["location_shares"][k + "_B_sub"] = d[d.section == "B"].subsection.value_counts().head(6).to_dict()
        out["location_shares"][k + "_n"] = int(len(d))
    G.drop(columns=[c for c in G.columns if c.endswith("_text")]).to_csv(f"{HERE}/data/group_year.csv", index=False)
    json.dump(out, open(f"{HERE}/results_measures.json", "w"), indent=1, default=str)
    for y in YEARS: print(y, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in yr[y].items()})
    print("first AI", out["first_ai_year"]); print("first GenAI", out["first_genai_year"]); print("AI Act", out["ai_act_mentions_by_year"]); print("DORA", out["dora_mentions_by_year"])
    print({k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in out["specificity_all"].items()})
