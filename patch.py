import os

filepath = r'c:\IEEE\devsecops_hackathon\frontend\index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

btn = """<button onclick="window.open('dashboard.html', '_blank')" class="px-5 py-2.5 bg-blue-500 text-obsidian-950 text-[10px] font-bold tracking-[0.2em] hover:bg-blue-400 transition-colors duration-300 shadow-[0_0_15px_rgba(59,130,246,0.4)] mr-4">
              LAUNCH LIVE GUARD DASHBOARD
            </button>\n            """

target = "INTEGRATE IN WEB APP"
idx = content.find(target)
if idx != -1:
    btn_start = content.rfind('<button', 0, idx)
    new_content = content[:btn_start] + btn + content[btn_start:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Injected successfully.")
else:
    print("Target not found.")

