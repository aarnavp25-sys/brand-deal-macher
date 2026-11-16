"""Fixed taxonomy for Brand Deal Matcher.

Every classification (keyword-based now, LLM later) must pick values from these
lists only; free-text labels break search. Keywords are matched lowercase
against bio + captions + hashtags.
"""

# name: (demo_rank, sub_tags, search terms for Apify Search Scraper, match keywords)
CATEGORIES = {
    "Food & Beverages": (1, ["home baker", "street food", "cafe review", "healthy food", "recipes"],
        ["pune home baker", "mumbai food blogger"],
        ["food", "foodie", "recipe", "cafe", "restaurant", "bake", "cake", "dessert", "chai", "biryani", "streetfood", "eats", "kitchen", "cooking", "misal", "vadapav"]),
    "Beauty & Skincare": (2, ["skincare", "makeup", "haircare", "natural/ayurvedic", "men's grooming"],
        ["pune beauty blogger", "indian skincare influencer", "mens grooming india"],
        ["skincare", "skin", "makeup", "beauty", "serum", "sunscreen", "haircare", "hair", "lipstick", "grooming", "beard", "glow", "spf"]),
    "Fashion & Clothing": (3, ["ethnic wear", "streetwear", "saree", "thrift", "men's fashion"],
        ["pune fashion blogger", "mumbai mens fashion", "ethnic wear influencer india"],
        ["fashion", "outfit", "ootd", "style", "styling", "saree", "kurta", "streetwear", "lookbook", "wear", "menswear", "thrift", "fit check"]),
    "Jewelry & Accessories": (4, ["handmade jewelry", "men's jewelry", "bags", "footwear", "watches"],
        ["jewellery influencer india", "watch reviewer india", "mens accessories india"],
        ["jewellery", "jewelry", "earrings", "necklace", "ring", "chain", "bracelet", "watch", "watches", "bag", "sneakers", "accessories", "oxidised"]),
    "Home Decor & Handmade": (5, ["home decor", "plants", "art/crafts", "candles", "gifting"],
        ["home decor influencer india", "pune home decor", "plant parent india"],
        ["decor", "homedecor", "interior", "plants", "plant", "candle", "handmade", "craft", "diy", "artwork", "gifting", "home tour"]),
    "Fitness & Wellness": (6, ["gym", "yoga", "nutrition", "mental wellness"],
        ["pune fitness influencer", "mumbai gym influencer", "yoga influencer india"],
        ["fitness", "gym", "workout", "yoga", "protein", "fatloss", "fat loss", "muscle", "transformation", "nutrition", "diet", "wellness", "bodybuilding"]),
    "Sports": (7, ["cricket", "football", "running", "cycling", "sports gear"],
        ["indian cricket creator", "pune runners", "football creator india"],
        ["cricket", "football", "running", "marathon", "cycling", "badminton", "sports", "athlete", "kabaddi", "tennis", "match"]),
    "Tech & Gadgets": (8, ["gadget review", "unboxing", "smartphones", "accessories", "apps"],
        ["indian tech reviewer", "gadget review hindi", "tech creator india"],
        ["tech", "gadget", "unboxing", "smartphone", "iphone", "android", "laptop", "review", "earbuds", "ai tools", "apps", "setup"]),
    "Gaming": (9, ["mobile gaming", "esports", "pc gaming"],
        ["indian gamer bgmi", "gaming creator india", "bgmi streamer"],
        ["gaming", "gamer", "bgmi", "pubg", "freefire", "valorant", "esports", "gameplay", "stream", "minecraft", "gta"]),
    "Entertainment & Comedy": (10, ["skits", "memes", "relatable", "pranks"],
        ["pune comedy creator", "hindi comedy reels", "marathi comedy creator"],
        ["comedy", "funny", "skit", "meme", "memes", "relatable", "prank", "humour", "humor", "standup", "acting"]),
    "Music & Dance": (11, ["singing", "dance covers", "instruments"],
        ["pune dancer", "indian singer cover", "mumbai dance creator"],
        ["dance", "dancer", "choreography", "singing", "singer", "cover", "music", "guitar", "song", "rap", "bollywood dance"]),
    "Education & Finance": (12, ["study tips", "career", "personal finance", "stock market"],
        ["personal finance india creator", "study tips india", "stock market hindi"],
        ["finance", "money", "stock", "investing", "trading", "sip", "mutualfund", "study", "career", "upsc", "exam", "education", "learn"]),
    "Parenting & Kids": (13, ["mom blogger", "baby products", "kids learning"],
        ["pune mom blogger", "indian mom influencer", "parenting india"],
        ["mom", "mommy", "motherhood", "parenting", "baby", "toddler", "kids", "momlife", "pregnancy", "newborn"]),
    "Travel & Explore": (14, ["city explore", "weekend trips", "stays"],
        ["pune travel blogger", "maharashtra travel creator", "indian travel influencer"],
        ["travel", "trip", "trek", "trekking", "explore", "wanderlust", "staycation", "hills", "beach", "roadtrip", "itinerary"]),
    "Automobile": (15, ["bikes", "cars", "modification"],
        ["pune bike rider", "indian car reviewer", "moto vlogger india"],
        ["bike", "biker", "car", "cars", "motovlog", "ride", "royalenfield", "ktm", "automobile", "superbike", "modified"]),
    "Pets": (16, ["dogs", "cats", "pet care"],
        ["pune dog influencer", "indian pet influencer", "cat lover india"],
        ["dog", "dogs", "puppy", "cat", "cats", "kitten", "pet", "pets", "doggo", "petcare", "labrador", "indie dog"]),
}

