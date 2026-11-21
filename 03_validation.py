"""Dictionary validation from two independent coders.
Sample (drawn before the annex filter): 200 cyber hits, all AI hits, 300 unflagged sentences from sections B and C;
exact duplicates removed. Only sentences that survive the final extraction (annex pages and table residue removed)
are evaluated. Agreement: percent agreement and Cohen's kappa computed directly from the 2x2 table.
Disagreements are resolved conservatively: a sentence counts as relevant only if both coders say so.
Precision = share of dictionary hits judged relevant; miss rate = share of unflagged B/C sentences judged relevant.
Output: results_validation.json
"""
import json, os, re, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); V = f"{HERE}/validation"
K = pd.read_csv(f"{V}/validation_key.csv"); A = pd.read_csv(f"{V}/coder_A.csv"); B = pd.read_csv(f"{V}/coder_B.csv")
def nz(t): t = str(t).replace("\u00ad ", "").replace("\u00ad", ""); t = re.sub(r"\s+", " ", t); return re.sub(r"(\w)- (\w)", r"\1-\2", t).strip()
S = pd.read_parquet(f"{HERE}/data/sentences.parquet"); keep = set(S.sentence.map(nz))
D = K.merge(A, on="id").merge(B, on="id", suffixes=("_A", "_B")); D["kept"] = D.sentence.map(nz).isin(keep)
def kappa(a, b):
    a = np.asarray(a); b = np.asarray(b); po = (a == b).mean(); pa = a.mean(); pb = b.mean(); pe = pa * pb + (1 - pa) * (1 - pb)
    return float(po), float((po - pe) / (1 - pe)) if pe < 1 else float("nan")
R = {"n_sample": int(len(D)), "sample_by_stratum": D.stratum.value_counts().to_dict(), "agreement_all_items": float(((D.cyber_A == D.cyber_B) & (D.ai_A == D.ai_B)).mean()), "n_kept": int(D.kept.sum()), "by_stratum_kept": D[D.kept].stratum.value_counts().to_dict()}
E = D[D.kept]
for k in ["cyber", "ai"]:
    po, kp = kappa(E[f"{k}_A"], E[f"{k}_B"]); R[f"{k}_agreement"] = po; R[f"{k}_kappa"] = kp
    both = (E[f"{k}_A"] == 1) & (E[f"{k}_B"] == 1); either = (E[f"{k}_A"] == 1) | (E[f"{k}_B"] == 1)
    hit = E.stratum == f"{k}_hit"; neg = E.stratum == "unflagged_BC"
    R[f"{k}_precision_both"] = float(both[hit].mean()); R[f"{k}_precision_either"] = float(either[hit].mean()); R[f"{k}_n_hits"] = int(hit.sum())
    R[f"{k}_miss_rate_both"] = float(both[neg].mean()); R[f"{k}_miss_rate_either"] = float(either[neg].mean()); R["n_unflagged"] = int(neg.sum())
    R[f"{k}_missed_examples"] = E[neg & either].sentence.str[:200].tolist()[:8]
    R[f"{k}_false_positive_examples"] = E[hit & ~either].sentence.str[:200].tolist()[:8]
# depth and type among agreed relevant sentences (use coder A's category where both agree on relevance and category)
for k, col in [("cyber", "cyber_depth"), ("ai", "ai_type")]:
    rel = E[(E[f"{k}_A"] == 1) & (E[f"{k}_B"] == 1) & (E.stratum == f"{k}_hit")]
    R[f"{col}_agreement"] = float((rel[f"{col}_A"] == rel[f"{col}_B"]).mean())
    agreed = rel[rel[f"{col}_A"] == rel[f"{col}_B"]]
    R[f"{col}_distribution_agreed"] = agreed[f"{col}_A"].value_counts().to_dict()
    R[f"{col}_by_year_agreed"] = agreed.groupby(["year", f"{col}_A"]).size().unstack(fill_value=0).to_dict(orient="index")
# AI precision before vs after annex filter (shows why the filter matters)
hitall = D.stratum == "ai_hit"; R["ai_precision_both_before_filter"] = float(((D.ai_A == 1) & (D.ai_B == 1))[hitall].mean())
json.dump(R, open(f"{HERE}/results_validation.json", "w"), indent=1, default=str)
print({k: v for k, v in R.items() if not isinstance(v, (list, dict))})
print(R["cyber_depth_distribution_agreed"], R["ai_type_distribution_agreed"])
