from flask import Flask, render_template, jsonify
import requests
import pycountry
from functools import lru_cache
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@lru_cache(maxsize=1)
def get_ip_info():
    """Fetch IP information with caching and error handling"""
    api_url = "https://ipinfo.io/json"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Resolve country name from country code
        country_code = data.get("country")
        country_name = country_code
        
        if country_code:
            try:
                country = pycountry.countries.get(alpha_2=country_code.upper())
                country_name = country.name if country else country_code
            except (KeyError, AttributeError):
                country_name = country_code

        # Determine IP version
        ip_address = data.get("ip", "")
        ip_version = "IPv6" if ":" in ip_address else "IPv4"

        ip_info = {
            "ip": ip_address,
            "version": ip_version,
            "city": data.get("city", "N/A"),
            "region": data.get("region", "N/A"),
            "country": country_name or "N/A",
            "country_code": country_code or "N/A",
            "isp": data.get("org", "N/A"),
            "location": data.get("loc"),
            "timezone": data.get("timezone", "N/A"),
            "postal": data.get("postal", "N/A")
        }
        
        return {"success": True, "data": ip_info}
    
    except requests.exceptions.Timeout:
        logging.error("Request timeout while fetching IP info")
        return {"success": False, "error": "Request timed out. Please try again."}
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching IP info: {str(e)}")
        return {"success": False, "error": f"Unable to fetch IP information: {str(e)}"}

@app.route("/")
def home():
    """Main route to display IP information"""
    result = get_ip_info()
    return render_template("index.html", result=result)

@app.route("/api/refresh")
def refresh():
    """API endpoint to refresh IP information"""
    get_ip_info.cache_clear()
    result = get_ip_info()
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)