"""
Quick diagnostic — run this to check if curl_cffi is working at all.
  python diagnose.py
"""

import curl_cffi
from curl_cffi import requests as cffi_requests

print(f"curl_cffi version: {curl_cffi.__version__}")
print()

# Test against simple, always-up URLs with zero bot detection
TEST_URLS = [
    ("https://api.ipify.org",  "returns your IP — simplest possible test"),
    ("https://example.com",    "IANA example site — always accessible"),
]

VERSIONS = ["chrome131", "chrome124", "chrome120"]

for url, desc in TEST_URLS:
    print(f"Testing: {url}  ({desc})")
    for version in VERSIONS:
        try:
            session = cffi_requests.Session(impersonate=version)
            resp    = session.get(url, timeout=10)
            print(f"  {version}: {resp.status_code}")
        except Exception as e:
            print(f"  {version}: ERROR — {e}")
    print()
