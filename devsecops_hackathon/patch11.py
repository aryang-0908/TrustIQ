import os
import glob

old_url = "https://vanguard-proxy-2026.loca.lt"
new_url = "https://geography-scoring-drawings-timing.trycloudflare.com"

# Search in frontend directory and root
files = glob.glob("frontend/*.html") + ["vanguard.html", "practice_shop/checkout.html"]

for file in files:
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        
        if old_url in content:
            content = content.replace(old_url, new_url)
            with open(file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated {file}")

