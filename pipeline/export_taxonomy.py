"""Write the fixed taxonomy to supabase/functions/api/taxonomy.json so the Edge Function uses the same lists.

usage: python3 pipeline/export_taxonomy.py   (rerun after editing taxonomy.py, then redeploy the function)
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from taxonomy import BRIEF_CITIES, CATEGORIES, PRODUCT_TYPES  # noqa: E402

out = os.path.join(HERE, "..", "supabase", "functions", "api", "taxonomy.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"categories": {c: v[3] for c, v in CATEGORIES.items()},
           "products": {p: [cat, kws] for p, (cat, kws) in PRODUCT_TYPES.items()},
           "cities": BRIEF_CITIES}, open(out, "w"), ensure_ascii=False, indent=1)
print("wrote", os.path.relpath(out), len(CATEGORIES), "categories", len(PRODUCT_TYPES), "products")
