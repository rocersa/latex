from flask import Flask, request, send_file, jsonify
from datetime import datetime
from flask_cors import CORS
import subprocess
import tempfile
import os
import pytz
import GenerateCuboid
from invoice_utils import generate_latex_invoice
from picklist_utils import generate_latex_picklist

app = Flask(__name__)
CORS(app)

@app.route("/generate-cuboid", methods=["POST"])
def generate_cuboid():
    success, filename = GenerateCuboid.run(100, 300, 200)
    if success:
        return send_file(filename, mimetype='image/png')
    else:
        return 'Failed to generate image', 500

@app.route("/generate-pdf-invoice", methods=["POST"])
def generate_pdf_invoice():
    data = request.json
    invoice = data.get("invoice")
    country = data.get("country")
    utc_now = datetime.now(pytz.utc)
    uk_time = utc_now.astimezone(pytz.timezone("Europe/London"))
    us_time = utc_now.astimezone(pytz.timezone("America/Los_Angeles"))
    nz_time = utc_now.astimezone(pytz.timezone("Pacific/Auckland"))
    au_time = utc_now.astimezone(pytz.timezone("Australia/Sydney"))
    # Generate LaTeX source code
    country = country.upper()
    if country == "UK":
        latex_source = generate_latex_invoice(invoice, uk_time, country, "£")
    elif country == "US":
        latex_source = generate_latex_invoice(invoice, us_time, country, "\\$")
    elif country == "NZ":
        latex_source = generate_latex_invoice(invoice, nz_time, country, "\\$")
    elif country == "AU":
        latex_source = generate_latex_invoice(invoice, au_time, country, "\\$")

    # Use a secure temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        tex_file_path = os.path.join(tmpdirname, "invoice.tex")
        pdf_file_path = os.path.join(tmpdirname, "invoice.pdf")

        # Write LaTeX source to a file
        with open(tex_file_path, "w") as f:
            f.write(latex_source)

        # Run pdflatex to generate PDF
        try:
            subprocess.run(
                ["pdflatex", "-output-directory", tmpdirname, tex_file_path], check=True
            )
        except subprocess.CalledProcessError as e:
            return jsonify({"error": "PDF generation failed", "details": e.stderr}), 500

        # Ensure the generated PDF file exists
        if not os.path.exists(pdf_file_path):
            return jsonify({"error": "PDF file not found"}), 500

        # Send the generated PDF file
        return send_file(pdf_file_path, as_attachment=True)


@app.route("/generate-pdf-picklist", methods=["POST"])
def generate_pdf_picklist():
    data = request.json
    invoice = data.get("invoice")
    info = data.get("info")
    components = data.get("components")
    country = data.get("country")
    utc_now = datetime.now(pytz.utc)
    uk_time = utc_now.astimezone(pytz.timezone("Europe/London"))
    us_time = utc_now.astimezone(pytz.timezone("America/Los_Angeles"))
    nz_time = utc_now.astimezone(pytz.timezone("Pacific/Auckland"))
    au_time = utc_now.astimezone(pytz.timezone("Australia/Sydney"))
    # Generate LaTeX source code
    country = country.upper()
    if country == "UK":
        latex_source = generate_latex_picklist(
            invoice, info, components, uk_time, country
        )
    elif country == "US":
        latex_source = generate_latex_picklist(
            invoice, info, components, us_time, country
        )
    elif country == "NZ":
        latex_source = generate_latex_picklist(
            invoice, info, components, nz_time, country
        )
    elif country == "AU":
        latex_source = generate_latex_picklist(
            invoice, info, components, au_time, country
        )

    # Use a secure temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        tex_file_path = os.path.join(tmpdirname, "picklist.tex")
        pdf_file_path = os.path.join(tmpdirname, "picklist.pdf")

        # Write LaTeX source to a file
        with open(tex_file_path, "w") as f:
            f.write(latex_source)
        # Run pdflatex to generate PDF
        try:
            subprocess.run(
                ["pdflatex", "-output-directory", tmpdirname, tex_file_path], check=True
            )
        except subprocess.CalledProcessError as e:
            return jsonify({"error": "PDF generation failed", "details": e.stderr}), 500

        # Ensure the generated PDF file exists
        if not os.path.exists(pdf_file_path):
            return jsonify({"error": "PDF file not found"}), 500

        # Send the generated PDF file
        return send_file(pdf_file_path, as_attachment=True)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
