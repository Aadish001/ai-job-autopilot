from dotenv import load_dotenv
load_dotenv()
import os

keys = ['GEMMA_API_KEY', 'RAPIDAPI_KEY', 'GOOGLE_SHEETS_CREDENTIALS', 'GOOGLE_SHEETS_ID']
for k in keys:
    val = os.environ.get(k)
    if val:
        print(f"{k}: SET ({val[:15]}...)")
    else:
        print(f"{k}: MISSING")

# Test pdflatex
import subprocess
try:
    result = subprocess.run(["pdflatex", "--version"], capture_output=True, text=True, timeout=10)
    print(f"\npdflatex: AVAILABLE ({result.stdout.split(chr(10))[0]})")
except FileNotFoundError:
    print("\npdflatex: NOT FOUND - You need to install MiKTeX or TeX Live")
except Exception as e:
    print(f"\npdflatex: ERROR ({e})")

print("\nAll checks complete.")
