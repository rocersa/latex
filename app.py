from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import datetime

app = Flask(__name__)
CORS(app)

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    invoice = data.get('invoice')
    totalPrice = data.get('totalPrice')
    latex = data.get('latex')
    print(latex)
    print(type(latex))
    if not invoice or not latex:
        return jsonify({"error": "Invalid input"}), 400
    
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
    latex_source = f"""
    \\documentclass[a4paper,12pt]{{article}}
    \\usepackage{{graphicx}}
    \\usepackage{{geometry}}
    \\geometry{{a4paper, margin=1cm}}
    \\usepackage{{array}}
    \\usepackage{{longtable}}
    \\usepackage{{lscape}} % Add landscape package for wide tables
    
    \\begin{{document}}
    
    \\begin{{center}}
        \\textbf{{\\Huge {{WWW.COR-TEN-STEEL.CO.UK}}}}
    \\end{{center}}
    
    \\vspace{{1cm}}
    
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedright
        \\small
        Cadley \\\\
        SN8 4NE \\\\
        Tel: 0118 234 9909 \\\\
        Email: uk@cor-ten-steel.co.uk \\\\
        \\vspace{{0.5cm}}
        \\textbf{{\\large Customer Details:}} \\\\
        Name: \\texttt{{{invoice['CustomerT']['FirstName']}}} \\texttt{{{invoice['CustomerT']['LastName']}}} \\\\
        Address: \\\\
        \\texttt{{{invoice['CustomerT']['AddressNumber']}}} \\texttt{{{invoice['CustomerT']['AddressStreet']}}} \\\\
        \\texttt{{{invoice['CustomerT']['AddressSuburb']}}} \\texttt{{{invoice['CustomerT']['AddressPostcode']}}} \\\\
        \\texttt{{{invoice['CustomerT']['AddressCity']}}} \\\\
        \\texttt{{{invoice['CustomerT']['AddressCountry']}}}
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedleft
        \\small
        Tax Invoice \\\\
        VAT Number: 161 6032 40 \\\\
        \\vspace{{1cm}}
        Invoice Number: \\texttt{{{str(invoice['InvoiceID']).zfill(5)}}} \\\\
        Date Issued: \\texttt{{{datetime.date.today().strftime("%Y-%m-%d")}}}
    \\end{{minipage}}
    
    \\vspace{{1cm}}
    
    \\begin{{longtable}}{{|p{{0.4\\textwidth}}|p{{0.1\\textwidth}}|p{{0.2\\textwidth}}|p{{0.2\\textwidth}}|}}
        \\hline
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total}} \\\\
        \\hline
        \\endfirsthead
        \\hline
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total}} \\\\
        \\hline
        \\endhead
        \\hline
        \\endfoot
        \\hline
        \\endlastfoot
        \\multicolumn{{2}}{{|c|}}{{}} & Subtotal & £\\texttt{{{totalPrice:.2f}}} \\\\
        \\hline
        \\multicolumn{{2}}{{|c|}}{{}} & VAT (20\\% Included) & £\\texttt{{{(0.2 * totalPrice):.2f}}} \\\\
        \\hline
        \\multicolumn{{2}}{{|c|}}{{}} & Freight & £\\texttt{{{invoice['freight_charged']:.2f}}} \\\\
        \\hline
        \\multicolumn{{2}}{{|c|}}{{}} & Total & £\\texttt{{{invoice['Price']:.2f}}} \\\\
    \\end{{longtable}}
    
    \\end{{document}}
    """
    return latex_source
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
