from flask import Flask, render_template, jsonify, request
import requests
import pycountry
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_client_ip():
    """Get visitor IP, accounting for reverse proxies."""
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr

def get_ip_info(ip):
    """Fetch IP info from ipinfo.io for a given IP"""
    api_url = f"https://ipinfo.io/{ip}/json"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        country_code = data.get("country")
        country_name = country_code
        if country_code:
            country = pycountry.countries.get(alpha_2=country_code.upper())
            if country:
                country_name = country.name

        ip_version = "IPv6" if ":" in ip else "IPv4"

        ip_info = {
            "ip": ip,
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
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching IP info: {str(e)}")
        return {"success": False, "error": str(e)}

@app.route("/", methods=["GET"])
def home():
    """Show visitor IP or lookup another IP"""
    ip_input = request.args.get("ip")
    if ip_input:
        ip = ip_input.strip()
    else:
        ip = get_client_ip()

    result = get_ip_info(ip)
    return render_template("index.html", result=result, current_ip=ip_input or "")

@app.route("/api/refresh")
def refresh():
    """Refresh IP info"""
    ip_input = request.args.get("ip")
    ip = ip_input.strip() if ip_input else get_client_ip()
    result = get_ip_info(ip)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
