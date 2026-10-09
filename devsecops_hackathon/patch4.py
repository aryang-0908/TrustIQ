import os, glob
urls = ['frontend/*.html', 'vanguard.html']
for p in urls:
 for f in glob.glob(p):
  content = open(f, 'r', encoding='utf-8').read()
  content = content.replace('https://17bb57ea1be181.lhr.life', 'https://vanguard-proxy-2026.loca.lt')
  open(f, 'w', encoding='utf-8').write(content)
