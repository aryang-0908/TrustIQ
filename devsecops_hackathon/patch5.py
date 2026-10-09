import re

with open("frontend/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add the CONNECT TO NOVA button
aegis_header_old = """      <div class="flex items-center gap-4 shrink-0" data-reveal data-delay="220">
          <button class="px-6 py-3 bg-neutral-100 text-obsidian-950 text-xs font-medium tracking-widest hover:bg-white transition-colors duration-300 hidden md:block">
            GENERATE EPHEMERAL KEY
          </button>
          <button onclick="openDeployModal()" class="px-6 py-3 bg-amber-500 text-obsidian-950 text-[11px] font-bold tracking-[0.2em] hover:bg-amber-400 transition-colors duration-300 shadow-[0_0_15px_rgba(245,158,11,0.4)]">
            DEPLOY IN WEB APP
          </button>
        </div>"""

aegis_header_new = """      <div class="flex items-center gap-4 shrink-0" data-reveal data-delay="220">
          <button id="aegisProxyBtn" onclick="toggleProxy()" class="px-6 py-3 bg-red-500 text-white text-[11px] font-bold tracking-[0.2em] hover:bg-red-400 transition-colors duration-300 shadow-[0_0_15px_rgba(239,68,68,0.4)]">
            CONNECT TO NOVA
          </button>
          <button class="px-6 py-3 bg-neutral-100 text-obsidian-950 text-xs font-medium tracking-widest hover:bg-white transition-colors duration-300 hidden md:block">
            GENERATE EPHEMERAL KEY
          </button>
          <button onclick="openDeployModal()" class="px-6 py-3 bg-amber-500 text-obsidian-950 text-[11px] font-bold tracking-[0.2em] hover:bg-amber-400 transition-colors duration-300 shadow-[0_0_15px_rgba(245,158,11,0.4)]">
            DEPLOY IN WEB APP
          </button>
        </div>"""

if aegis_header_old in content:
    content = content.replace(aegis_header_old, aegis_header_new)
    print("Replaced Aegis header successfully.")
else:
    print("Could not find Aegis header old string.")

# 2. Add the toggleProxy function before </body>
proxy_script = """
  let proxyActive = false;
  async function toggleProxy() {
      const btn = document.getElementById('aegisProxyBtn');
      try {
          const res = await fetch('https://vanguard-proxy-2026.loca.lt/dashboard/toggle_proxy', {
              method: 'POST'
          });
          const data = await res.json();
          proxyActive = data.proxy_active;
          
          if (proxyActive) {
              btn.textContent = 'DISCONNECT FROM NOVA';
              btn.classList.remove('bg-red-500', 'hover:bg-red-400', 'shadow-[0_0_15px_rgba(239,68,68,0.4)]');
              btn.classList.add('bg-emerald-500', 'hover:bg-emerald-400', 'shadow-[0_0_15px_rgba(16,185,129,0.4)]');
          } else {
              btn.textContent = 'CONNECT TO NOVA';
              btn.classList.remove('bg-emerald-500', 'hover:bg-emerald-400', 'shadow-[0_0_15px_rgba(16,185,129,0.4)]');
              btn.classList.add('bg-red-500', 'hover:bg-red-400', 'shadow-[0_0_15px_rgba(239,68,68,0.4)]');
          }
      } catch (e) {
          alert("Error toggling proxy. Is the proxy server running?");
          console.error(e);
      }
  }

  // Fetch initial state
  async function initProxyState() {
      try {
          const res = await fetch('https://vanguard-proxy-2026.loca.lt/dashboard/status');
          const data = await res.json();
          proxyActive = data.proxy_active;
          const btn = document.getElementById('aegisProxyBtn');
          if (btn) {
              if (proxyActive) {
                  btn.textContent = 'DISCONNECT FROM NOVA';
                  btn.classList.remove('bg-red-500', 'hover:bg-red-400', 'shadow-[0_0_15px_rgba(239,68,68,0.4)]');
                  btn.classList.add('bg-emerald-500', 'hover:bg-emerald-400', 'shadow-[0_0_15px_rgba(16,185,129,0.4)]');
              } else {
                  btn.textContent = 'CONNECT TO NOVA';
                  btn.classList.remove('bg-emerald-500', 'hover:bg-emerald-400', 'shadow-[0_0_15px_rgba(16,185,129,0.4)]');
                  btn.classList.add('bg-red-500', 'hover:bg-red-400', 'shadow-[0_0_15px_rgba(239,68,68,0.4)]');
              }
          }
      } catch (e) {
          console.error("Could not fetch proxy state", e);
      }
  }
  
  window.addEventListener('DOMContentLoaded', initProxyState);
</script>
</body>
"""

if "function toggleProxy()" not in content:
    content = content.replace("</script>\n</body>", proxy_script)
    print("Added proxy script successfully.")
else:
    print("Proxy script already exists.")

with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(content)

