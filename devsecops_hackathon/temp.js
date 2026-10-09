
                    async function simulateAttack(type) {
                        const resDiv = document.getElementById('attack-result');
                        resDiv.innerHTML = "Sending payload...";
                        resDiv.className = "mt-4 font-mono text-xs text-blue-400 h-8";
                        
                        let url = 'http://127.0.0.1:8000/api/test_attack';
                        let options = { method: 'GET' };

                        if (type === 'sql') {
                            url = "http://127.0.0.1:8000/api/test_attack?search=' OR 1=1 --";
                        } else if (type === 'xss') {
                            url = "http://127.0.0.1:8000/api/test_attack?q=alert(1)<\/script>";
                        } else if (type === 'idor') {
                            url = "http://127.0.0.1:8000/api/orders/admin_99";
                            options = { 
                                method: 'GET',
                                headers: { 'Authorization': 'Bearer testuser' }
                            };
                        } else if (type === 'dlp') {
                            url = "http://127.0.0.1:8000/api/leak_key";
                        } else if (type === 'header_xss') {
                            url = "http://127.0.0.1:8000/api/products";
                            options = { 
                                method: 'GET',
                                headers: { 'X-Custom-Header': "alert('hacked')<\/script>" }
                            };
                        }

                        try {
                            const response = await fetch(url, options);
                            const text = await response.text();
                            
                            if (!response.ok) {
                                resDiv.innerHTML = `<span class="text-green-500">BLOCKED BY VEIL: ${response.status}</span> - ${text}`;
                            } else {
                                resDiv.innerHTML = `<span class="text-red-500">FAILED: Payload bypassed proxy (HTTP 200). Is Veil running?</span>`;
                            }
                        } catch (e) {
                            resDiv.innerHTML = `<span class="text-red-500">Error: ${e.message}</span>`;
                        }
                    }
                
