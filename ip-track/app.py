from flask import Flask, render_template, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_ipv4_info():
    """Fetch IPv4 address and related information from multiple sources"""
    results = []
    
    # Source 1: ipify.org + ipapi.co
    try:
        ipv4_response = requests.get('https://api.ipify.org?format=json', timeout=5)
        if ipv4_response.status_code == 200:
            ipv4_data = ipv4_response.json()
            ip = ipv4_data.get('ip')
            
            if ip and ':' not in ip:
                info_response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5)
                if info_response.status_code == 200:
                    data = info_response.json()
                    results.append({
                        'source': 'ipapi.co',
                        'ip': ip,
                        'version': 'IPv4',
                        'city': data.get('city'),
                        'region': data.get('region'),
                        'country': data.get('country_name'),
                        'country_code': data.get('country_code'),
                        'postal': data.get('postal'),
                        'latitude': data.get('latitude'),
                        'longitude': data.get('longitude'),
                        'timezone': data.get('timezone'),
                        'isp': data.get('org'),
                        'asn': data.get('asn'),
                        'continent': data.get('continent_code')
                    })
    except Exception as e:
        print(f"Error fetching from ipapi.co: {e}")
    
    # Source 2: ipinfo.io
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        if response.status_code == 200:
            data = response.json()
            ip = data.get('ip')
            
            if ip and ':' not in ip:
                loc = data.get('loc', '').split(',')
                results.append({
                    'source': 'ipinfo.io',
                    'ip': ip,
                    'version': 'IPv4',
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'country': data.get('country'),
                    'country_code': data.get('country'),
                    'postal': data.get('postal'),
                    'latitude': loc[0] if len(loc) > 0 else None,
                    'longitude': loc[1] if len(loc) > 1 else None,
                    'timezone': data.get('timezone'),
                    'isp': data.get('org'),
                    'asn': None,
                    'hostname': data.get('hostname')
                })
    except Exception as e:
        print(f"Error fetching from ipinfo.io: {e}")
    
    # Source 3: ip-api.com
    try:
        response = requests.get('http://ip-api.com/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                ip = data.get('query')
                
                if ip and ':' not in ip:
                    results.append({
                        'source': 'ip-api.com',
                        'ip': ip,
                        'version': 'IPv4',
                        'city': data.get('city'),
                        'region': data.get('regionName'),
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'postal': data.get('zip'),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'timezone': data.get('timezone'),
                        'isp': data.get('isp'),
                        'asn': data.get('as'),
                        'continent': None
                    })
    except Exception as e:
        print(f"Error fetching from ip-api.com: {e}")
    
    return results if results else None

def get_ipv6_info():
    """Fetch IPv6 address information from multiple sources"""
    results = []
    
    # Source 1: api64.ipify.org + ipapi.co
    try:
        response = requests.get('https://api64.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            data = response.json()
            ip = data.get('ip')
            
            if ip and ':' in ip:
                try:
                    info_response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5)
                    if info_response.status_code == 200:
                        info_data = info_response.json()
                        results.append({
                            'source': 'ipapi.co',
                            'ip': ip,
                            'version': 'IPv6',
                            'city': info_data.get('city'),
                            'region': info_data.get('region'),
                            'country': info_data.get('country_name'),
                            'country_code': info_data.get('country_code'),
                            'isp': info_data.get('org'),
                            'asn': info_data.get('asn')
                        })
                except Exception as e:
                    print(f"Error getting IPv6 details from ipapi.co: {e}")
                    results.append({
                        'source': 'api64.ipify.org',
                        'ip': ip,
                        'version': 'IPv6',
                        'note': 'Limited info available'
                    })
    except Exception as e:
        print(f"Error fetching IPv6: {e}")
    
    # Source 2: ipinfo.io (IPv6)
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        if response.status_code == 200:
            data = response.json()
            ip = data.get('ip')
            
            if ip and ':' in ip:
                results.append({
                    'source': 'ipinfo.io',
                    'ip': ip,
                    'version': 'IPv6',
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'country': data.get('country'),
                    'country_code': data.get('country'),
                    'isp': data.get('org'),
                    'hostname': data.get('hostname')
                })
    except Exception as e:
        print(f"Error fetching IPv6 from ipinfo.io: {e}")
    
    return results if results else None

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/ip-info')
def get_ip_info():
    """API endpoint to get both IPv4 and IPv6 information"""
    ipv4_data = get_ipv4_info()
    ipv6_data = get_ipv6_info()
    
    return jsonify({
        'ipv4': ipv4_data,
        'ipv6': ipv6_data
    })

@app.route('/api/ipv4')
def get_ipv4():
    """API endpoint for IPv4 only"""
    return jsonify(get_ipv4_info())

@app.route('/api/ipv6')
def get_ipv6():
    """API endpoint for IPv6 only"""
    return jsonify(get_ipv6_info())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)