import re

with open("frontend/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace toggleProxy and initProxyState
old_script = """  let proxyActive = false;
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
  }"""

new_script = """  let proxyActive = false;
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

if old_script in content:
    content = content.replace(old_script, new_script)
    with open("frontend/index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed script successfully.")
else:
    print("Could not find old script. Let's dump the script content.")

