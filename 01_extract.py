"""Extract text from every downloaded SFCR, split it into sentences, assign each sentence to an SFCR section
(Summary, A to E; C.5 operational risk tracked separately) and flag cyber and AI sentences with the dictionaries below.
Output: data/sentences.parquet (one row per sentence), data/reports.csv (one row per report).
"""
import csv, json, os, re, sys, numpy as np, pandas as pd, fitz
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = f"{HERE}/data_raw"; OUT = f"{HERE}/data"; os.makedirs(OUT, exist_ok=True)

# ---- dictionaries (word-boundary regexes, case-insensitive unless stated) -------------------------------
CYBER = [r"cyber[\s-]?(?:attack|attacks|crime|criminals?|security|risk|risks|threat|threats|incident|incidents|insurance|resilience|event|events)?",
         r"information security", r"IT security", r"ICT (?:risk|risks|security|incident|incidents)", r"data breach(?:es)?", r"ransomware",
         r"malware", r"phishing", r"hack(?:ing|ers?|ed)", r"network security", r"digital operational resilience", r"\bDORA\b",
         r"denial[- ]of[- ]service", r"information and communication technology risk", r"NotPetya", r"WannaCry"]
AI = [r"artificial intelligence", r"machine[- ]learning", r"deep learning", r"neural networks?", r"generative AI", r"\bGenAI\b",
      r"large language models?", r"\bLLMs?\b", r"ChatGPT", r"AI Act", r"natural language processing", r"\bAI\b"]
CASE_SENSITIVE = {r"\bAI\b", r"\bGenAI\b", r"\bLLMs?\b", r"\bDORA\b", r"IT security"}
def compile_dict(lst):
    return [re.compile(p if p.startswith(r"\b") else r"\b" + p + r"\b", 0 if p in CASE_SENSITIVE else re.I) for p in lst]
CY, AIr = compile_dict(CYBER), compile_dict(AI)

QRT = re.compile(r"\bS\.\d{2}\.\d{2}\.\d{2}\b")
LEI = re.compile(r"\b[0-9A-Z]{18}[0-9]{2}\b")
ENTITY_LIST = re.compile(r"Non-\s?mutual|Ancillary services undertaking|Undertakings in the scope of the group|Identification code of the undertaking", re.I)
TITLES = {"business and performance": "A", "system of governance": "B", "risk profile": "C",
          "valuation for solvency purposes": "D", "capital management": "E"}
TOP = re.compile(r"^\s*(?:section\s+)?([a-e])[.:)]?\s+(business and performance|system of governance|risk profile|valuation for solvency purposes|capital management)\s*$", re.I)
SUB = re.compile(r"^\s*([A-E])\.(\d{1,2})\.?\s+([A-Z][A-Za-z ,&\-–’'()/]{2,90})$")
CODE_ONLY = re.compile(r"^\s*([A-E])(?:\.(\d{1,2}))?\.?\s*$")
SUMMARY_RE = re.compile(r"^\s*(?:Executive\s+)?Summary\s*$", re.I)
ANNEX_RE = re.compile(r"^\s*(Annex(?:es)?|Appendix|Appendices|Quantitative reporting templates|Public QRTs?|QRTs?)\b[^.]{0,60}$", re.I)
def norm(l): return re.sub(r"[^a-z ]", "", l.lower()).strip()
def title_section(l): return TITLES.get(norm(l))

def split_sentences(t):
    t = t.replace("\u00ad ", "").replace("\u00ad", "")
    t = re.sub(r"\s+", " ", t); t = re.sub(r"(\w)- (\w)", r"\1-\2", t)
    out = []
    for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", t):
        s = s.strip(); w = s.split()
        if len(w) < 4 or len(w) > 150: continue
        if sum(ch.isdigit() for ch in s) / max(len(s), 1) > 0.25: continue      # table residue
        if LEI.search(s) or ENTITY_LIST.search(s): continue                     # group-scope undertaking lists
        out.append(s)
    return out

