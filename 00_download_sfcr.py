"""Download every SFCR marked 'ok' in data_raw/sfcr_inventory.csv into data_raw/sfcr/<group>_<year>.pdf.
Sequential, 2-second pause, generic User-Agent, normal TLS. Records size and SHA-256 in data_raw/sfcr_downloads.csv."""
import csv, hashlib, os, re, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = f"{HERE}/data_raw"; OUT = f"{RAW}/sfcr"; os.makedirs(OUT, exist_ok=True)
rows = [r for r in csv.DictReader(open(f"{RAW}/sfcr_inventory.csv")) if r["status"] == "ok"]
log = []
for r in rows:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", r["group"]).strip("_"); dst = f"{OUT}/{slug}_{r['year']}.pdf"
    if not os.path.exists(dst) or os.path.getsize(dst) < 10000:
        subprocess.run(["curl", "-sSL", "-m", "300", "-o", dst, r["url"]], check=False)
        time.sleep(2)
    ok = os.path.exists(dst) and open(dst, "rb").read(5) == b"%PDF-"
    h = hashlib.sha256(open(dst, "rb").read()).hexdigest() if ok else ""
    log.append({"group": r["group"], "year": r["year"], "file": os.path.basename(dst), "ok": ok, "bytes": os.path.getsize(dst) if os.path.exists(dst) else 0, "sha256": h, "url": r["url"]})
    print(r["group"], r["year"], ok, flush=True)
with open(f"{RAW}/sfcr_downloads.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(log[0].keys())); w.writeheader(); w.writerows(log)
print("ok", sum(x["ok"] for x in log), "of", len(log))
