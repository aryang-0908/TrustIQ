import re

with open("frontend/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Veil Header buttons
veil_buttons_old = """          <button onclick="window.open('dashboard.html', '_blank')" class="px-5 py-2.5 bg-blue-500 text-obsidian-950 text-[10px] font-bold tracking-[0.2em] hover:bg-blue-400 transition-colors duration-300 shadow-[0_0_15px_rgba(59,130,246,0.4)] mr-4">
              LAUNCH LIVE GUARD DASHBOARD
            </button>
            <button onclick="openDeployModal()" class="px-5 py-2.5 bg-emerald-500 text-obsidian-950 text-[10px] font-bold tracking-[0.2em] hover:bg-emerald-400 transition-colors duration-300 shadow-[0_0_15px_rgba(52,211,153,0.4)]">
            INTEGRATE IN WEB APP
          </button>"""

veil_buttons_new = """          <button id="veilProxyBtn" onclick="toggleProxy()" class="px-5 py-2.5 bg-red-500 text-white text-[11px] font-bold tracking-[0.2em] hover:bg-red-400 transition-colors duration-300 shadow-[0_0_15px_rgba(239,68,68,0.4)] mr-4">
              CONNECT TO VANGUARD
            </button>
            <button onclick="window.open('dashboard.html', '_blank')" class="px-5 py-2.5 bg-blue-500 text-obsidian-950 text-[10px] font-bold tracking-[0.2em] hover:bg-blue-400 transition-colors duration-300 shadow-[0_0_15px_rgba(59,130,246,0.4)] mr-4">
              DASHBOARD
            </button>
            <button onclick="openDeployModal()" class="px-5 py-2.5 bg-emerald-500 text-obsidian-950 text-[10px] font-bold tracking-[0.2em] hover:bg-emerald-400 transition-colors duration-300 shadow-[0_0_15px_rgba(52,211,153,0.4)]">
            INTEGRATE
          </button>"""

if veil_buttons_old in content:
    content = content.replace(veil_buttons_old, veil_buttons_new)
else:
    print("Could not find Veil buttons old string.")

# 2. Update JavaScript to handle both buttons
js_old = """  let proxyActive = false;
  async function toggleProxy() {
      const btn = document.getElementById('aegisProxyBtn');
      const newState = !proxyActive;
      try {
          const res = await fetch('https://vanguard-proxy-2026.loca.lt/dashboard/toggle_proxy', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Bypass-Tunnel-Reminder': 'true' },
              body: JSON.stringify({ active: newState })
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
          const res = await fetch('https://vanguard-proxy-2026.loca.lt/dashboard', {
              headers: { 'Bypass-Tunnel-Reminder': 'true' }
          });
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
  }"""

js_new = """  let proxyActive = false;
  
  function updateProxyButtons() {
      const aegisBtn = document.getElementById('aegisProxyBtn');
      const veilBtn = document.getElementById('veilProxyBtn');
      
      if (aegisBtn) {
          if (proxyActive) {
              aegisBtn.textContent = 'DISCONNECT FROM NOVA';
              aegisBtn.classList.remove('bg-red-500', 'hover:bg-red-400', 'shadow-[0_0_15px_rgba(239,68,68,0.4)]');
              aegisBtn.classList.add('bg-emerald-500', 'hover:bg-emerald-400', 'shadow-[0_0_15px_rgba(16,185,129,0.4)]');
          } else {
              aegisBtn.textContent = 'CONNECT TO NOVA';
              aegisBtn.classList.remove('bg-emerald-500', 'hover:bg-emerald-400', 'shadow-[0_0_15px_rgba(16,185,129,0.4)]');
              aegisBtn.classList.add('bg-red-500', 'hover:bg-red-400', 'shadow-[0_0_15px_rgba(239,68,68,0.4)]');
          }
      }
      
      if (veilBtn) {
          if (proxyActive) {
              veilBtn.textContent = 'DISCONNECT FROM VANGUARD';
              veilBtn.classList.remove('bg-red-500', 'hover:bg-red-400', 'shadow-[0_0_15px_rgba(239,68,68,0.4)]');
              veilBtn.classList.add('bg-emerald-500', 'hover:bg-emerald-400', 'shadow-[0_0_15px_rgba(16,185,129,0.4)]');
          } else {
              veilBtn.textContent = 'CONNECT TO VANGUARD';
              veilBtn.classList.remove('bg-emerald-500', 'hover:bg-emerald-400', 'shadow-[0_0_15px_rgba(16,185,129,0.4)]');
              veilBtn.classList.add('bg-red-500', 'hover:bg-red-400', 'shadow-[0_0_15px_rgba(239,68,68,0.4)]');
          }
      }
  }

  async function toggleProxy() {
      const newState = !proxyActive;
      try {
          const res = await fetch('https://vanguard-proxy-2026.loca.lt/dashboard/toggle_proxy', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Bypass-Tunnel-Reminder': 'true' },
              body: JSON.stringify({ active: newState })
          });
          const data = await res.json();
          proxyActive = data.proxy_active;
          updateProxyButtons();
      } catch (e) {
          alert("Error toggling proxy. Is the proxy server running?");
          console.error(e);
      }
  }

  // Fetch initial state
  async function initProxyState() {
      try {
          const res = await fetch('https://vanguard-proxy-2026.loca.lt/dashboard', {
              headers: { 'Bypass-Tunnel-Reminder': 'true' }
          });
          const data = await res.json();
          proxyActive = data.proxy_active;
          updateProxyButtons();
      } catch (e) {
          console.error("Could not fetch proxy state", e);
      }
  }"""

if js_old in content:
    content = content.replace(js_old, js_new)
else:
    print("Could not find old JS block.")

with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated index.html with dual proxy buttons.")

