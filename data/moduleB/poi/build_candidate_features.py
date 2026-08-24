"""build_candidate_features.py
Rebuild candidate_poi_features_v1.json using the new poi_cleaned_v1.json
(which includes restaurant / bank / education categories from poi_type_mapping_v2).

Candidates: uses mock candidate coordinates from the existing file (same 10 sites),
but recalculates all POI stats from the new poi_cleaned_v1.json.

Usage: python build_candidate_features.py
"""
import json, math, os
from datetime import datetime, timezone
from collections import defaultdict

BASE       = os.path.dirname(__file__)
POI_FILE   = os.path.join(BASE, 'poi_cleaned_v1.json')
FEAT_FILE  = os.path.join(BASE, 'candidate_poi_features_v1.json')

RADII      = [300, 500]
R_WEIGHTS  = {300: 0.65, 500: 0.35}
DEDUPE_M   = 50

# Top-level categories to include in poiFactors
MAIN_CATS  = ['medical','transport','commercial','public_service','leisure',
              'accessibility_support','restaurant','bank','education']

# Subcategories to track in poiFactorsSub
SUB_CATS   = [
    # transport
    'bus_stop','mtr_station','parking','ferry_pier','ev_charging','logistics',
    # commercial / restaurant / bank
    'supermarket','convenience_store','shopping_mall','department_store','hotel',
    'chinese_cuisine','fast_food','cafe','teahouse','other_restaurant','foreign_cuisine',
    'bank','atm','insurance',
    # medical
    'clinic','general_hospital','specialist_hospital','pharmacy','emergency',
    # leisure
    'park','gym','sports_complex','museum','cinema','bar','amusement_park',
    # public_service
    'public_toilet','library','post_office','community_center',
    # education
    'kindergarten','primary_school','secondary_school','university','training_center',
    # accessibility
    'accessible_toilet','rehab_center','assistive_device','barrier_free_service',
]

# Density score normalisation reference counts (per 300m weighted)
# These are the max counts observed across all candidates (used for 0-100 normalisation).
# Will be computed dynamically after first pass.

