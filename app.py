from flask import Flask, render_template, jsonify, request, send_file
import requests
import pycountry
import logging
import csv
import io
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

@app.route("/export/csv")
def export_csv():
    """Export IP information as CSV"""
    ip_input = request.args.get("ip")
    ip = ip_input if ip_input else get_client_ip()
    result = get_ip_info(ip)
    if not result["success"]:
        return jsonify(result), 400

    data = result["data"]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Field", "Value"])
    for key, value in data.items():
        writer.writerow([key, value])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='ip_info.csv')

@app.route("/export/excel")
def export_excel():
    """Export IP information as Excel"""
    ip_input = request.args.get("ip")
    ip = ip_input if ip_input else get_client_ip()
    result = get_ip_info(ip)
    if not result["success"]:
        return jsonify(result), 400

    data = result["data"]
    wb = Workbook()
    ws = wb.active
    ws.title = "IP Information"
    ws.append(["Field", "Value"])
    for key, value in data.items():
        ws.append([key, value])
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='ip_info.xlsx')

@app.route("/export/pdf")
def export_pdf():
    """Export IP information as PDF"""
    ip_input = request.args.get("ip")
    ip = ip_input if ip_input else get_client_ip()
    result = get_ip_info(ip)
    if not result["success"]:
        return jsonify(result), 400

    data = result["data"]
    output = io.BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    c.drawString(100, 750, "IP Information Report")
    y = 720
    for key, value in data.items():
        c.drawString(100, y, f"{key}: {value}")
        y -= 20
    c.save()
    output.seek(0)
    return send_file(output, mimetype='application/pdf', as_attachment=True, download_name='ip_info.pdf')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
