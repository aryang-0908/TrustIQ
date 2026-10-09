import re

with open("frontend/index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_catch = """      } catch (e) {
          alert("Error toggling proxy. Is the proxy server running?");
          console.error(e);
      }"""

new_catch = """      } catch (e) {
          alert("Error toggling proxy: " + e.message + "\\nCheck if https://vanguard-proxy-2026.loca.lt is accessible and bypass the reminder.");
          console.error(e);
      }"""

if old_catch in content:
    content = content.replace(old_catch, new_catch)
    with open("frontend/index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched index.html catch block.")
else:
    print("Could not find catch block.")