# Round-2 search terms (2026-11-16): city-specific terms for categories where broad
# terms returned mostly >100K or <1K accounts. Lesson: city + niche terms yield
# far more 1K-100K creators than "india"/"influencer" terms.
EXTRA_SEARCH_TERMS = {
    "Tech & Gadgets": ["pune tech creator", "mumbai tech creator", "tech tips marathi", "smartphone tips hindi", "unboxing india"],
    "Education & Finance": ["pune finance creator", "marathi finance", "career guidance pune", "mumbai finance influencer"],
    "Beauty & Skincare": ["pune makeup blogger", "mumbai skincare blogger", "skincare routine india"],
    "Home Decor & Handmade": ["mumbai home decor blogger", "pune interior creator", "bangalore home decor"],
    "Gaming": ["pune gamer", "marathi gamer"],
    "Music & Dance": ["pune singer"],
    "Fashion & Clothing": ["mumbai fashion blogger"],
}

# Round-3 search terms (2026-11-16): fill thin categories with the last Apify credit.
for _cat, _terms in {
    "Jewelry & Accessories": ["pune jewellery blogger", "mumbai jewellery influencer", "mens accessories mumbai", "watch collector india", "sneakerhead india"],
    "Education & Finance": ["pune career coach", "finance tips marathi", "mumbai study influencer"],
    "Fitness & Wellness": ["pune gym trainer", "pune yoga teacher", "mumbai fitness coach"],
    "Entertainment & Comedy": ["pune comedy reels", "mumbai comedy creator"],
    "Fashion & Clothing": ["pune mens fashion", "pune fashion influencer", "delhi fashion blogger"],
    "Gaming": ["mumbai gamer"], "Tech & Gadgets": ["pune tech reviewer"],
    "Parenting & Kids": ["mumbai mom blogger"], "Home Decor & Handmade": ["pune home decor blogger"],
}.items():
    EXTRA_SEARCH_TERMS.setdefault(_cat, []).extend(_terms)

# Round-4 search terms (2026-11-17): last Apify credit of the cycle, thinnest categories.
for _cat, _terms in {
    "Education & Finance": ["pune study creator", "marathi education creator", "upsc aspirant creator", "money tips hindi"],
    "Jewelry & Accessories": ["handmade jewellery pune", "oxidised jewellery influencer", "pune watch lover"],
    "Entertainment & Comedy": ["marathi reels creator", "hindi relatable reels", "pune skit creator"],
    "Gaming": ["marathi gaming", "free fire creator india", "valorant india creator"],
    "Music & Dance": ["mumbai singer", "pune guitarist"], "Home Decor & Handmade": ["pune plant lover", "diy decor india"],
    "Sports": ["pune cricket", "pune cyclist"], "Tech & Gadgets": ["tech marathi"],
}.items():
    EXTRA_SEARCH_TERMS.setdefault(_cat, []).extend(_terms)

