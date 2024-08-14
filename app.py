from flask import Flask, request, send_file
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    invoice = data['invoice']
    totalPrice = data['totalPrice']

    # Generate LaTeX source code
    latex_source = generate_latex_source(invoice, totalPrice)
    
    # Write LaTeX source to a file
    with open('invoice.tex', 'w') as f:
        f.write(latex_source)
    
    # Run pdflatex to generate PDF
    subprocess.run(['pdflatex', 'invoice.tex'], check=True)

    # Send the generated PDF file
    return send_file('invoice.pdf', as_attachment=True)

def generate_latex_source(invoice, totalPrice):
    # Generate LaTeX content here (similar to the LaTeX source in your Node.js example)
    latex_source = """
    \\documentclass[a4paper,12pt]{article}
    \\usepackage{graphicx}
    \\usepackage{geometry}
    \\geometry{a4paper, margin=1in}
    \\usepackage{array}
    \\usepackage{longtable}
    
    \\begin{document}
    \\begin{center}
        \\textbf{\\Huge {WWW.COR-TEN-STEEL.CO.UK}}
    \\end{center}
    
    \\vspace{1cm}
    
    % Add more LaTeX content here
    
    \\end{document}
    """
    return latex_source

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
