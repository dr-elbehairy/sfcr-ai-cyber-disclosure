"""Figures for paper 6. Output: ../figures/fig1..fig4 (.png, 300 dpi)."""
import json, os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, "figures") if os.path.exists(os.path.join(HERE, "run_all.py")) else os.path.join(os.path.dirname(HERE), "figures")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
NAVY, PETROL, GOLD, GREY = "#1C4076", "#007A88", "#B8860B", "#8C8C8C"
M = json.load(open(f"{HERE}/results_measures.json")); V = json.load(open(f"{HERE}/results_validation.json")); G = pd.read_csv(f"{HERE}/data/group_year.csv")
YRS = list(range(2016, 2026)); by = M["by_year"]

fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
ax[0].plot(YRS, [by[str(y)]["cyber_per10k_mean"] for y in YRS], "o-", color=NAVY, ms=3, label="Cyber")
ax[0].plot(YRS, [by[str(y)]["ai_per10k_mean"] for y in YRS], "s-", color=GOLD, ms=3, label="AI")
ax[0].set_title("(a) Sentences per 10,000 words", loc="left"); ax[0].legend(frameon=False)
ax[1].bar(YRS, [by[str(y)]["groups_with_ai"] / by[str(y)]["reports"] for y in YRS], color=GOLD, label="AI")
ax[1].plot(YRS, [by[str(y)]["groups_with_cyber"] / by[str(y)]["reports"] for y in YRS], "o-", color=NAVY, ms=3, label="Cyber")
ax[1].set_ylim(0, 1); ax[1].set_title("(b) Share of groups disclosing", loc="left"); ax[1].legend(frameon=False)
for a in ax: a.set_xticks([2016, 2018, 2020, 2022, 2024])
fig.tight_layout(); fig.savefig(f"{FIG}/fig1_volume.png", dpi=300); plt.close(fig)

fig, ax = plt.subplots(figsize=(4.8, 2.8))
ax.plot(YRS, [M["dora_mentions_by_year"][str(y)] for y in YRS], "o-", color=NAVY, ms=3, label="DORA")
ax.plot(YRS, [M["ai_act_mentions_by_year"][str(y)] for y in YRS], "s-", color=GOLD, ms=3, label="AI Act")
ax.set_ylabel("Sentences (all groups)"); ax.legend(frameon=False); ax.set_xticks([2016, 2018, 2020, 2022, 2024])
fig.tight_layout(); fig.savefig(f"{FIG}/fig2_regulation_mentions.png", dpi=300); plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
cats = ["mention", "governance", "quantified", "product"]; d = V["cyber_depth_distribution_agreed"]
ax[0].barh(cats, [d.get(c, 0) for c in cats], color=NAVY); ax[0].set_title("(a) Cyber sentences by depth", loc="left"); ax[0].invert_yaxis()
cats2 = ["use", "risk_governance", "regulation", "other"]; d2 = V["ai_type_distribution_agreed"]
ax[1].barh(["Use", "Risk/governance", "Regulation", "Other"], [d2.get(c, 0) for c in cats2], color=GOLD); ax[1].set_title("(b) AI sentences by type", loc="left"); ax[1].invert_yaxis()
for a in ax: a.set_xlabel("Validated sentences (both coders agree)")
fig.tight_layout(); fig.savefig(f"{FIG}/fig3_depth_type.png", dpi=300); plt.close(fig)

fig, ax = plt.subplots(figsize=(4.8, 2.8))
sp = M["specificity_by_year"]
ax.plot(YRS, [sp["cyber"][str(y)]["any"] for y in YRS], "o-", color=NAVY, ms=3, label="Cyber")
ax.plot(YRS, [sp["ai"][str(y)]["any"] if by[str(y)]["ai_sent_total"] >= 10 else np.nan for y in YRS], "s-", color=GOLD, ms=3, label="AI (years with ≥ 10 sentences)")
ax.set_ylim(0, 1); ax.set_ylabel("Share of sentences with a specific element"); ax.legend(frameon=False, fontsize=7); ax.set_xticks([2016, 2018, 2020, 2022, 2024])
fig.tight_layout(); fig.savefig(f"{FIG}/fig4_specificity.png", dpi=300); plt.close(fig)
print("figures written to", FIG)
