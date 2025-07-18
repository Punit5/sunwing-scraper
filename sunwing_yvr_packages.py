import requests
import datetime

url = "https://www.sunwing.ca/page-data/en/promotion/packages/all-inclusive-vacation-packages/page-data.json"

response = requests.get(url)
data = response.json()

def get_offers_for_gateway(data, gateway_code):
    offers = []
    try:
        rules = data["result"]["data"]["contentfulFluidLayout"]["pageSections"]["pageSections"]
        for section in rules:
            if "wrapperSections" in section and section["wrapperSections"]:
                for wrapper in section["wrapperSections"]["pageSections"]:
                    if wrapper.get("__typename") == "ContentfulPromotionRule":
                        for group in wrapper.get("merchandising", []):
                            gateway = group.get("Gateway", {})
                            if gateway.get("Code") == gateway_code:
                                for offer in group.get("PromotionGroups", []):
                                    for deal in offer.get("Offers", []):
                                        offers.append(deal)
    except Exception as e:
        print(f"[DEBUG] Error parsing JSON for {gateway_code}: {e}")
    return offers

def parse_date(d):
    try:
        return datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return datetime.datetime.max

def html_escape(text):
    import html
    return html.escape(str(text))

def export_html(offers, filename, gateway_name):
    # Sort by destination first, then by departure date (ascending)
    offers.sort(key=lambda x: (
        x.get("Destination", {}).get("Name", "ZZZ"),  # ZZZ as fallback to sort unknown destinations last
        parse_date(x.get("DepartureDate", "9999-12-31T00:00:00"))
    ))
    html_rows = []
    for offer in offers:
        acc = offer.get("AccommodationInfo", {})
        html_rows.append(f"<tr>"
            f"<td>{html_escape(acc.get('AccommodationName', 'N/A'))}</td>"
            f"<td>{html_escape(acc.get('StarRating', 'N/A'))}</td>"
            f"<td>{html_escape(offer.get('Destination', {}).get('Name', 'N/A'))}</td>"
            f"<td>{html_escape(offer.get('Destination', {}).get('CountryName', 'N/A'))}</td>"
            f"<td>{html_escape(offer.get('DepartureDate', 'N/A')[:10])}</td>"
            f"<td>{html_escape(offer.get('Duration', 'N/A'))}</td>"
            f"<td>{html_escape(offer.get('MealPlan', 'N/A'))}</td>"
            f"<td>${html_escape(offer.get('Price', 'N/A'))} (Reg: ${html_escape(offer.get('RegPrice', 'N/A'))}) {html_escape(offer.get('tax', ''))}</td>"
            f"<td>{html_escape(offer.get('SaveUpto', 'N/A'))}%</td>"
            f"<td><a href='{html_escape(offer.get('DeepLink', 'N/A'))}' target='_blank'>Book</a></td>"
            "</tr>")
    html_content = f"""
<html>
<head>
    <title>Sunwing {gateway_name} Packages</title>
    <style>
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background: #f0f0f0; }}
    </style>
</head>
<body>
    <h1>Sunwing All-Inclusive Packages from {gateway_name}</h1>
    <table>
        <tr>
            <th>Hotel</th>
            <th>Stars</th>
            <th>Destination</th>
            <th>Country</th>
            <th>Departure</th>
            <th>Duration</th>
            <th>Meal Plan</th>
            <th>Price</th>
            <th>Save Up To</th>
            <th>Link</th>
        </tr>
        {''.join(html_rows)}
    </table>
</body>
</html>
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Exported to {filename}")

# YVR (Vancouver)
yvr_offers = get_offers_for_gateway(data, "YVR")
export_html(yvr_offers, "sunwing_yvr_packages.html", "Vancouver (YVR)")

# YYZ (Toronto)
yyz_offers = get_offers_for_gateway(data, "YYZ")
export_html(yyz_offers, "sunwing_yyz_packages.html", "Toronto (YYZ)") 