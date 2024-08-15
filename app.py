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
    \\pagestyle{{empty}}

    \\begin{{document}}
    
    \\begin{{center}}
        \\textbf{{\\Huge {{COR-TEN-STEEL UK}}}}
    \\end{{center}}
    
    \\vspace{{1cm}}
    \\noindent
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
    
    \\begin{{longtable}}{{|p{{0.4\\textwidth}}|>{{\\centering\\arraybackslash}}p{{0.1\\textwidth}}|p{{0.2\\textwidth}}|p{{0.2\\textwidth}}|}}
        \\hline
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total}} \\\\
        \\hline
        \\endhead
        {table_rows(invoice)}
        \\multicolumn{{2}}{{c|}}{{}} & Subtotal & £\\texttt{{{totalPrice:.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Freight & £\\texttt{{{invoice['freight_charged']:.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Balance due inc VAT & £\\texttt{{{invoice['Price']:.2f}}} \\\\
        \\cline{{3-4}}
        \\endfoot
    \\end{{longtable}}
    \\vspace{{1cm}}
    \\noindent
    Payment can be made by bank transfer to the following account:
    \\begin{{center}}
    \\texttt{{Account Name: Cor-Ten-Steel}} \\\\
    \\texttt{{Sort Code: 12-34-56}} \\\\
    \\texttt{{Account Number: 12345678}} \\\\
    \\texttt{{Reference: 00003}}
    \\end{{center}}
    
    \\end{{document}}
    """
    return latex_source

def table_rows(invoice):
    table_rows = ""
    for product in invoice["InvoiceComponentsT"]:
        table_rows += f"\\texttt{{{product['ProductsT']['NameMetric']}}} & \\texttt{{{product['Quantity']}}} & \\texttt{{£{product['ProductsT']['UKRetailCost']:.2f}}} & \\texttt{{£{(product['ProductsT']['UKRetailCost'] * product['Quantity']):.2f}}} \\\\ \n"
        table_rows += "\\hline \n"
    return table_rows


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
