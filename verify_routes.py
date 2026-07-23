import urllib.request

urls = [
    'http://127.0.0.1:8001/health',
    'http://127.0.0.1:8001/api/v1/tickets?page=1&size=2',
    'http://127.0.0.1:8001/api/v1/conversations',
    'http://127.0.0.1:8001/api/v1/dashboard?days=7',
]

for url in urls:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            print(url, resp.status)
            print(body[:500])
            print('---')
    except Exception as e:
        print(url, 'ERROR', e)
        print('---')
