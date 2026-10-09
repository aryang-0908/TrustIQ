import re

with open('vanguard.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_script = '''<script>
                    function showHackedModal(title, text) {
                        let modal = document.getElementById('hacked-modal');
                        if (!modal) {
                            modal = document.createElement('div');
                            modal.id = 'hacked-modal';
                            modal.className = 'fixed inset-0 bg-black/90 z-[9999] flex items-center justify-center p-4';
                            modal.innerHTML = \
                                <div class="bg-black border border-red-500 rounded p-6 max-w-2xl w-full shadow-[0_0_50px_rgba(239,68,68,0.4)] relative">
                                    <div class="absolute top-0 left-0 w-full h-1 bg-red-600"></div>
                                    <h2 class="text-red-500 font-mono text-2xl mb-2 flex items-center gap-2">
                                        <i class="fas fa-skull"></i> <span id="hacked-title">SYSTEM COMPROMISED</span>
                                    </h2>
                                    <p class="text-gray-400 font-mono text-xs mb-4">CRITICAL SECURITY FAILURE. PROXY BYPASSED.</p>
                                    <div class="bg-gray-900 border border-red-900 p-4 rounded h-64 overflow-y-auto">
                                        <pre id="hacked-content" class="text-green-500 font-mono text-[11px] whitespace-pre-wrap"></pre>
                                    </div>
                                    <div class="mt-6 flex justify-end">
                                        <button onclick="document.getElementById('hacked-modal').remove()" class="bg-red-600 hover:bg-red-700 text-white font-mono px-6 py-2 rounded transition">SHUT DOWN TERMINAL</button>
                                    </div>
                                </div>
                            \;
                            document.body.appendChild(modal);
                        }
                        document.getElementById('hacked-title').innerText = title;
                        document.getElementById('hacked-content').innerText = text;
                    }

                    async function simulateAttack(type) {
                        try {
                            const resDiv = document.getElementById('attack-result');
                            if (resDiv) {
                                resDiv.innerHTML = "Sending payload...";
                                resDiv.className = "mt-4 font-mono text-xs text-blue-400 h-8";
                            }
                            
                            let url = 'https://vanguard-proxy-2026.loca.lt/api/search';
                            let options = { method: 'GET', headers: {'Bypass-Tunnel-Reminder': 'true'} };
                            let attackTitle = "SYSTEM COMPROMISED";

                            if (type === 'sql') {
                                url = "https://vanguard-proxy-2026.loca.lt/api/search?q=' OR 1=1 --";
                                attackTitle = "SQL INJECTION SUCCESSFUL";
                            } else if (type === 'xss') {
                                url = "https://vanguard-proxy-2026.loca.lt/api/reviews";
                                options = {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json', 'Bypass-Tunnel-Reminder': 'true' },
                                    body: JSON.stringify({ user: "hacker", review: "<script>alert('You have been hacked!')<\/script>" })
                                };
                                attackTitle = "STORED XSS EXPLOITED";
                            } else if (type === 'idor') {
                                url = "https://vanguard-proxy-2026.loca.lt/api/orders/admin_99";
                                options = { 
                                    method: 'GET',
                                    headers: { 'Authorization': 'Bearer user_1', 'Bypass-Tunnel-Reminder': 'true' }
                                };
                                attackTitle = "IDOR: UNAUTHORIZED ACCESS TO ADMIN ORDERS";
                            } else if (type === 'dlp') {
                                url = "https://vanguard-proxy-2026.loca.lt/api/admin/stats";
                                attackTitle = "DLP FAILURE: SECRETS EXFILTRATED";
                            } else if (type === 'header_xss') {
                                url = "https://vanguard-proxy-2026.loca.lt/api/products";
                                options = { 
                                    method: 'GET',
                                    headers: { 'is_admin': 'true', 'Bypass-Tunnel-Reminder': 'true' }
                                };
                                attackTitle = "PRIVILEGE ESCALATION SUCCESSFUL";
                            }

                            const response = await fetch(url, options);
                            const text = await response.text();
                            
                            if (resDiv) {
                                if (response.status === 400 || response.status === 401 || response.status === 403 || response.status === 429) {
                                    resDiv.innerHTML = \<span class="text-green-500 font-bold"><i class="fas fa-shield-alt"></i> BLOCKED BY VEIL: \</span> - \\;
                                } else {
                                    resDiv.innerHTML = \<span class="text-red-500 font-bold"><i class="fas fa-exclamation-triangle"></i> HACK SUCCESSFUL: Payload bypassed proxy (HTTP \)</span>\;
                                    
                                    let formattedText = text;
                                    try {
                                        formattedText = JSON.stringify(JSON.parse(text), null, 2);
                                    } catch (e) {}
                                    
                                    showHackedModal(attackTitle, formattedText);
                                }
                            }
                        } catch (e) {
                            console.error("Attack error:", e);
                            const resDiv = document.getElementById('attack-result');
                            if (resDiv) {
                                resDiv.innerHTML = \<span class="text-red-500">Error: \</span>\;
                            }
                        }
                    }
                </script>'''

content = re.sub(r'<script>\s*async function simulateAttack\(type\).*?<\/script>', new_script, content, flags=re.DOTALL)

with open('vanguard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done patching vanguard.html')
