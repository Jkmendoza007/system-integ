from flask import Flask, render_template
import requests
import pycountry

app = Flask(__name__)

def get_ip_info():
    api_url = "https://ipinfo.io/json"  # Using IPinfo public API
    
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Resolve country name
        country_code = data.get("country")
        country_name = country_code
        if country_code:
            try:
                country = pycountry.countries.get(alpha_2=country_code.upper())
                country_name = country.name if country else country_code
            except:
                country_name = country_code

        ip_info = {
            "IP Address": data.get("ip"),
            "Version": "IPv6" if ":" in data.get("ip", "") else "IPv4",
            "City": data.get("city"),
            "Region": data.get("region"),
            "Country": country_name,
            "Country Code": country_code,
            "ISP": data.get("org"),
            "ASN": data.get("asn")
        }
        return ip_info
    except requests.exceptions.RequestException as e:
        return {"Error": str(e)}

@app.route("/")
def home():
    ip_info = get_ip_info()
    return render_template("index.html", ip_info=ip_info)

if __name__ == "__main__":
    app.run(debug=True)