def process(path):
    doc = fitz.open(path); pages = []; toc_pages = set(); qrt_pages = set()
    for pno, page in enumerate(doc):
        ptxt = page.get_text("text"); lines = ptxt.splitlines()
        if sum(1 for l in lines if re.search(r"\.{5,}\s*\d+\s*$", l)) >= 5: toc_pages.add(pno); continue
        if QRT.search("\n".join(lines[:4])) or (QRT.search(ptxt) and sum(ch.isdigit() for ch in ptxt) / max(len(ptxt), 1) > 0.15):
            qrt_pages.add(pno); continue
        pages.append((pno, lines))
    # running headers, footers and navigation bars: short lines repeated on many pages
    freq = {}
    for _, lines in pages:
        for l in set(x.strip() for x in lines if 0 < len(x.strip()) < 80): freq[l] = freq.get(l, 0) + 1
    thr = max(3, 0.3 * len(pages)); repeated = {l for l, c_ in freq.items() if c_ >= thr}
    sec, sub = "front", None; rows = []
    for pno, lines in pages:
        lines = [l for l in lines if l.strip() not in repeated]
        buf = []; pending = None
        def flush():
            nonlocal buf
            if buf: rows.extend((pno, sec, sub, s_) for s_ in split_sentences(" ".join(buf))); buf = []
        for l in lines:
            st = l.strip()
            if SUMMARY_RE.match(st) and sec == "front": flush(); sec, sub = "S", None; continue
            if sec in ("D", "E") and ANNEX_RE.match(st): flush(); sec, sub = "annex", None; continue
            m = TOP.match(st); ts = title_section(st) if len(st) < 45 else None
            if m: flush(); sec, sub = m.group(1).upper(), None; pending = None; continue
            if ts: flush(); sec, sub = ts, None; pending = None; continue
            m2 = SUB.match(st)
            if m2 and len(st) < 100:
                flush(); sec = m2.group(1); title = m2.group(3).lower()
                sub = "C.5" if (sec == "C" and "operational" in title) else f"{sec}.{m2.group(2)}" + ("" if sec != "C" else "x")
                pending = None; continue
            c = CODE_ONLY.match(st)
            if c and c.group(2): pending = (c.group(1), c.group(2)); continue
            if pending and st:
                if re.match(r"^[A-Z][A-Za-z ,&\-–’'()/]{2,90}$", st):
                    flush(); sec = pending[0]; title = st.lower()
                    sub = "C.5" if (sec == "C" and "operational" in title) else f"{sec}.{pending[1]}" + ("" if sec != "C" else "x")
                    pending = None; continue
                pending = None
            if sec == "C" and re.fullmatch(r"\s*operational risks?\s*", st, re.I): flush(); sub = "C.5"; continue
            buf.append(l)
        flush()
    return rows, doc.page_count, len(toc_pages), len(qrt_pages)

if __name__ == "__main__":
    inv = pd.read_csv(f"{RAW}/sfcr_downloads.csv"); inv = inv[inv.ok]
    allrows = []; rep = []
    for _, r in inv.iterrows():
        rows, npages, ntoc, nqrt = process(f"{RAW}/sfcr/{r.file}")
        df = pd.DataFrame(rows, columns=["page", "section", "subsection", "sentence"]); df["group"] = r.group; df["year"] = int(r.year)
        df["cyber"] = df.sentence.apply(lambda s: any(p.search(s) for p in CY)); df["ai"] = df.sentence.apply(lambda s: any(p.search(s) for p in AIr))
        df["words"] = df.sentence.str.split().str.len()
        allrows.append(df)
        secs = df.groupby("section").words.sum().to_dict()
        rep.append({"group": r.group, "year": int(r.year), "pages": npages, "toc_pages": ntoc, "qrt_pages": nqrt, "sentences": len(df), "words": int(df.words.sum()),
                    "cyber_sent": int(df.cyber.sum()), "ai_sent": int(df.ai.sum()), "share_words_front": secs.get("front", 0) / max(df.words.sum(), 1),
                    "sections_found": "".join(sorted(k for k in secs if k in "SABCDE")), "annex_words": int(secs.get("annex", 0)), "c5_found": bool((df.subsection == "C.5").any())})
        print(r.group, r.year, len(df), int(df.cyber.sum()), int(df.ai.sum()), rep[-1]["sections_found"], rep[-1]["c5_found"], flush=True)
    S = pd.concat(allrows, ignore_index=True); S.to_parquet(f"{OUT}/sentences.parquet"); pd.DataFrame(rep).to_csv(f"{OUT}/reports.csv", index=False)
    print("sentences", len(S), "cyber", int(S.cyber.sum()), "ai", int(S.ai.sum()))
