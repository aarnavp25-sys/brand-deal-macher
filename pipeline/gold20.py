"""Gold labels for 20 creators, written by reading each creator's bio and posts (S-009, 2026-11-18).

Used by `llm_classify.py test` to check a model before paying for a full run. Same set and scoring as the
47-model Bedrock test in docs/data-and-matching.md (LLM / AWS notes), so results are comparable.
Each entry: (acceptable primary categories, allowed products, required products (one must appear), is_shop).
2026-11-20: allowed products extended for the 82-type taxonomy (40 types added after S-009), only where the
evidence posts were read and really feature the product (e.g. a furniture store -> furniture, a tour operator ->
tours & trips, an @anveshan ghee collab -> organic staples).
"""

F, B, FA, H = "Food & Beverages", "Beauty & Skincare", "Fashion & Clothing", "Home Decor & Handmade"

GOLD = {
    "rider_girls_pune": ({"Automobile"}, {"bikes & cars"}, set(), False),
    "the_tastyy_torte": ({F}, {"home baked goods"}, {"home baked goods"}, True),
    "ashma_makeup_artist": ({B}, {"makeup", "skincare"}, {"makeup"}, False),
    "thatsoshrutii": ({FA, B}, {"women's western wear", "women's ethnic wear", "footwear", "makeup"},
                      {"women's western wear", "women's ethnic wear"}, False),
    "priyal_giri": ({B, FA}, {"skincare", "makeup", "women's jewelry", "women's western wear", "women's ethnic wear",
                              "travel stays", "smartphones", "candles & gifting", "yoga & wellness",
                              "audio & wearables", "beverages"},
                    {"skincare", "makeup", "women's jewelry", "women's western wear"}, False),
    "facilities_furniture": ({H}, {"home decor", "candles & gifting", "plants & gardening", "furniture"}, {"home decor"}, True),
    "lifefitness_raipur": ({"Fitness & Wellness"}, set(), set(), True),
    "brahmaball": ({"Sports"}, set(), set(), False),
    "srimano": ({"Education & Finance", "Tech & Gadgets"}, set(), set(), False),
    "gamersparadisekol": ({"Gaming"}, {"games & esports", "restaurants & cafes"}, set(), True),
    "puneet_kids_comedy_dance_reels": ({"Entertainment & Comedy", "Music & Dance"}, set(), set(), False),
    "amit.mishra_official": ({"Music & Dance"}, set(), set(), False),
    "deepesh_sj": ({"Entertainment & Comedy"}, {"courses & edtech"}, set(), False),
    "talesofasassymumma": ({"Parenting & Kids"}, {"candles & gifting", "healthy food", "baby products", "organic staples",
                                                  "toys & games"}, set(), False),
    "breathedreamgo": ({"Travel & Explore"}, {"travel stays", "tours & trips", "handmade crafts"}, {"travel stays"}, False),
    "carsncoffee.ind": ({"Automobile"}, {"bikes & cars", "beverages"}, set(), False),
    "simmi_singh00_": ({"Entertainment & Comedy"}, set(), set(), False),
    "vibe_with_hasmukhii": ({"Travel & Explore"}, {"travel stays", "restaurants & cafes", "packaged snacks",
                                                   "smartphones", "apps & software", "events & experiences"}, {"travel stays"}, False),
    "classicpahadi": ({"Travel & Explore"}, {"bikes & cars"}, set(), False),
    "jagrati_chatnani": ({"Music & Dance", "Entertainment & Comedy"}, {"women's ethnic wear", "music & dance classes"},
                         set(), False),
}


def score(username, row):
    """row = cleaned LLM fields (category, products [{type,...}], is_shop). Returns per-check booleans."""
    cats, allowed, required, shop = GOLD[username]
    prods = {p["type"] for p in row.get("products") or []}
    return {"cat": row.get("category") in cats,
            "prod": prods <= allowed and (not required or bool(prods & required)),
            "shop": bool(row.get("is_shop")) == shop}
