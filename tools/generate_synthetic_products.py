import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(__file__))
TMP = os.path.join(ROOT, 'tmp')

summary_path = os.path.join(TMP, 'ml_analysis_summary.json')
output_path = os.path.join(TMP, 'product_clusters_3d.json')

if not os.path.exists(summary_path):
    print('ml_analysis_summary.json not found in tmp/. Cannot synthesize product data.')
    exit(1)

with open(summary_path, 'r', encoding='utf-8') as f:
    summary = json.load(f)

categories = summary.get('product_categories', {})
if not categories:
    # fallback categories
    categories = {'Bestsellers': {'count': 1000, 'percentage': 40}, 'Popular Items': {'count': 600, 'percentage': 24}, 'Niche Products': {'count': 500, 'percentage': 20}, 'Regular Items': {'count': 300, 'percentage': 16}}

# produce about 200 synthetic products
TOTAL = 200
cats = list(categories.keys())
weights = [categories[c].get('percentage', 1) for c in cats]
# normalize weights
s = sum(weights)
weights = [w/s for w in weights]

products = []
for i in range(TOTAL):
    # choose category by weight
    r = random.random()
    cum = 0
    for c, w in zip(cats, weights):
        cum += w
        if r <= cum:
            cat = c
            break
    # generate synthetic metrics based on category
    # larger categories get higher quantities and revenue
    base_q = int(100 + random.random() * 1000 * (0.5 + weights[cats.index(cat)]))
    base_rev = round(base_q * (5 + random.random() * 50), 2)  # price average 5-55
    num_trans = int(1 + random.random() * 300 * (0.5 + weights[cats.index(cat)]))
    prod = {
        'Description': f'{cat} Sample Product {i+1}',
        'TotalQuantity': base_q,
        'TotalRevenue': base_rev,
        'NumTransactions': num_trans,
        'ProductCategory': cat
    }
    products.append(prod)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print(f'Wrote synthetic product clusters: {output_path} (records: {len(products)})')