# ── helpers ───────────────────────────────────────────────────────────────────
def haversine_m(lng1, lat1, lng2, lat2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((phi2-phi1)/2)**2 +
         math.cos(phi1)*math.cos(phi2)*math.sin(math.radians(lng2-lng1)/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def weighted_score(c300, c500):
    return c300 * R_WEIGHTS[300] + c500 * R_WEIGHTS[500]

# ── load POI records ──────────────────────────────────────────────────────────
print('Loading poi_cleaned_v1.json ...')
with open(POI_FILE, encoding='utf-8') as f:
    poi_data = json.load(f)
recs = poi_data['records']
print(f'  {len(recs)} records loaded')

# Filter to valid coords only
recs = [r for r in recs if r.get('is_valid_coord') and r.get('lng') and r.get('lat')]
print(f'  {len(recs)} with valid coords')

# ── load existing candidates (keep same sites + IDs) ─────────────────────────
print('Loading existing candidate_poi_features_v1.json for site list ...')
with open(FEAT_FILE, encoding='utf-8') as f:
    existing = json.load(f)
cand_list = [
    {'candidateId': c['candidateId'], 'siteCode': c['siteCode'],
     'lng': c['lng'], 'lat': c['lat']}
    for c in existing['candidates']
]
print(f'  {len(cand_list)} candidate sites')

# ── compute features per candidate ───────────────────────────────────────────
print('Computing POI features ...')

all_results = []

for cand in cand_list:
    clng, clat = cand['lng'], cand['lat']

    # Gather distances for all POIs within 500m
    nearby = []
    for r in recs:
        d = haversine_m(clng, clat, r['lng'], r['lat'])
        if d <= 500:
            nearby.append((d, r))

    # ── poiFactors (main categories) ──────────────────────────────────────────
    poi_factors = {}
    for cat in MAIN_CATS:
        cat_pois = [(d, r) for d, r in nearby if r['category'] == cat]
        c300 = sum(1 for d, _ in cat_pois if d <= 300)
        c500 = len(cat_pois)
        nearest = min((d for d, _ in cat_pois), default=None)
        # deduplication within 50m grid
        seen_cells = set()
        unique50 = 0
        for d, r in sorted(cat_pois, key=lambda x: x[0]):
            cell = (round(r['lng'], 4), round(r['lat'], 4))
            if cell not in seen_cells:
                seen_cells.add(cell)
                unique50 += 1
        poi_factors[cat] = {
            'count_300m': c300,
            'count_500m': c500,
            'nearest_distance_m': round(nearest, 2) if nearest is not None else None,
            'density_score': 0,  # placeholder, normalised later
            'count_unique_50m': unique50,
        }

    # ── poiFactorsSub (subcategories) ─────────────────────────────────────────
    poi_factors_sub = {}
    for sub in SUB_CATS:
        sub_pois = [(d, r) for d, r in nearby if r.get('subcategory') == sub]
        c300 = sum(1 for d, _ in sub_pois if d <= 300)
        c500 = len(sub_pois)
        nearest = min((d for d, _ in sub_pois), default=None)
        seen_cells = set()
        unique50 = 0
        for d, r in sorted(sub_pois, key=lambda x: x[0]):
            cell = (round(r['lng'], 4), round(r['lat'], 4))
            if cell not in seen_cells:
                seen_cells.add(cell)
                unique50 += 1
        poi_factors_sub[sub] = {
            'count_300m': c300,
            'count_500m': c500,
            'nearest_distance_m': round(nearest, 2) if nearest is not None else None,
            'count_unique_50m': unique50,
        }

    all_results.append({
        'candidateId': cand['candidateId'],
        'siteCode': cand['siteCode'],
        'lng': clng,
        'lat': clat,
        'poiFactors': poi_factors,
        'poiFactorsSub': poi_factors_sub,
    })

# ── normalise density_score (0-100 relative to batch max) ────────────────────
print('Normalising density scores ...')
for cat in MAIN_CATS:
    max_w = max(
        weighted_score(r['poiFactors'][cat]['count_300m'],
                       r['poiFactors'][cat]['count_500m'])
        for r in all_results
    )
    for r in all_results:
        f = r['poiFactors'][cat]
        w = weighted_score(f['count_300m'], f['count_500m'])
        f['density_score'] = round((w / max_w * 100) if max_w > 0 else 0, 2)

# ── generate poiComposite + poiSuggestions ────────────────────────────────────
SCORED_CATS = [c for c in MAIN_CATS if c != 'other']

def suggestion_tier(scores):
    avg = sum(scores) / len(scores) if scores else 0
    if avg >= 60: return 'good'
    if avg >= 30: return 'medium'
    return 'weak'

SUGGESTION_RULES = [
    (lambda f: f.get('accessibility_support',{}).get('count_500m',0) == 0,
     '500m 内无障碍支持设施偏少，建议优先配置无障碍卫生间、辅具支持与休憩点。'),
    (lambda f: f.get('public_service',{}).get('count_500m',0) < 5,
     '公共便民服务覆盖不足，建议补充社区服务联动设施。'),
    (lambda f: (f.get('poiFactorsSub',{}) or {}).get('accessible_toilet',{}).get('count_300m',0) == 0 if 'poiFactorsSub' in f else False,
     '200m 内无障碍公厕不足，建议优先补齐无障碍卫生间。'),
    (lambda f: f.get('medical',{}).get('nearest_distance_m') is not None and f.get('medical',{}).get('nearest_distance_m',9999) < 200,
     '医疗资源近邻度较高，适合优先布局应急充电与接驳服务。'),
    (lambda f: f.get('restaurant',{}).get('count_500m',0) > 20,
     '餐饮配套较密集，适合结合人流节点布局服务点。'),
    (lambda f: f.get('bank',{}).get('count_500m',0) > 3,
     '金融服务设施集中，适合面向商务出行需求配置服务点。'),
    (lambda f: f.get('education',{}).get('count_500m',0) > 3,
     '周边教育设施较多，适合兼顾家长接送需求配置停靠点。'),
]

for r in all_results:
    pf = r['poiFactors']
    scores = [pf[c]['density_score'] for c in SCORED_CATS if c in pf]
    tier = suggestion_tier(scores)

    sorted_cats = sorted(SCORED_CATS, key=lambda c: pf.get(c, {}).get('density_score', 0), reverse=True)
    strengths = [c for c in sorted_cats if pf.get(c, {}).get('density_score', 0) >= 40][:3]
    gaps = [c for c in sorted_cats[::-1] if pf.get(c, {}).get('density_score', 0) < 20][:3]

    psub = r['poiFactorsSub']
    sub_sorted = sorted(SUB_CATS, key=lambda s: psub.get(s, {}).get('count_500m', 0), reverse=True)
    sub_strengths = [s for s in sub_sorted if psub.get(s, {}).get('count_500m', 0) > 0][:3]
    sub_gaps = [s for s in sub_sorted[::-1] if psub.get(s, {}).get('count_500m', 0) == 0][:3]

    suggestions = []
    combined = dict(r)
    combined['poiFactorsSub'] = psub
    for check, msg in SUGGESTION_RULES:
        try:
            if check(pf if 'poiFactorsSub' not in str(check.__code__.co_varnames) else combined):
                suggestions.append(msg)
        except Exception:
            pass

    # simpler suggestion pass
    suggestions = []
    if pf.get('accessibility_support', {}).get('count_500m', 0) == 0:
        suggestions.append('500m 内无障碍支持设施偏少，建议优先配置无障碍卫生间、辅具支持与休憩点。')
    if pf.get('public_service', {}).get('count_500m', 0) < 5:
        suggestions.append('公共便民服务覆盖不足，建议补充社区服务联动设施。')
    if psub.get('accessible_toilet', {}).get('count_300m', 0) == 0:
        suggestions.append('200m 内无障碍公厕不足，建议优先补齐无障碍卫生间。')
    if pf.get('medical', {}).get('nearest_distance_m') is not None and pf['medical']['nearest_distance_m'] < 200:
        suggestions.append('医疗资源近邻度较高，适合优先布局应急充电与接驳服务。')
    if pf.get('restaurant', {}).get('count_500m', 0) > 20:
        suggestions.append('餐饮配套较密集，适合结合人流节点布局服务点。')
    if pf.get('bank', {}).get('count_500m', 0) > 3:
        suggestions.append('金融服务设施集中，适合面向商务出行需求配置服务点。')
    if pf.get('education', {}).get('count_500m', 0) > 3:
        suggestions.append('周边教育设施较多，适合兼顾家长接送需求配置停靠点。')

    r['poiComposite'] = {
        'suggestionTier': tier,
        'topStrengths': strengths,
        'topGaps': gaps,
        'subcategoryStrengths': sub_strengths,
        'subcategoryGaps': sub_gaps,
    }
    r['poiSuggestions'] = suggestions

# ── write output ──────────────────────────────────────────────────────────────
out = {
    'schemaVersion': 'candidate-poi-features-v1',
    'generatedAt': datetime.now(timezone.utc).isoformat(),
    'source': {
        'poi': 'public/data/moduleB/poi/poi_cleaned_v1.json',
        'poiMappingVersion': 'poi-type-mapping-v2',
        'candidates': 'mock (10 representative sites)',
        'note': 'Rebuilt with v2 category system: restaurant/bank/education now tracked as separate poiFactors.'
    },
    'radius': RADII,
    'radiusWeights': {'300': R_WEIGHTS[300], '500': R_WEIGHTS[500]},
    'metadata': {
        'aggregation_radius_m': 500,
        'dedupe_radius_m': DEDUPE_M,
        'mainCategories': MAIN_CATS,
    },
    'candidates': all_results,
}

print(f'Writing {FEAT_FILE} ...')
with open(FEAT_FILE, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print('Done.')
print()
print('=== Summary per candidate ===')
for r in all_results:
    pf = r['poiFactors']
    scores = {c: pf[c]['density_score'] for c in MAIN_CATS}
    print(f"  {r['siteCode']:15s}  " + '  '.join(f"{c[:4]}={v:.0f}" for c, v in scores.items()))
