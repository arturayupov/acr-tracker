"""ACR (AI Citation Rate) Monitor for Livostyle / Arcada LLC.

Queries Perplexity API with a panel of fashion-vertical questions, parses responses
for citations to our canonical domains, computes ACR metrics, and appends to a
time-series. Designed to run as a daily GitHub Action.
"""
import os, json, time, urllib.request
from datetime import datetime
from pathlib import Path

API_URL = 'https://api.perplexity.ai/chat/completions'
MODEL   = 'sonar'
PANEL   = json.load(open('queries/panel.json'))
QUERIES = PANEL['queries']
OWN_DOMAINS = [d.lower() for d in PANEL['own_domains']]
BRAND_TERMS = PANEL['brand_terms']

def ask(query):
    body = json.dumps({
        'model': MODEL,
        'messages': [{'role':'user','content': query}],
        'max_tokens': 500,
        'temperature': 0.2,
        'return_citations': True,
        'return_related_questions': False,
    }).encode()
    req = urllib.request.Request(API_URL, data=body, method='POST', headers={
        'Authorization': f'Bearer {os.environ["PPLX_API_KEY"]}',
        'Content-Type': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def cited(resp):
    """Return (cited_domains, cited_pages, brand_in_text)."""
    answer = resp.get('choices',[{}])[0].get('message',{}).get('content','') or ''
    citations = resp.get('citations', []) or []
    # Perplexity returns citation URLs in metadata
    domains = []
    pages = []
    for c in citations:
        url = c if isinstance(c, str) else c.get('url', '')
        for od in OWN_DOMAINS:
            if od in url.lower():
                domains.append(od)
                pages.append(url)
                break
    brand_in_text = any(b in answer.lower() for b in BRAND_TERMS)
    return list(set(domains)), pages, brand_in_text, answer

def main():
    today = datetime.utcnow().strftime('%Y-%m-%d')
    out = {'date': today, 'model': MODEL, 'total_queries': len(QUERIES), 'queries': []}
    cited_count = brand_count = 0
    for i, q in enumerate(QUERIES, 1):
        try:
            r = ask(q)
            domains, pages, brand, answer = cited(r)
            entry = {
                'query': q, 'cited_domains': domains,
                'cited_pages': pages[:5], 'brand_in_text': brand,
                'answer_snippet': answer[:200]
            }
            if domains: cited_count += 1
            if brand: brand_count += 1
            out['queries'].append(entry)
            print(f'  {i}/{len(QUERIES)}: cite={"✓" if domains else "·"} brand={"✓" if brand else "·"}', flush=True)
            time.sleep(0.6)  # rate-limit
        except Exception as e:
            out['queries'].append({'query': q, 'error': str(e)[:200]})
            print(f'  {i}/{len(QUERIES)}: ERROR — {e}', flush=True)

    out['acr_cited_rate']  = round(cited_count / len(QUERIES), 4)
    out['acr_brand_rate']  = round(brand_count / len(QUERIES), 4)

    # Save daily snapshot
    Path('data/daily').mkdir(parents=True, exist_ok=True)
    with open(f'data/daily/{today}.json','w') as f:
        json.dump(out, f, indent=2)

    # Update time-series
    ts_path = 'data/timeseries.json'
    ts = json.load(open(ts_path)) if Path(ts_path).exists() else []
    ts = [t for t in ts if t['date'] != today]  # de-dupe today
    ts.append({
        'date': today,
        'acr_cited_rate': out['acr_cited_rate'],
        'acr_brand_rate': out['acr_brand_rate'],
        'total_queries': out['total_queries'],
        'model': MODEL,
    })
    ts.sort(key=lambda x: x['date'])
    with open(ts_path,'w') as f: json.dump(ts, f, indent=2)

    print(f'\n=== {today} ===')
    print(f'  ACR (citation rate): {out["acr_cited_rate"]:.2%}')
    print(f'  ACR (brand mention): {out["acr_brand_rate"]:.2%}')
    print(f'  Snapshot: data/daily/{today}.json')
    print(f'  Time series: {ts_path}')

if __name__ == '__main__':
    main()
