"""Group-level heterogeneity and illustrative sentences.
- Per group: reports, words per report, cyber and AI sentences per 10,000 words, share of specific cyber sentences,
  mean year-to-year stickiness, and cross-referencing intensity (sentences pointing the reader to the annual report /
  universal registration document, per 10,000 words), which measures disclosure by reference (Directive Art. 51(1)).
- Illustrative sentences: validated sentences on which both coders agree, two per depth/type, drawn with a fixed seed.
Output: results_groups.json
"""
import json, os, re, importlib.util, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("m", f"{HERE}/02_measures.py"); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
S = pd.read_parquet(f"{HERE}/data/sentences.parquet"); NZ = {}
def nz(t): t = str(t).replace("\u00ad ", "").replace("\u00ad", ""); t = re.sub(r"\s+", " ", t); return re.sub(r"(\w)- (\w)", r"\1-\2", t).strip()
G = pd.read_csv(f"{HERE}/data/group_year.csv")
XREF = re.compile(r"(?:Universal Registration Document|Annual Report|Annual Financial Report|Integrated (?:Annual )?Report|Annual Review)[^.]{0,80}(?:refer|see|available|not duplicated|incorporated|included)|(?:refer|see|incorporated by reference|included by reference)[^.]{0,80}(?:Universal Registration Document|Annual Report|Annual Financial Report|Integrated (?:Annual )?Report)", re.I)
S["xref"] = S.sentence.str.contains(XREF)
c = S[S.cyber].copy(); c["spec"] = c.sentence.apply(M.has_number) | c.sentence.str.contains(M.REG) | c.sentence.str.contains(M.ROLE) | c.sentence.str.contains(M.QUANT) | c.sentence.str.contains(M.EVENT)
rows = []
for g, d in S.groupby("group"):
    gy = G[G.group == g]; w = d.words.sum()
    rows.append({"group": g, "reports": int(gy.year.nunique()), "words_per_report": float(w / gy.year.nunique()),
                 "cyber_per10k": float(1e4 * d.cyber.sum() / w), "ai_per10k": float(1e4 * d.ai.sum() / w),
                 "cyber_specific": float(c[c.group == g].spec.mean()) if (c.group == g).any() else None,
                 "sticky": float(gy.cyber_sticky.mean()) if gy.cyber_sticky.notna().any() else None,
                 "xref_per10k": float(1e4 * d.xref.sum() / w), "years_with_ai": int((gy.ai > 0).sum())})
T = pd.DataFrame(rows).sort_values("cyber_per10k", ascending=False)
q = T.xref_per10k.median()
R = {"groups": T.to_dict("records"), "xref_median": float(q),
     "cyber_per10k_high_xref": float(T[T.xref_per10k > q].cyber_per10k.median()), "cyber_per10k_low_xref": float(T[T.xref_per10k <= q].cyber_per10k.median()),
     "words_high_xref": float(T[T.xref_per10k > q].words_per_report.median()), "words_low_xref": float(T[T.xref_per10k <= q].words_per_report.median()),
     "groups_no_cyber": T[T.cyber_per10k == 0].group.tolist(), "groups_no_ai": T[T.ai_per10k == 0].group.tolist(),
     "range_cyber_per10k": [float(T.cyber_per10k.min()), float(T.cyber_per10k.max())]}
K = pd.read_csv(f"{HERE}/validation/validation_key.csv"); A = pd.read_csv(f"{HERE}/validation/coder_A.csv"); B = pd.read_csv(f"{HERE}/validation/coder_B.csv")
D = K.merge(A, on="id").merge(B, on="id", suffixes=("_A", "_B")); D["sentence"] = D.sentence.map(nz)
Sx = S.set_index("sentence")[["section", "subsection"]]; Sx = Sx[~Sx.index.duplicated()]
D = D[D.sentence.isin(Sx.index) & ~D.sentence.str.contains("■|•|\u00ad|\u2010|[\uf000-\uf8ff]|shall prevail") & D.sentence.str.match(r"^[A-Z]")]  # clean, complete sentences only
D["section"] = Sx.loc[D.sentence, "section"].values; D["subsection"] = Sx.loc[D.sentence, "subsection"].values
ex = {}
for col, cats in [("cyber_depth", ["mention", "governance", "quantified"]), ("ai_type", ["use", "risk_governance", "regulation"])]:
    for cat in cats:
        x = D[(D[f"{col}_A"] == cat) & (D[f"{col}_B"] == cat) & (D.sentence.str.split().str.len().between(12, 60))].sample(frac=1, random_state=7).head(2)
        ex[f"{col}:{cat}"] = [{"group": r.group, "year": int(r.year), "section": r.subsection if isinstance(r.subsection, str) else r.section, "sentence": r.sentence} for _, r in x.iterrows()]
R["examples"] = ex
json.dump(R, open(f"{HERE}/results_groups.json", "w"), indent=1, default=str)
print(T.round(3).to_string()); print({k: v for k, v in R.items() if k not in ["groups", "examples"]})
for k, v in ex.items():
    for e in v: print(k, "|", e["group"], e["year"], e["section"], "|", e["sentence"][:230])