# product type: (category, keywords) — what a brand can sell, and evidence words in posts
PRODUCT_TYPES = {
    "home baked goods": ("Food & Beverages", ["cake", "cookies", "brownie", "bake", "homebaker", "dessert"]),
    "packaged snacks": ("Food & Beverages", ["snack", "chips", "namkeen", "makhana"]),
    "beverages": ("Food & Beverages", ["coffee", "chai", "tea", "juice", "smoothie", "drink"]),
    "restaurants & cafes": ("Food & Beverages", ["cafe", "restaurant", "eatery", "dine"]),
    "skincare": ("Beauty & Skincare", ["skincare", "serum", "sunscreen", "moisturizer", "facewash", "spf"]),
    "makeup": ("Beauty & Skincare", ["makeup", "lipstick", "foundation", "kajal", "eyeliner"]),
    "haircare": ("Beauty & Skincare", ["haircare", "shampoo", "hair oil", "conditioner"]),
    "men's grooming": ("Beauty & Skincare", ["beard", "trimmer", "grooming", "shave", "aftershave"]),
    "perfume": ("Beauty & Skincare", ["perfume", "fragrance", "attar", "scent", "deodorant"]),
    "women's ethnic wear": ("Fashion & Clothing", ["saree", "kurti", "lehenga", "ethnic", "kurta set"]),
    "women's western wear": ("Fashion & Clothing", ["dress", "top", "jeans", "western wear"]),
    "men's clothing": ("Fashion & Clothing", ["menswear", "shirt", "mens fashion", "men's fashion", "tshirt", "kurta"]),
    "streetwear": ("Fashion & Clothing", ["streetwear", "oversized", "hoodie", "cargo"]),
    "women's jewelry": ("Jewelry & Accessories", ["earrings", "necklace", "jhumka", "oxidised", "bangles"]),
    "men's jewelry": ("Jewelry & Accessories", ["chain", "ring", "bracelet", "mens jewelry", "men's jewellery"]),
    "watches": ("Jewelry & Accessories", ["watch", "watches", "wristwatch", "timepiece"]),
    "bags": ("Jewelry & Accessories", ["bag", "handbag", "backpack", "tote"]),
    "footwear": ("Jewelry & Accessories", ["sneakers", "shoes", "footwear", "heels", "sandals"]),
    "sunglasses": ("Jewelry & Accessories", ["sunglasses", "shades", "eyewear"]),
    "home decor": ("Home Decor & Handmade", ["decor", "homedecor", "interior", "cushion", "wall art"]),
    "plants & gardening": ("Home Decor & Handmade", ["plant", "plants", "garden", "succulent"]),
    "candles & gifting": ("Home Decor & Handmade", ["candle", "gift", "hamper", "gifting"]),
    "handmade crafts": ("Home Decor & Handmade", ["handmade", "craft", "crochet", "resin art", "pottery"]),
    "gym wear": ("Fitness & Wellness", ["gymwear", "activewear", "gym wear", "leggings"]),
    "supplements": ("Fitness & Wellness", ["protein", "whey", "supplement", "creatine", "preworkout"]),
    "healthy food": ("Fitness & Wellness", ["healthy", "diet", "millet", "oats", "nutrition"]),
    "yoga & wellness": ("Fitness & Wellness", ["yoga", "meditation", "wellness", "ayurveda"]),
    "sports gear": ("Sports", ["bat", "jersey", "football boots", "racket", "sports gear"]),
    "smartphones": ("Tech & Gadgets", ["iphone", "smartphone", "samsung", "oneplus", "pixel"]),
    "audio & wearables": ("Tech & Gadgets", ["earbuds", "headphones", "smartwatch", "speaker", "tws"]),
    "laptops & pc": ("Tech & Gadgets", ["laptop", "macbook", "pc build", "keyboard", "monitor"]),
    "phone accessories": ("Tech & Gadgets", ["phone case", "charger", "powerbank", "cover"]),
    "apps & software": ("Tech & Gadgets", ["app", "ai tool", "software", "chatgpt"]),
    "gaming gear": ("Gaming", ["controller", "gaming mouse", "headset", "gaming phone", "trigger"]),
    "music gear": ("Music & Dance", ["guitar", "mic", "microphone", "keyboard piano"]),
    "courses & edtech": ("Education & Finance", ["course", "upsc", "exam", "study", "notes"]),
    "finance apps": ("Education & Finance", ["sip", "mutual fund", "demat", "trading app", "investing"]),
    "baby products": ("Parenting & Kids", ["baby", "diaper", "toddler", "newborn", "kids toys"]),
    "travel stays": ("Travel & Explore", ["stay", "homestay", "resort", "villa", "hotel"]),
    "travel gear": ("Travel & Explore", ["luggage", "suitcase", "travel bag", "trolley"]),
    "bike & car accessories": ("Automobile", ["helmet", "riding gear", "car accessories", "dashcam"]),
    "pet products": ("Pets", ["pet food", "dog food", "cat food", "pet toy", "treats"]),
}

CREATOR_IG_CATEGORIES_OK = {
    None, "", "Digital creator", "Blogger", "Reel creator", "Personal blog", "Artist", "Public figure",
    "Athlete", "Gamer", "Video creator", "Musician", "Musician/band", "Dancer", "Comedian", "Writer",
    "Photographer", "Fitness trainer", "Fitness model", "Model", "Actor", "Creator", "Education",
    "Kitchen/cooking", "Food & Drink", "Video game", "Gaming video creator", "Health/beauty",
    "Fashion model", "Coach", "Entrepreneur", "Personal coach", "Makeup artist", "Chef",
    "Just for fun", "Pet", "Traveler",
}
