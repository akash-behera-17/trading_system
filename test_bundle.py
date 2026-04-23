import urllib.request
import re

try:
    html = urllib.request.urlopen('https://neurotrade-ai.netlify.app').read().decode('utf-8')
    js_paths = re.findall(r'src=\"(/assets/index-.*?\.js)\"', html)
    if not js_paths:
        print('No JS path found in HTML')
    else:
        for path in js_paths:
            js_url = 'https://neurotrade-ai.netlify.app' + path
            js_code = urllib.request.urlopen(js_url).read().decode('utf-8')
            if 'trading-system-ma0a.onrender.com' in js_code:
                print('SUCCESS: Render URL is baked into the JS bundle!', path)
            elif 'localhost:5000' in js_code:
                print('FAIL: localhost:5000 is compiled into the bundle!', path)
            else:
                print('NEITHER FOUND')
except Exception as e:
    print('Error:', e)
