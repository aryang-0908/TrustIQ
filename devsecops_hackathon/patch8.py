with open('vanguard.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("</script>\" })", "<\\/script>\" })")

with open('vanguard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed vanguard.html")

