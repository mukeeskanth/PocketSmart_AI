from app.services.gemini_service import generate_json, configured

PLATFORMS = {
    "home": [
        ("Amazon", "https://www.amazon.in/s?k="),
        ("IKEA", "https://www.ikea.com/in/en/search/?q="),
        ("Flipkart", "https://www.flipkart.com/search?q=")
    ],
    "party": [
        ("Swiggy", "https://www.swiggy.com/search?query="),
        ("Zomato", "https://www.zomato.com/search?q="),
        ("OYO", "https://www.oyorooms.com/search?location=")
    ],
    "jewelry": [
        ("Amazon", "https://www.amazon.in/s?k="),
        ("Flipkart", "https://www.flipkart.com/search?q=")
    ]
}

def fallback(planner, data):
    budget = data["budget"]
    if planner == "home":
        names = [f"{r} lighting" for r in data["rooms"]]
        names += [f"{r} storage" for r in data["rooms"]]
        allocation = [
            {"category":"Furniture","amount":round(budget*.45)},
            {"category":"Lighting","amount":round(budget*.20)},
            {"category":"Decor","amount":round(budget*.20)},
            {"category":"Contingency","amount":round(budget*.15)}]
        summary = f"{data['style']} home plan for ₹{budget:,.0f}."
    elif planner == "party":
        names = ["Catering package","Party decoration","Venue setup",
                 "Entertainment setup","Guest refreshments"]
        allocation = [
            {"category":"Food & catering","amount":round(budget*.50)},
            {"category":"Venue","amount":round(budget*.20)},
            {"category":"Decoration","amount":round(budget*.15)},
            {"category":"Entertainment","amount":round(budget*.10)},
            {"category":"Contingency","amount":round(budget*.05)}]
        summary = f"{data['event_type']} plan for {data['guests']} guests within ₹{budget:,.0f}."
    else:
        names = [f"{data['style']} necklace", f"{data['style']} earrings",
                 "Bracelet / bangle", "Ring"]
        allocation = [
            {"category":"Necklace","amount":round(budget*.45)},
            {"category":"Earrings","amount":round(budget*.25)},
            {"category":"Bracelet","amount":round(budget*.15)},
            {"category":"Ring","amount":round(budget*.15)}]
        summary = f"{data['style']} jewelry ideas for {data['occasion']} within ₹{budget:,.0f}."

    platforms = PLATFORMS[planner]
    per = max(1, round(budget / max(1, len(names))))
    recs = []
    for i, name in enumerate(names[:8]):
        platform, base = platforms[i % len(platforms)]
        recs.append({
            "name": name,
            "estimated_price": per,
            "platform": platform,
            "url": base + name.replace(" ", "+"),
            "reason": "Budget-conscious suggestion for the requested category."
        })
    return {"summary":summary, "budget_allocation":allocation,
            "recommendations":recs}

def recommend(planner, data, image_path=None):
    fb = fallback(planner, data)
    if not configured():
        return fb

    prompts = {
        "home": f"""Return ONLY JSON with keys summary,budget_allocation,recommendations.
Home interior plan. Budget INR {data['budget']}; rooms {data['rooms']};
style {data['style']}; items {data['items']}; city {data['city']}.
Give 6-8 practical ideas. Each recommendation must have name, estimated_price,
platform, url, reason. Do not claim live inventory or exact current prices.""",
        "party": f"""Return ONLY JSON with keys summary,budget_allocation,recommendations.
Plan a {data['event_type']} for {data['guests']} guests, budget INR {data['budget']}.
Venue {data['venue']}; city {data['city']}; preferences {data['preferences']}.
Allocate budget across food, venue, decoration and entertainment. Give 6-8 ideas.
Do not claim live availability or exact current prices.""",
        "jewelry": f"""Return ONLY JSON with keys summary,budget_allocation,recommendations.
Recommend jewelry within INR {data['budget']} for {data['occasion']}.
Style {data['style']}; outfit color {data['outfit_color']}; preferences {data['preferences']}.
Use the supplied image if present. Give 6-8 ideas with name, estimated_price,
platform, url and reason. Do not claim live inventory or exact current prices."""
    }
    try:
        result = generate_json(prompts[planner], image_path)
        if isinstance(result, dict) and result.get("recommendations"):
            return result
    except Exception:
        pass
    return fb
