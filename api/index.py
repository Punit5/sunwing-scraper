from flask import Flask, jsonify
import requests
import datetime
from typing import List, Dict, Any
import os

app = Flask(__name__)

def get_offers_for_gateway(data: Dict[str, Any], gateway_code: str) -> List[Dict[str, Any]]:
    """Extract offers for a specific gateway from the Sunwing API response."""
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
        print(f"Error parsing JSON for {gateway_code}: {e}")
    return offers

def parse_date(d: str) -> datetime.datetime:
    """Parse date string into datetime object."""
    try:
        return datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return datetime.datetime.max

def fetch_sunwing_data() -> Dict[str, Any]:
    """Fetch data from Sunwing's API."""
    url = "https://www.sunwing.ca/page-data/en/promotion/packages/all-inclusive-vacation-packages/page-data.json"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from Sunwing: {e}")
        raise

def format_offers_for_web(offers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format offers for web display."""
    offers.sort(key=lambda x: (
        x.get("Destination", {}).get("Name", "ZZZ"),
        parse_date(x.get("DepartureDate", "9999-12-31T00:00:00"))
    ))
    
    formatted_offers = []
    for offer in offers:
        acc = offer.get("AccommodationInfo", {})
        formatted_offer = {
            "hotel": acc.get('AccommodationName', 'N/A'),
            "stars": acc.get('StarRating', 'N/A'),
            "destination": offer.get('Destination', {}).get('Name', 'N/A'),
            "country": offer.get('Destination', {}).get('CountryName', 'N/A'),
            "departure_date": offer.get('DepartureDate', 'N/A')[:10],
            "duration": offer.get('Duration', 'N/A'),
            "meal_plan": offer.get('MealPlan', 'N/A'),
            "price": offer.get('Price', 'N/A'),
            "reg_price": offer.get('RegPrice', 'N/A'),
            "tax": offer.get('tax', ''),
            "save_upto": offer.get('SaveUpto', 'N/A'),
            "deep_link": offer.get('DeepLink', 'N/A')
        }
        formatted_offers.append(formatted_offer)
    
    return formatted_offers

@app.route('/')
def index():
    """Serve the main page."""
    try:
        # Try to read from current directory first, then parent
        try:
            with open('index.html', 'r') as f:
                content = f.read()
        except FileNotFoundError:
            with open('../index.html', 'r') as f:
                content = f.read()
        
        return content, 200, {'Content-Type': 'text/html'}
    except Exception as e:
        return f"Error loading page: {str(e)}", 500

@app.route('/api/packages/<gateway>')
def get_packages(gateway):
    """API endpoint to get packages for a specific gateway."""
    gateway_names = {
        'YVR': 'Vancouver (YVR)',
        'YYZ': 'Toronto (YYZ)'
    }
    
    if gateway not in gateway_names:
        return jsonify({"error": f"Unknown gateway code '{gateway}'"}), 400
    
    try:
        data = fetch_sunwing_data()
        offers = get_offers_for_gateway(data, gateway)
        formatted_offers = format_offers_for_web(offers)
        
        return jsonify({
            "gateway": gateway,
            "gateway_name": gateway_names[gateway],
            "packages": formatted_offers,
            "count": len(formatted_offers),
            "generated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500