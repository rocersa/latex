from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os

app = Flask(__name__)
CORS(app)

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    invoice = data.get('invoice')
    latex = data.get('latex')

    if not invoice or not latex:
        return jsonify({"error": "Invalid input"}), 400

    # Generate LaTeX source code
    latex_source = str(latex)

    # Use a secure temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        tex_file_path = os.path.join(tmpdirname, 'invoice.tex')
        pdf_file_path = os.path.join(tmpdirname, 'invoice.pdf')

        # Write LaTeX source to a file
        with open(tex_file_path, 'w') as f:
            f.write(latex_source)

        # Run pdflatex to generate PDF
        try:
            subprocess.run(['pdflatex', '-output-directory', tmpdirname, tex_file_path], check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": "PDF generation failed", "details": str(e)}), 500

        # Ensure the generated PDF file exists
        if not os.path.exists(pdf_file_path):
            return jsonify({"error": "PDF file not found"}), 500

        # Send the generated PDF file
        filename = f"invoice_{invoice['CustomerT']['FirstName']}_{invoice['CustomerT']['LastName']}.pdf"
        return send_file(pdf_file_path, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
