#!/usr/bin/env python3

import sys
import os
from pathlib import Path

def check_venv():
    """Check if running in the virtual environment and provide helpful error message if not."""
    venv_python = Path(__file__).parent / "myvenv" / "bin" / "python"
    if not venv_python.exists():
        print("Error: Virtual environment not found. Please run the script using run_sunwing_deals.sh", file=sys.stderr)
        sys.exit(1)
    
    if sys.executable != str(venv_python):
        print("Error: Please run this script using run_sunwing_deals.sh", file=sys.stderr)
        print("This ensures the script runs with the correct Python environment and dependencies.", file=sys.stderr)
        sys.exit(1)

# Check virtual environment before importing other modules
check_venv()

import requests
import datetime
import argparse
from typing import List, Dict, Any

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
        print(f"Error parsing JSON for {gateway_code}: {e}", file=sys.stderr)
    return offers

def parse_date(d: str) -> datetime.datetime:
    """Parse date string into datetime object."""
    try:
        return datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return datetime.datetime.max

def html_escape(text: Any) -> str:
    """Escape HTML special characters."""
    import html
    return html.escape(str(text))

def export_html(offers: List[Dict[str, Any]], filename: str, gateway_name: str) -> None:
    """Export offers to an HTML file with proper formatting."""
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
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tr:hover {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>Sunwing All-Inclusive Packages from {gateway_name}</h1>
    <p>Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
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
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Successfully exported to {filename}")
    except Exception as e:
        print(f"Error writing to {filename}: {e}", file=sys.stderr)
        sys.exit(1)

def fetch_sunwing_data() -> Dict[str, Any]:
    """Fetch data from Sunwing's API."""
    url = "https://www.sunwing.ca/page-data/en/promotion/packages/all-inclusive-vacation-packages/page-data.json"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from Sunwing: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to handle command-line arguments and execute the script."""
    parser = argparse.ArgumentParser(description='Fetch and export Sunwing vacation packages.')
    parser.add_argument('--gateways', nargs='+', default=['YVR', 'YYZ'],
                      help='Gateway codes to fetch (default: YVR YYZ)')
    parser.add_argument('--output-dir', default='.',
                      help='Directory to save output files (default: current directory)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        try:
            os.makedirs(args.output_dir)
        except Exception as e:
            print(f"Error creating output directory: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Fetch data from Sunwing
    print("Fetching data from Sunwing...")
    data = fetch_sunwing_data()
    
    # Process each gateway
    gateway_names = {
        'YVR': 'Vancouver (YVR)',
        'YYZ': 'Toronto (YYZ)'
    }
    
    for gateway in args.gateways:
        if gateway not in gateway_names:
            print(f"Warning: Unknown gateway code '{gateway}', skipping...", file=sys.stderr)
            continue
            
        print(f"Processing {gateway_names[gateway]}...")
        offers = get_offers_for_gateway(data, gateway)
        if not offers:
            print(f"Warning: No offers found for {gateway}", file=sys.stderr)
            continue
            
        output_file = os.path.join(args.output_dir, f"sunwing_{gateway.lower()}_packages.html")
        export_html(offers, output_file, gateway_names[gateway])

if __name__ == "__main__":
    main() 