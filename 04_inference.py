"""Inference by group-level (cluster) bootstrap, 5,000 resamples of the 20 groups (Efron, 1979, applied to clusters).
Quantities: change in disclosure intensity (2022-2025 vs 2016-2019); specificity of cyber vs AI sentences and its
difference; share of cyber sentences in C.5 early vs late; year-to-year stickiness early vs late; share of groups
disclosing AI per year. Output: results_inference.json
"""
import json, os, re, importlib.util, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
spec_ = importlib.util.spec_from_file_location("m", f"{HERE}/02_measures.py"); M = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(M)
S = pd.read_parquet(f"{HERE}/data/sentences.parquet"); G = pd.read_csv(f"{HERE}/data/group_year.csv"); REP = pd.read_csv(f"{HERE}/data/reports.csv")
EARLY, LATE = range(2016, 2020), range(2022, 2026)
groups = sorted(G.group.unique()); rng = np.random.default_rng(2027); B = 5000
for k in ["cyber", "ai"]:
    f = S[S[k]].copy()
    f["specific"] = f.sentence.apply(M.has_number) | f.sentence.str.contains(M.REG) | f.sentence.str.contains(M.ROLE) | f.sentence.str.contains(M.QUANT) | f.sentence.str.contains(M.EVENT)
    S.loc[f.index, f"{k}_specific"] = f["specific"]
def stats(gs):
    g = G[G.group.isin(gs)] if gs is not None else G
    s = S[S.group.isin(gs)] if gs is not None else S
    out = {}
    for k in ["cyber", "ai"]:
        e = g[g.year.isin(EARLY)]; l = g[g.year.isin(LATE)]
        out[f"{k}_intensity_early"] = 1e4 * e[k].sum() / e.words.sum(); out[f"{k}_intensity_late"] = 1e4 * l[k].sum() / l.words.sum()
        out[f"{k}_intensity_ratio"] = out[f"{k}_intensity_late"] / out[f"{k}_intensity_early"] if out[f"{k}_intensity_early"] > 0 else np.nan
        sk = s[s[k]]; out[f"{k}_specific"] = float(sk[f"{k}_specific"].astype(bool).mean())
        out[f"{k}_specific_late"] = float(sk[sk.year.isin(LATE)][f"{k}_specific"].astype(bool).mean())
    okc5 = set(map(tuple, REP[REP.c5_found][["group", "year"]].values)); s5 = s[[(g_, y_) in okc5 for g_, y_ in zip(s.group, s.year)]]
    c = s5[s5.cyber]; out["cyber_inC5_early"] = float((c[c.year.isin(EARLY)].subsection == "C.5").mean()); out["cyber_inC5_late"] = float((c[c.year.isin(LATE)].subsection == "C.5").mean())
    out["cyber_sticky_early"] = float(g[g.year.isin(range(2017, 2020))].cyber_sticky.mean()); out["cyber_sticky_late"] = float(g[g.year.isin(LATE)].cyber_sticky.mean())
    out["specific_diff_cyber_minus_ai_late"] = out["cyber_specific_late"] - out["ai_specific_late"]
    return out
point = stats(None); boots = []
for _ in range(B):
    gs = list(rng.choice(groups, len(groups), replace=True))
    g = pd.concat([G[G.group == x].assign(_b=i) for i, x in enumerate(gs)]); s = pd.concat([S[S.group == x] for x in gs])
    Gs, Ss = G, S; globals()["G"], globals()["S"] = g, s
    try: boots.append(stats(None))
    finally: globals()["G"], globals()["S"] = Gs, Ss
Bd = pd.DataFrame(boots)
R = {k: {"est": float(v), "ci95": [float(Bd[k].quantile(0.025)), float(Bd[k].quantile(0.975))]} for k, v in point.items()}
R["n_groups"] = len(groups); R["B"] = B
Gs, Ss = G, S; G = Gs[Gs.group != "Hannover Re"]; S = Ss[Ss.group != "Hannover Re"]
R["without_hannover_re"] = {k: float(v) for k, v in stats(None).items()}; G, S = Gs, Ss
R["groups_disclosing_ai_by_year"] = {int(y): [int((d.ai > 0).sum()), int(len(d))] for y, d in G.groupby("year")}
json.dump(R, open(f"{HERE}/results_inference.json", "w"), indent=1)
for k, v in R.items():
    if isinstance(v, dict) and "est" in v: print(k, round(v["est"], 3), [round(x, 3) for x in v["ci95"]])
print(R["groups_disclosing_ai_by_year"])
