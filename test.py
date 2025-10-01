import requests
import pycountry

def get_ip_info():
    # Using ipapi.co as an example public API
    api_url = "https://ipinfo.io/json/"
    
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        
        # Extract important info
        country_code = data.get("country")
        country_name = country_code
        if country_code:
            try:
                country = pycountry.countries.get(alpha_2=country_code.upper())
                country_name = country.name if country else country_code
            except:
                country_name = country_code

        ip_info = {
            "IPv4/IPv6 Address": data.get("ip"),
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
        print(f"Error retrieving IP info: {e}")
        return None

def display_ip_info(ip_info):
    if ip_info:
        print("\n📡 Public IP Address Information\n" + "-"*40)
        for key, value in ip_info.items():
            print(f"{key}: {value}")
    else:
        print("No IP information available.")

if __name__ == "__main__":
    ip_info = get_ip_info()
    display_ip_info(ip_info)
