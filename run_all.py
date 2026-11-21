"""Reproduce every result: python run_all.py. Downloads the SFCRs from the groups' websites (some may refuse automated
access or move; check data_raw/sfcr_downloads.csv for SHA-256 of the files used in the paper), then runs the pipeline."""
import subprocess, sys, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
for s in ["00_download_sfcr.py", "01_extract.py", "02_measures.py", "03_validation.py", "04_inference.py", "05_figures.py", "06_groups.py"]:
    print(">>", s, flush=True); subprocess.run([sys.executable, s], check=True)
for f in os.listdir(HERE):
    if f.startswith("results_") and f.endswith(".json"): shutil.copy(f, os.path.join("results", f))
