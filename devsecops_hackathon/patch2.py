import re
with open('vanguard.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'modal\.innerHTML =\s+<div class=\"bg-black(.*?)<div class=\"mt-6 flex justify-end\">\s+<button onclick=\"document\.getElementById\(\'hacked-modal\'\)\.remove\(\)\" class=\"bg-red-600 hover:bg-red-700 text-white font-mono px-6 py-2 rounded transition\">SHUT DOWN TERMINAL<\/button>\s+<\/div>\s+<\/div>\s+\\\;',
    r'modal.innerHTML = <div class=\"bg-black\g<1><div class=\"mt-6 flex justify-end\">\n<button onclick=\"document.getElementById(\'hacked-modal\').remove()\" class=\"bg-red-600 hover:bg-red-700 text-white font-mono px-6 py-2 rounded transition\">SHUT DOWN TERMINAL</button>\n</div>\n</div>;',
    content,
    flags=re.DOTALL
)

with open('vanguard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patched vanguard.html successfully!')
